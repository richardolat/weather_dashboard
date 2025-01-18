import os
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

class WeatherDashboard:
    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY")
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")
        # Explicitly set the region name to avoid endpoint mismatches
        self.s3_client = boto3.client('s3', region_name="us-west-2")

    def create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.s3_client.meta.region_name == "us-east-1":
                # us-east-1 doesn't require LocationConstraint
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name
                )
            else:
                # Other regions require LocationConstraint
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.s3_client.meta.region_name
                    }
                )
            print(f"Created bucket: {self.bucket_name}")
        except self.s3_client.exceptions.BucketAlreadyExists:
            print(f"Bucket already exists: {self.bucket_name}")
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            print(f"Bucket already owned by you: {self.bucket_name}")
        except ClientError as e:
            print(f"Error creating bucket: {e}")

    def fetch_weather(self, city):
        """Fetch weather data from WeatherAPI"""
        base_url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": self.api_key,
            "q": city
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

    def process_weather_data(self, raw_data):
        """Process raw weather data into structured format"""
        if not raw_data:
            return None
        processed_data = {
            "city": raw_data.get("location", {}).get("name"),
            "region": raw_data.get("location", {}).get("region"),
            "country": raw_data.get("location", {}).get("country"),
            "temperature": raw_data.get("current", {}).get("temp_c"),
            "condition": raw_data.get("current", {}).get("condition", {}).get("text"),
            "humidity": raw_data.get("current", {}).get("humidity"),
            "wind_kph": raw_data.get("current", {}).get("wind_kph"),
            "timestamp": datetime.now().isoformat()
        }
        return processed_data

    def save_to_s3(self, data, file_name):
        """Save processed data to S3 bucket"""
        if not data:
            print("No data to save")
            return
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            print(f"Data saved to S3 bucket {self.bucket_name} with file name {file_name}")
        except ClientError as e:
            print(f"Error saving to S3: {e}")

if __name__ == "__main__":
    dashboard = WeatherDashboard()
    # Step 1: Create the S3 bucket
    print("Setting up S3 bucket...")
    dashboard.create_bucket()
    # Step 2: Fetch weather data
    print("Fetching weather data...")
    city = os.getenv("CITY", "London")  # Default city is London if not set
    raw_data = dashboard.fetch_weather(city)
    # Step 3: Process the data
    print("Processing weather data...")
    processed_data = dashboard.process_weather_data(raw_data)
    # Step 4: Save data to S3
    print("Saving data to S3...")
    file_name = f"weather_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    dashboard.save_to_s3(processed_data, file_name)
    print("Weather data pipeline completed successfully.")
