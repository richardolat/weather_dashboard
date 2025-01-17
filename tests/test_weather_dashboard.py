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

    assert processed_data["city"] == "London"
    assert processed_data["temperature"] == 15.0
    assert processed_data["condition"] == "Sunny"
