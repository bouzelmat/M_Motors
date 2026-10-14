locals {
  rds_is_production = terraform.workspace == "production"
  rds_identifier    = "${var.project_name}-db-${terraform.workspace}"
}

resource "aws_db_subnet_group" "postgres" {
  name       = "${local.common_name}-db"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "${local.common_name}-db-subnets"
  }
}

resource "aws_security_group" "rds" {
  name        = "${local.common_name}-rds"
  description = "PostgreSQL access only from ECS Express Mode tasks"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL from ECS Express Mode tasks"
    protocol        = "tcp"
    from_port       = 5432
    to_port         = 5432
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    description = "Allow outbound database traffic"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "random_password" "database" {
  length  = 40
  special = false
}

resource "aws_secretsmanager_secret" "database_password" {
  name                    = "${var.project_name}/db-password-${terraform.workspace}"
  description             = "RDS password for ${local.common_name}; managed by Terraform"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "database_password" {
  secret_id     = aws_secretsmanager_secret.database_password.id
  secret_string = random_password.database.result
}

resource "aws_db_instance" "postgres" {
  identifier = local.rds_identifier

  engine         = "postgres"
  engine_version = "16"
  instance_class = local.rds_is_production ? "db.t4g.medium" : "db.t4g.micro"

  allocated_storage     = local.rds_is_production ? 30 : 20
  max_allocated_storage = local.rds_is_production ? 100 : 50
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.database_name
  username = var.database_username
  password = random_password.database.result
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  multi_az                = local.rds_is_production
  backup_retention_period = 3
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"
  copy_tags_to_snapshot   = true

  deletion_protection       = local.rds_is_production
  skip_final_snapshot       = !local.rds_is_production
  final_snapshot_identifier = local.rds_is_production ? "${local.rds_identifier}-final" : null

  apply_immediately               = false
  auto_minor_version_upgrade      = true
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  depends_on = [aws_secretsmanager_secret_version.database_password]
}
