# 1. Bucket S3 dédié aux documents justificatifs
resource "aws_s3_bucket" "dossier_documents" {
  bucket = "m-motors-documents"

  tags = {
    Name        = "M-Motors Dossier Documents"
    Environment = var.environment
  }
}

# 2. Block Public Access (Obligatoire - Accès privé uniquement)
resource "aws_s3_bucket_public_access_block" "dossier_documents_privacy" {
  bucket = aws_s3_bucket.dossier_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 3. Chiffrement côté serveur (SSE-S3)
resource "aws_s3_bucket_server_side_encryption_configuration" "dossier_documents_encryption" {
  bucket = aws_s3_bucket.dossier_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4. Politique imposant TLS + refus explicite de s3:GetObject aux non-autorisés
resource "aws_s3_bucket_policy" "enforce_tls_and_deny_public" {
  bucket = aws_s3_bucket.dossier_documents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Refus des requêtes non-TLS
      {
        Sid       = "EnforceTLSRequestsOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.dossier_documents.arn,
          "${aws_s3_bucket.dossier_documents.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      # Refus explicite de s3:GetObject aux principaux non autorisés
      {
        Sid       = "DenyPublicGetObject"
        Effect    = "Deny"
        Principal = {
          AWS = "*"
          Federated = "*"
        }
        Action = "s3:GetObject"
        Resource = "${aws_s3_bucket.dossier_documents.arn}/*"
        Condition = {
          StringNotEquals = {
            "aws:PrincipalArn" = var.allowed_iam_roles
          }
        }
      }
    ]
  })
}

# 5. Désactivation explicite du website hosting (déjà couvert par public_access_block)
resource "aws_s3_bucket_website_configuration" "disable_website" {
  bucket = aws_s3_bucket.dossier_documents.id
  # La simple absence de configuration désactive le website hosting
}