# infra/terraform/s3.tf

# 1. Définition du bucket S3
resource "aws_s3_bucket" "vehicle_photos" {
  bucket = "m-motors-photos"

  tags = {
    Name        = "M-Motors Vehicle Photos"
    Environment = var.environment
  }
}

# 2. Blocage strict de tout accès public (Obligatoire pour la sécurité)
resource "aws_s3_bucket_public_access_block" "vehicle_photos_privacy" {
  bucket = aws_s3_bucket.vehicle_photos.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 3. Configuration CORS pour autoriser l'upload direct (POST) depuis le web/mobile
resource "aws_s3_bucket_cors_configuration" "vehicle_photos_cors" {
  bucket = aws_s3_bucket.vehicle_photos.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["POST"]
    allowed_origins = ["https://app.m-motors.com", "http://localhost:3000"]
    max_age_seconds = 3000
  }
}