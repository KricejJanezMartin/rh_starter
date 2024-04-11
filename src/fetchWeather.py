import os
import pandas as pd
from retry_requests import retry
from datetime import datetime, timedelta
import logging
import mysql.connector
import requests
from datetime import datetime, timedelta
import logging
import pandas as pd
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import requests
import json
from datetime import datetime, timedelta

# Calculate the start and end dates
end_date = datetime.now().date()
start_date = end_date - timedelta(days=14)

url = "https://archive-api.open-meteo.com/v1/archive"

# Define the parameters
params = {
    "latitude": 46.5547,
    "longitude": 15.6467,
    "start_date": start_date.strftime("%Y-%m-%d"),
    "end_date": end_date.strftime("%Y-%m-%d"),
    "hourly": "temperature_2m,relative_humidity_2m,rain,snowfall"
}

# Generate the full URL
full_url = f"{url}?latitude={params['latitude']}&longitude={params['longitude']}&start_date={params['start_date']}&end_date={params['end_date']}&hourly={params['hourly']}"

# Send a GET request to the URL
response = requests.get(full_url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    responses = json.loads(response.text)

    # Print the JSON response
   # print(json.dumps(responses))
else:
    print(f"Request failed with status code {response.status_code}")

logging.info("Data fetched succesfully ")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = responses['hourly']
hourly_temperature_2m = hourly['temperature_2m']
hourly_relative_humidity_2m = hourly['relative_humidity_2m']
hourly_rain = hourly['rain']
hourly_snowfall = hourly['snowfall']

hourly_data = {
    "date": pd.to_datetime(hourly['time'], utc=True),
    "temperature_2m": hourly_temperature_2m,
    "relative_humidity_2m": hourly_relative_humidity_2m,
    "rain": hourly_rain,
    "snowfall": hourly_snowfall
}

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Drop rows with NaN values
hourly_dataframe = hourly_dataframe.dropna()

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

# Check if the table exists
cursor.execute("SHOW TABLES LIKE 'hourly_weather_data'")
result = cursor.fetchone()

# If the table doesn't exist, create it
if not result:
    create_table_query = """
    CREATE TABLE hourly_weather_data (
        timestamp TIMESTAMP,
        temperature_2m FLOAT,
        relative_humidity_2m FLOAT,
        rain FLOAT,
        snowfall FLOAT
    )
    """
    cursor.execute(create_table_query)

# Assuming your DataFrame is named df
for index, row in hourly_dataframe.iterrows():
    # Convert the date to a string format that MySQL can understand
    date_str = row["date"].strftime("%Y-%m-%d %H:%M:%S")

    # Insert the data into the database
    insert_query = "INSERT INTO hourly_weather_data (timestamp, temperature_2m, relative_humidity_2m, rain, snowfall) VALUES (%s, %s, %s, %s, %s)"
    values = (date_str, row["temperature_2m"], row["relative_humidity_2m"], row["rain"], row["snowfall"])
    cursor.execute(insert_query, values)

logging.info("Inserted data into database")

# Commit the transaction
db.commit()

logging.info("Checkpoint 5: After committing the transaction")

# Close the connection
db.close()

logging.info("Checkpoint 6: After closing the connection")