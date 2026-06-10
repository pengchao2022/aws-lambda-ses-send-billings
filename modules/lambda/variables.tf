variable "schedule_expression" {
  type = string
  description = "EventBridge call expression using standard cron format"
  default = "cron(0/2 * * * ? *)"     # run every 2 minutes

  # other cron format e.g.
  # cron(0 9 ? * MON *)       every monday at 9:00 AM
  # cron(0 * * * ? *)         every hour on the hour 每小时整点
  # cron(0 8 ? * MON-FRI *)   Monday to Friday at 8 AM
  
}

variable "sender_email" {
  type = string
  description = "The email address of the sender"
  
}

variable "recipient_email" {
  type = string
  description = "The email address of the receiver"
  
}

variable "function_name" {
  type = string
  description = "The name of Lambda function"
  
}

variable "zip_path" {
  type        = string
  description = "the path of ZIP file (will compress lambda_function.py to ZIP package)"
}