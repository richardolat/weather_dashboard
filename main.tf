provider "aws" {
  region = "us-west-2" # Change this to your desired region
}

# Create the S3 Bucket
resource "aws_s3_bucket" "weather_bucket" {
  bucket = "weather-dashboard-unique-id" # Replace with a globally unique name

  tags = {
    Name        = "WeatherDashboardBucket"
    Environment = "Production"
  }
}

# Enable Versioning
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.weather_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Add Bucket Policy
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.weather_bucket.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          AWS = "${aws_iam_role.weather_app_role.arn}" # Dynamically reference the IAM role ARN
        },
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = [
          "arn:aws:s3:::weather-dashboard-unique-id",
          "arn:aws:s3:::weather-dashboard-unique-id/*"
        ]
      }
    ]
  })
}

# Create IAM Role for the Weather App
resource "aws_iam_role" "weather_app_role" {
  name = "weather-app-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com" # Replace with the service using this role
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach S3 Access Policy to the IAM Role
resource "aws_iam_policy" "s3_access_policy" {
  name        = "S3AccessPolicy"
  description = "Policy to allow S3 access for weather-dashboard"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = [
          "arn:aws:s3:::weather-dashboard-unique-id",
          "arn:aws:s3:::weather-dashboard-unique-id/*"
        ]
      }
    ]
  })
}

# Attach Policy to the Role
resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.weather_app_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# Outputs
output "bucket_name" {
  value = aws_s3_bucket.weather_bucket.id
}

output "iam_role_arn" {
  value = aws_iam_role.weather_app_role.arn
}
