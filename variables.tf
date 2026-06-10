variable "region" {
  description = "the Region of AWS resouces deployed"
  type        = string
  default     = "us-east-1"
}

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
  default = "pengchao.ma6@gmail.com"
  
}

variable "recipient_email" {
  type = string
  description = "The email address of the receiver"
  default = "prometheus_0521@qq.com"
  
}

variable "function_name" {
  type = string
  description = "The name of Lambda function"
  default = "lambda-ses-function"
  
}