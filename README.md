# Weather Dashboard

This Weather Dashboard project fetches real-time weather data for a city using the WeatherAPI, processes it, and stores it in an Amazon S3 bucket. The application is designed to automate the pipeline of fetching, processing, and saving weather data, making it ideal for monitoring weather conditions or building weather-related applications.

## Features
- Fetch real-time weather data using WeatherAPI.
- Process and structure the weather data for better readability and usability.
- Save processed weather data to an AWS S3 bucket in JSON format.
- Automatically create an S3 bucket if it does not exist.
- Supports environment variable configuration for flexibility and security.

## Requirements
- Python 3.8 or later
- AWS account with access to S3
- WeatherAPI account and API key

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/weather-dashboard.git
cd weather-dashboard
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root directory and configure the following variables:
```env
WEATHERAPI_KEY=your_weatherapi_key
AWS_BUCKET_NAME=your_s3_bucket_name
CITY=your_default_city
```
- `WEATHERAPI_KEY`: Your WeatherAPI API key.
- `AWS_BUCKET_NAME`: Name of the S3 bucket where data will be stored.
- `CITY`: (Optional) Default city to fetch weather data for (e.g., London).

### 5. Configure AWS Credentials
Ensure your AWS credentials are properly configured to allow access to the S3 bucket.

```bash
aws configure
```
Provide the Access Key ID, Secret Access Key, and Default Region for the IAM user or role.

### 6. Bash Script to Automate Environment Setup
You can automate the environment setup using the following bash script:
```bash
#!/bin/bash

# Clone the repository
echo "Cloning the repository..."
git clone https://github.com/your-repo/weather-dashboard.git
cd weather-dashboard || exit

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Prompt for environment variables
echo "Configuring environment variables..."
read -p "Enter your WeatherAPI Key: " WEATHERAPI_KEY
read -p "Enter your AWS S3 Bucket Name: " AWS_BUCKET_NAME
read -p "Enter your default city (optional): " CITY
CITY=${CITY:-London}

# Create .env file
echo "Creating .env file..."
cat <<EOT >> .env
WEATHERAPI_KEY=$WEATHERAPI_KEY
AWS_BUCKET_NAME=$AWS_BUCKET_NAME
CITY=$CITY
EOT

# Confirm setup
echo "Environment setup complete."
```

Make the script executable and run it:
```bash
chmod +x setup_environment.sh
./setup_environment.sh
```

## Usage
Run the script using the following command:
```bash
python src/weather_dashboard.py
```

The script performs the following steps:
1. Sets up the S3 bucket.
2. Fetches real-time weather data for the specified city.
3. Processes the weather data into a structured format.
4. Saves the processed data to the S3 bucket.

### Example Output
```bash
Setting up S3 bucket...
Bucket already exists: weather-dashboard-unique-id
Fetching weather data...
Processing weather data...
Saving data to S3...
Data saved to S3 bucket weather-dashboard-unique-id with file name weather_data_20250116123045.json
Weather data pipeline completed successfully.
```

## Project Structure
```
weather-dashboard/
├── src/
│   ├── weather_dashboard.py  # Main script
├── tests/
│   ├── test_weather_dashboard.py  # Test script
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
├── README.md                 # Project documentation
├── .github/
│   └── workflows/
│       └── weather-dashboard-automation.yml    # GitHub Actions workflow
```

## Dependencies
- `boto3`: AWS SDK for Python to interact with S3.
- `requests`: HTTP library to fetch weather data from WeatherAPI.
- `python-dotenv`: Load environment variables from a `.env` file.
- `pytest`: Testing framework for Python.

Install these dependencies using:
```bash
pip install -r requirements.txt
```

## Testing
Tests for the Weather Dashboard project are located in the `tests/` directory. The tests validate the functionality of the key components, including:
- Fetching weather data.
- Processing weather data.
- Interacting with the S3 bucket.

### Running Tests
Run the following command to execute the tests:
```bash
pytest tests/
```

### Example Test File
Create a test file `tests/test_weather_dashboard.py` with the following content:
```python
import pytest
from src.weather_dashboard import WeatherDashboard
from unittest.mock import patch, MagicMock

@patch("boto3.client")
def test_create_bucket(mock_boto3_client):
    mock_s3 = MagicMock()
    mock_boto3_client.return_value = mock_s3

    dashboard = WeatherDashboard()
    dashboard.bucket_name = "test-bucket"

    # Simulate bucket creation
    mock_s3.create_bucket.return_value = {}

    dashboard.create_bucket()
    mock_s3.create_bucket.assert_called_with(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
    )

def test_process_weather_data():
    raw_data = {
        "location": {"name": "London", "region": "", "country": "UK"},
        "current": {"temp_c": 15.0, "condition": {"text": "Sunny"}, "humidity": 50, "wind_kph": 10.0}
    }

    dashboard = WeatherDashboard()
    processed_data = dashboard.process_weather_data(raw_data)

    assert processed_data == {
        "city": "London",
        "region": "",
        "country": "UK",
        "temperature": 15.0,
        "condition": "Sunny",
        "humidity": 50,
        "wind_kph": 10.0,
        "timestamp": pytest.approx(processed_data["timestamp"])
    }
```

## GitHub Actions Workflow
Automate testing and deployment with GitHub Actions. Create the workflow file `.github/workflows/weather-dashboard-automation.yml` with the following content:

```yaml
name: Weather Dashboard Automation

on:
  workflow_dispatch: # Manual trigger
  schedule:
    - cron: "0 12 * * *" # Daily at 12:00 PM UTC

jobs:
  weather_dashboard_job:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/

      - name: Run Weather Dashboard
        env:
          OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_BUCKET_NAME: ${{ secrets.AWS_BUCKET_NAME }}
          CITY: ${{ secrets.CITY }}
        run: |
          python src/weather_dashboard.py
```

## Terraform Setup
You can manage the S3 resources using Terraform. Below is the Terraform configuration to create the required S3 bucket:

```hcl
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
```

Apply the Terraform configuration using:
```bash
terraform init
terraform apply
```

## Environment Variables
- **`WEATHERAPI_KEY`**: Required for accessing WeatherAPI.
- **`AWS_BUCKET_NAME`**: Name of the S3 bucket where the data will be stored.
- **`CITY`**: Optional default city to fetch weather data for.

## Error Handling
- Handles bucket creation errors, such as bucket already existing or ownership conflicts.
- Handles errors when fetching data from WeatherAPI (e.g., network issues or invalid API key).
- Logs errors encountered while saving data to S3, including access permission issues.

## How It Works
1. **Create S3 Bucket**: The script checks if the S3 bucket exists. If not, it creates the bucket in the specified AWS region.
2. **Fetch Weather Data**: Real-time weather data is retrieved from WeatherAPI based on the specified city.
3. **Process Weather Data**: The raw weather data is structured into a JSON format with key details like temperature, condition, humidity, and wind speed.
4. **Save to S3**: The processed data is saved to the S3 bucket with a timestamped file name.

## AWS Setup
### S3 Bucket Policy
Ensure the S3 bucket has the correct permissions. Here is an example bucket policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_USER"
      },
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

### IAM Policy
Attach the following IAM policy to your user or role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

## Future Enhancements
- Add support for multiple cities.
- Schedule weather data fetch using a task scheduler (e.g., `cron` or `Celery`).
- Add support for more weather APIs.
- Implement comprehensive test cases for all modules.
- Introduce a web-based UI for managing cities and viewing weather data.
- Add support for database storage (e.g., DynamoDB or PostgreSQL).

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Feel free to contribute to this project by submitting pull requests or reporting issues!
