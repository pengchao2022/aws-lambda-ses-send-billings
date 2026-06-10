module "ses" {
  source        = "./modules/ses"
  sender_identity_email = "pengchao.ma6@gmail.com"
}

module "lambda" {
  source          = "./modules/lambda"
  function_name   = "lambda-ses-function"
  sender_email    = "pengchao.ma6@gmail.com"
  recipient_email = "prometheus_0521@qq.com"
  schedule_expression = "cron(0/2 * * * ? *)"
  zip_path            = "${path.root}/lambda_payload.zip"
}