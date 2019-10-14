provider "aws" {
  region = var.aws_region
}

locals {
  kubeconfig = <<KUBECONFIG

apiVersion: v1
clusters:
- cluster:
    server: ${aws_eks_cluster.translation-api.endpoint}
    certificate-authority-data: ${aws_eks_cluster.translation-api.certificate_authority.0.data}
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: aws
  name: aws
current-context: aws
kind: Config
preferences: {}
users:
- name: aws
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "${var.cluster_name}"
KUBECONFIG

  config_map_aws_auth = <<CONFIGMAPAWSAUTH


apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: ${aws_iam_role.translation-api-node.arn}
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
CONFIGMAPAWSAUTH

    translation-api-node-userdata = <<USERDATA
#!/bin/bash
set -o xtrace
/etc/eks/bootstrap.sh --apiserver-endpoint '${aws_eks_cluster.translation-api.endpoint}' --b64-cluster-ca '${aws_eks_cluster.translation-api.certificate_authority.0.data}' '${var.cluster_name}'
USERDATA
}


data "aws_availability_zones" "available" {}

resource "aws_vpc" "translation-api-vpc" {
  cidr_block = "10.0.0.0/16"

  tags = map(
     "Name", "translation-api-node",
     "kubernetes.io/cluster/${var.cluster_name}", "shared",
    )
}

resource "aws_subnet" "translation-api-subnet" {
  count = 2

  availability_zone = data.aws_availability_zones.available.names[count.index]
  cidr_block        = "10.0.${count.index}.0/24"
  vpc_id            = aws_vpc.translation-api-vpc.id

  tags = map(
     "Name", "translation-api-node",
     "kubernetes.io/cluster/${var.cluster_name}", "shared",
    )
}

resource "aws_internet_gateway" "translation-api-igw" {
  vpc_id = aws_vpc.translation-api-vpc.id

  tags = {
    Name = "translation-api-node"
  }
}

resource "aws_route_table" "translation-api-rt" {
  vpc_id = aws_vpc.translation-api-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.translation-api-igw.id
  }
}

resource "aws_route_table_association" "translation-api" {
  count = 2

  subnet_id      = aws_subnet.translation-api-subnet.*.id[count.index]
  route_table_id = aws_route_table.translation-api-rt.id
}

resource "aws_iam_role" "translation-api-cluster-role" {

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "translation-api-cluster-AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.translation-api-cluster-role.name
}

resource "aws_iam_role_policy_attachment" "translation-api-cluster-AmazonEKSServicePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.translation-api-cluster-role.name
}

resource "aws_security_group" "translation-api-cluster-sgp-cluster" {
  description = "Cluster communication with worker nodes"
  vpc_id      = aws_vpc.translation-api-vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "translation-api-node"
  }
}

resource "aws_eks_cluster" "translation-api" {
  name            = var.cluster_name
  role_arn        = aws_iam_role.translation-api-cluster-role.arn

  vpc_config {
    security_group_ids = [
      aws_security_group.translation-api-cluster-sgp-cluster.id]
    subnet_ids         = aws_subnet.translation-api-subnet.*.id
  }

  depends_on = [
    "aws_iam_role_policy_attachment.translation-api-cluster-AmazonEKSClusterPolicy",
    "aws_iam_role_policy_attachment.translation-api-cluster-AmazonEKSServicePolicy",
  ]
}

resource "aws_iam_role" "translation-api-node" {

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "translation-api-node-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.translation-api-node.name
}

resource "aws_iam_role_policy_attachment" "translation-api-node-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.translation-api-node.name
}

resource "aws_iam_role_policy_attachment" "translation-api-node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.translation-api-node.name
}

resource "aws_iam_instance_profile" "translation-api-node" {
  role = aws_iam_role.translation-api-node.name
}

resource "aws_security_group" "translation-api-cluster-sgp-node" {
  description = "Security group for all nodes in the cluster"
  vpc_id      = aws_vpc.translation-api-vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = map(
     "Name", "translation-api-node",
     "kubernetes.io/cluster/${var.cluster_name}", "owned",
    )
}

resource "aws_security_group_rule" "translation-api-node-ingress-self" {
  description              = "Allow node to communicate with each other"
  from_port                = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.translation-api-cluster-sgp-node.id
  source_security_group_id = aws_security_group.translation-api-cluster-sgp-node.id
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "translation-api-node-ingress-cluster" {
  description              = "Allow worker Kubelets and pods to receive communication from the cluster control plane"
  from_port                = 1025
  protocol                 = "tcp"
  security_group_id        = aws_security_group.translation-api-cluster-sgp-node.id
  source_security_group_id = aws_security_group.translation-api-cluster-sgp-cluster.id
  to_port                  = 65535
  type                     = "ingress"
}

resource "aws_security_group_rule" "translation-api-cluster-ingress-node-https" {
  description              = "Allow pods to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.translation-api-cluster-sgp-cluster.id
  source_security_group_id = aws_security_group.translation-api-cluster-sgp-node.id
  to_port                  = 443
  type                     = "ingress"
}

data "aws_ami" "eks-worker" {
  filter {
    name   = "name"
    values = ["amazon-eks-node-${aws_eks_cluster.translation-api.version}-v*"]
  }

  most_recent = true
  owners      = ["602401143452"] # Amazon EKS AMI Account ID
}

resource "aws_launch_configuration" "translation-api-launch-configuration" {
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.translation-api-node.name
  image_id                    = data.aws_ami.eks-worker.id
  instance_type               = var.worker_type
  name_prefix                 = "translation-api"
  spot_price                  = var.worker_spot_price
  security_groups             = [aws_security_group.translation-api-cluster-sgp-node.id]
  user_data_base64            = base64encode(local.translation-api-node-userdata)

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "translation-api-autoscaling-group" {
  desired_capacity     = var.worker_cluster_desired_capacity
  launch_configuration = aws_launch_configuration.translation-api-launch-configuration.id
  max_size             = var.worker_cluster_max_size
  min_size             = var.worker_cluster_min_size
  vpc_zone_identifier  = aws_subnet.translation-api-subnet.*.id

  tag {
    key                 = "Name"
    value               = "translation-api"
    propagate_at_launch = true
  }

  tag {
    key                 = "kubernetes.io/cluster/${var.cluster_name}"
    value               = "owned"
    propagate_at_launch = true
  }
}