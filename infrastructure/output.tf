output "config_map_aws_auth" {
  value = module.eks-translation-api.config_map_aws_auth
}

output "worker_iam_role_arn" {
  value = module.eks-translation-api.worker_iam_role_arn
}