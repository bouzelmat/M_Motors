# =============================================================================
# ÉTAPE 4 : Bucket S3 pour legacy.db + Rôle IAM dédié (lecture seule)
# =============================================================================

resource "random_string" "migration_bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# -----------------------------------------------------------------------------
# 2. Bucket S3 dédié à la migration (chiffré + accès public bloqué)
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "legacy_migration" {
  bucket = "${var.project_name}-staging-legacy-${random_string.migration_bucket_suffix.result}"

  tags = {
    Environment = "staging"
    Purpose     = "legacy-migration-us603"
    Project     = var.project_name
  }
}

# Blocage explicite de l'accès public (redondant avec les paramètres compte, mais explicite)
resource "aws_s3_bucket_public_access_block" "legacy_migration" {
  bucket = aws_s3_bucket.legacy_migration.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Chiffrement AES-256 au repos
resource "aws_s3_bucket_server_side_encryption_configuration" "legacy_migration" {
  bucket = aws_s3_bucket.legacy_migration.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # Pas besoin de KMS pour ce cas d'usage
    }
  }
}

# -----------------------------------------------------------------------------
# 3. Rôle IAM DÉDIÉ pour l'ETL (isolation totale)
# -----------------------------------------------------------------------------
resource "aws_iam_role" "etl_migration" {
  name = "${var.project_name}-staging-etl-migration" # Ex: "m-motors-staging-etl-migration"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" } # Pour ECS Express
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Environment = "staging"
    Purpose     = "ETL Legacy Migration Read-Only"
  }
}

# -----------------------------------------------------------------------------
# 4. Politique IAM : ACCÈS LECTURE SEULE sur le bucket legacy
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "etl_legacy_readonly" {
  name = "${var.project_name}-staging-etl-legacy-readonly"
  role = aws_iam_role.etl_migration.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowListBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.legacy_migration.arn]
      },
      {
        Sid      = "AllowGetObject"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = ["${aws_s3_bucket.legacy_migration.arn}/*"]
      }
      # ❌ AUCUNE action PutObject/DeleteObject/DeleteBucket autorisée
    ]
  })
}

# -----------------------------------------------------------------------------
# 5. Sortie : ARN du rôle ETL (pour référence dans ECS ou CI/CD)
# -----------------------------------------------------------------------------
output "etl_migration_role_arn" {
  description = "ARN du rôle IAM dédié à l'ETL de migration (lecture seule sur legacy.db)"
  value       = aws_iam_role.etl_migration.arn
}

output "legacy_migration_bucket_name" {
  description = "Nom du bucket S3 pour legacy.db"
  value       = aws_s3_bucket.legacy_migration.bucket
}

output "legacy_migration_bucket_arn" {
  description = "ARN du bucket S3 pour legacy.db"
  value       = aws_s3_bucket.legacy_migration.arn
}