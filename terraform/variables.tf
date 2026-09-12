variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Target AWS deployment region."
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment namespace."
}

variable "instance_type" {
  type        = string
  default     = "t3.small"
  description = "AWS EC2 instance type."
}

variable "public_key_data" {
  type        = string
  description = "Public SSH key content generated dynamically by CI/CD pipeline."
}