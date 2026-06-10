# iam role
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



# cloudWatch log group
resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 7
}

# lambda function
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


# create policy for send_email and aws cost explorer
resource "aws_iam_policy" "lambda_combined_policy" {
  name = "lambda_ses_ce_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["ses:SendEmail", "ses:SendRawEmail"],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action   = ["ce:GetCostAndUsage"],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

# attach the policy to lambda role
resource "aws_iam_role_policy_attachment" "attach_combined_policy" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_combined_policy.arn
}


