resource "aws_ses_email_identity" "identity" {
  email = var.sender_identity_email
}