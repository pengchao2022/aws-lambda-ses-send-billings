# 1. IAM Role & Logs
resource "aws_iam_role" "iam_for_lambda" {
  name = "${var.function_name}_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" } }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "ses_send" {
  role = aws_iam_role.iam_for_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = ["ses:SendEmail", "ses:SendRawEmail"], Effect = "Allow", Resource = "*" }]
  })
}

# 2. CloudWatch Log Group
resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 7
}

# 3. Lambda Function
resource "aws_lambda_function" "func" {
  filename      = "lambda_payload.zip"
  function_name = var.function_name
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  source_code_hash = filebase64sha256(var.zip_path) # let terraform can know the code change

  environment {
    variables = {
      SENDER    = var.sender_email
      RECIPIENT = var.recipient_email
    }
  }
}

# create iam role for scheduler
resource "aws_iam_role" "scheduler_role" {
  name = "${var.function_name}_scheduler_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "scheduler.amazonaws.com" } }]
  })
}

# let schedule can invoke lambda 
resource "aws_iam_role_policy" "scheduler_invoke_lambda" {
  role = aws_iam_role.scheduler_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = "lambda:InvokeFunction"
      Effect   = "Allow"
      Resource = aws_lambda_function.func.arn
    }]
  })
}

# create schedule
resource "aws_scheduler_schedule" "this" {
  name       = "${var.function_name}_trigger"
  schedule_expression = var.schedule_expression

  flexible_time_window { mode = "OFF" }

  target {
    arn      = aws_lambda_function.func.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}