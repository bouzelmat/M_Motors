output "environment" {
  value = terraform.workspace
}

output "ecr_repository_url" {
  value = aws_ecr_repository.backend.repository_url
}

output "ecs_express_service_arn" {
  value = aws_ecs_express_gateway_service.backend.service_arn
}

output "ecs_express_service_url" {
  value = one([
    for path in aws_ecs_express_gateway_service.backend.ingress_paths : path.endpoint
    if path.access_type == "PUBLIC"
  ])
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "frontend_cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.frontend.id
}

output "frontend_cloudfront_domain_name" {
  value = aws_cloudfront_distribution.frontend.domain_name
}

output "photos_bucket_name" {
  value = aws_s3_bucket.vehicle_photos.bucket
}

output "documents_bucket_name" {
  value = aws_s3_bucket.dossier_documents.bucket
}

output "database_password_secret_arn" {
  value     = aws_secretsmanager_secret.database_password.arn
  sensitive = true
}

output "monitoring_log_group_name" {
  value = aws_cloudwatch_log_group.backend.name
}

output "monitoring_sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "monitoring_error_alarm_name" {
  value = aws_cloudwatch_metric_alarm.backend_errors.alarm_name
}
