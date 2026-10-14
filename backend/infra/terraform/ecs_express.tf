resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}/backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.common_name}/backend"
  retention_in_days = 7
}

resource "aws_iam_role" "ecs_execution" {
  name = "${local.common_name}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_managed" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${local.common_name}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["secretsmanager:GetSecretValue"]
      Resource = [
        aws_secretsmanager_secret.database_password.arn,
        aws_secretsmanager_secret.application_key.arn
      ]
    }]
  })
}

resource "aws_iam_role" "ecs_infrastructure" {
  name = "${local.common_name}-ecs-infrastructure"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# CORRECTION 1 : Politique en ligne pour contourner le blocage 404 de la politique gérée
resource "aws_iam_role_policy" "ecs_infrastructure_inline" {
  name = "${local.common_name}-ecs-infra-policy"
  role = aws_iam_role.ecs_infrastructure.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticloadbalancing:*",
          "ec2:CreateSecurityGroup",
          "ec2:DeleteSecurityGroup",
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          "application-autoscaling:*",
          "iam:CreateServiceLinkedRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "ecs_task" {
  name = "${local.common_name}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "ecs_task" {
  name = "${local.common_name}-ecs-task-access"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ]
      Resource = [
        aws_s3_bucket.vehicle_photos.arn,
        "${aws_s3_bucket.vehicle_photos.arn}/*",
        aws_s3_bucket.dossier_documents.arn,
        "${aws_s3_bucket.dossier_documents.arn}/*"
      ]
    }]
  })
}

resource "aws_ecs_express_gateway_service" "backend" {
  service_name            = "${local.common_name}-backend"
  execution_role_arn      = aws_iam_role.ecs_execution.arn
  infrastructure_role_arn = aws_iam_role.ecs_infrastructure.arn
  task_role_arn           = aws_iam_role.ecs_task.arn
  cpu                     = local.ecs_is_production ? "1024" : "256"
  memory                  = local.ecs_is_production ? "2048" : "512"
  health_check_path       = "/health"
  wait_for_steady_state   = true

  network_configuration {
    subnets         = local.ecs_subnets
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  primary_container {
    image          = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
    container_port = 8000

    aws_logs_configuration {
      log_group         = aws_cloudwatch_log_group.backend.name
      log_stream_prefix = "backend"
    }

    environment {
      name  = "APP_NAME"
      value = "M-Motors API"
    }
    environment {
      name  = "ENVIRONMENT"
      value = terraform.workspace
    }
    environment {
      name  = "AWS_REGION"
      value = var.aws_region
    }
    environment {
      name  = "DB_HOST"
      value = aws_db_instance.postgres.address
    }
    environment {
      name  = "DB_NAME"
      value = var.database_name
    }
    environment {
      name  = "DB_USER"
      value = var.database_username
    }
    environment {
      name  = "S3_BUCKET_NAME"
      value = aws_s3_bucket.vehicle_photos.bucket
    }
    environment {
      name  = "S3_DOCUMENTS_BUCKET_NAME"
      value = aws_s3_bucket.dossier_documents.bucket
    }
    environment {
      name  = "CORS_ALLOWED_ORIGINS"
      value = jsonencode(concat(var.allowed_cors_origins, ["https://${aws_cloudfront_distribution.frontend.domain_name}"]))
    }

    secret {
      name       = "DB_PASSWORD"
      value_from = aws_secretsmanager_secret.database_password.arn
    }
    secret {
      name       = "SECRET_KEY"
      value_from = aws_secretsmanager_secret.application_key.arn
    }
  }

  scaling_target {
    auto_scaling_metric       = "AVERAGE_CPU"
    auto_scaling_target_value = 60
    min_task_count            = 1
    max_task_count            = local.ecs_is_production ? 3 : 1
  }

  # CORRECTION 2 : Le depends_on pointe maintenant vers la politique en ligne (inline)
  depends_on = [
    aws_iam_role_policy_attachment.ecs_execution_managed,
    aws_iam_role_policy.ecs_execution_secrets,
    aws_iam_role_policy.ecs_infrastructure_inline, # <-- C'est ici que la modification a été faite
    aws_iam_role_policy.ecs_task,
    aws_db_instance.postgres,
    aws_secretsmanager_secret_version.database_password,
    aws_secretsmanager_secret_version.application_key
  ]
}

resource "random_password" "application_key" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret" "application_key" {
  name                    = "${var.project_name}/application-key-${terraform.workspace}"
  description             = "JWT signing key for ${local.common_name}"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "application_key" {
  secret_id     = aws_secretsmanager_secret.application_key.id
  secret_string = random_password.application_key.result
}