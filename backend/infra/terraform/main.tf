terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # BACKEND DISTANT S3 : Indispensable pour que GitHub Actions se "souvienne" de l'état
  backend "s3" {
    bucket  = "m-motors-terraform-state-bucket" # Remplacez par le nom exact de votre bucket créé manuellement
    key     = "staging/terraform.tfstate"
    region  = "eu-west-3"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = terraform.workspace
      ManagedBy   = "Terraform"
    }
  }
}

locals {
  environment       = terraform.workspace
  name_suffix       = terraform.workspace
  common_name       = "${var.project_name}-${local.name_suffix}"
  ecs_is_production = terraform.workspace == "production"
  ecs_subnets       = slice(data.aws_subnets.default.ids, 0, min(3, length(data.aws_subnets.default.ids)))
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${local.common_name}-ecs-tasks"
  description = "Egress security group for ECS Express Mode tasks"
  vpc_id      = data.aws_vpc.default.id

  egress {
    description = "Allow outbound application traffic"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_budgets_budget" "monthly" {
  count = var.budget_alert_email == null ? 0 : 1

  name         = "${local.common_name}-monthly"
  budget_type  = "COST"
  limit_amount = "5"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.budget_alert_email]
  }
}