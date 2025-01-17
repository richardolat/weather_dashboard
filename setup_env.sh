#!/bin/bash

# Prompt the user for input
echo "Welcome to the .env setup script!"
read -p "Enter your OpenWeather API Key: " openweather_api_key
read -p "Enter your AWS Bucket Name: " aws_bucket_name
read -p "Enter your default city (e.g., London): " city

# Create the .env file
cat <<EOL > src/.env
OPENWEATHER_API_KEY=$openweather_api_key
AWS_BUCKET_NAME=$aws_bucket_name
CITY=$city
EOL

# Confirmation message
echo ".env file has been successfully created in the src directory!"
