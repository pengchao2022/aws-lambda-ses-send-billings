output "verified_email" {
  description = "The email address that has been verified in Amazon SES"
  value       = aws_ses_email_identity.identity.email
  sensitive   = false
}

