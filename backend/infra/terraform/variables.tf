variable "project_name" {
  description = "Prefixe de nommage du projet."
  type        = string
  default     = "m-motors"
}

variable "aws_region" {
  description = "Région AWS cible."
  type        = string
  default     = "eu-west-3"
}

variable "image_tag" {
  description = "Tag immuable de l’image backend publiée dans ECR."
  type        = string
  default     = "latest"
}

variable "database_name" {
  description = "Nom de la base PostgreSQL."
  type        = string
  default     = "m_motors"
}

variable "database_username" {
  description = "Utilisateur maître RDS."
  type        = string
  default     = "m_motors"
}

variable "budget_alert_email" {
  description = "Adresse de notification du budget AWS. Laisser null pour ne pas créer le budget."
  type        = string
  default     = null
  nullable    = true
}

variable "frontend_allowed_origins" {
  description = "Origines autorisées par CORS pour les uploads directs vers S3."
  type        = list(string)
  default     = ["*"]
}

variable "frontend_build_api_base_url" {
  description = "Valeur VITE_API_BASE_URL utilisée au build frontend."
  type        = string
  default     = "/"
}

variable "allowed_cors_origins" {
  description = "Origines CORS exposées par l’API."
  type        = list(string)
  default     = []
}

variable "monitoring_alert_email" {
  description = "Adresse e-mail qui reçoit les alertes CloudWatch via SNS. La confirmation se fait via le lien reçu par e-mail."
  type        = string
  default     = "omarbouzelmat99@gmail.com"
}
