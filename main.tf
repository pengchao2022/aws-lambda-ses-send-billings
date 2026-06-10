module "ses" {
  source        = "./modules/ses"
  sender_identity_email = "pengchao.ma6@gmail.com"
}

module "lambda" {
  source          = "./modules/lambda"
  function_name   = "my-automation-lambda"
  sender_email    = module.ses.verified_email
  recipient_email = "prometheus_0521@qq.com"
  schedule_expression = var.schedule_expression
  zip_path            = "${path.root}/lambda_payload.zip"
}