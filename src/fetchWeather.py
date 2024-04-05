import openmeteo_requests
import os
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime, timedelta
import logging
import mysql.connector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
# Calculate the start and end dates
end_date = datetime.now().date()
start_date = end_date - timedelta(days=14)

params = {
    "latitude": 46.5547,
    "longitude": 15.6467,
    "start_date": start_date.strftime("%Y-%m-%d"),
    "end_date": end_date.strftime("%Y-%m-%d"),
    "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "snowfall"]
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

logging.info("Data fetched succesfully ")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_rain = hourly.Variables(2).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(3).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["rain"] = hourly_rain
hourly_data["snowfall"] = hourly_snowfall

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

logging.info("Starting DB write")

# Create a connection to the database
db = mysql.connector.connect(
  host=os.getenv("DB_HOST"),  # replace with your MySQL container's IP
  user=os.getenv("DB_USER"),
  password=os.getenv("DB_PASSWORD"),
  database=os.getenv("DB_NAME")
)


logging.info("Connected to database")


cursor = db.cursor()

# Assuming your hourly_data dictionary looks like this:
# hourly_data = {"temperature_2m": 20, "relative_humidity_2m": 50, "rain": 10, "snowfall": 0}

# Insert the data into the database
insert_query = "INSERT INTO yourtable (temperature_2m, relative_humidity_2m, rain, snowfall) VALUES (%s, %s, %s, %s)"
values = (hourly_data["temperature_2m"], hourly_data["relative_humidity_2m"], hourly_data["rain"], hourly_data["snowfall"])
cursor.execute(insert_query, values)

logging.info("Inserted data into database")

# Commit the transaction
db.commit()

logging.info("Checkpoint 5: After committing the transaction")

# Close the connection
db.close()

logging.info("Checkpoint 6: After closing the connection")