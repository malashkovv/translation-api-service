provider "aws" {
  region = var.aws_region
}

module "vpc-translation-api" {
  source               = "terraform-aws-modules/vpc/aws"
  version              = "2.6.0"
  name                 = "${var.cluster_name}-vpc"
  cidr                 = "10.0.0.0/16"
  azs                  = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  public_subnets       = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  enable_dns_hostnames = true

  tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

resource "aws_iam_role_policy_attachment" "worker-policy-attachment-AWSXRayDaemonWriteAccess" {
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
  role       = module.eks-translation-api.worker_iam_role_name
}

module "eks-translation-api" {
  source                      = "terraform-aws-modules/eks/aws"
  cluster_name                = var.cluster_name
  subnets                     = module.vpc-translation-api.public_subnets
  vpc_id                      = module.vpc-translation-api.vpc_id
  manage_aws_auth             = true

  worker_groups = [
    {
      name                  = "spot"
      instance_type         = var.worker_type
      root_volume_size      = 20
      spot_price            = var.worker_spot_price
      asg_max_size          = var.worker_cluster_max_size
      asg_desired_capacity  = var.worker_cluster_desired_capacity
      autoscaling_enabled   = true
      kubelet_extra_args    = "--node-labels=kubernetes.io/lifecycle=spot"
      suspended_processes   = ["AZRebalance"]
      public_ip             = true
      tags = [{
        key                 = "type"
        value               = "spot"
        propagate_at_launch = true
      }]
    }
  ]

  tags = {
    environment = "stage"
  }
}
