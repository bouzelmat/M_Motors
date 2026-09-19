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

# 3. Chiffrement côté serveur (SSE-S3 par défaut ou KMS)
resource "aws_s3_bucket_server_side_encryption_configuration" "dossier_documents_encryption" {
  bucket = aws_s3_bucket.dossier_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4. Politique imposant l'usage de TLS (HTTPS obligatoire)
resource "aws_s3_bucket_policy" "enforce_tls" {
  bucket = aws_s3_bucket.dossier_documents.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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
      }
    ]
  })
}