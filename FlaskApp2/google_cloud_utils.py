from google.cloud import bigquery
from google.cloud import texttospeech
from datetime import datetime, timedelta
import pandas as pd

def insert_data_to_bigquery(client, data):
    """Inserts weather data into BigQuery."""
    fields = ', '.join(data.keys())
    values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()])
    query = f"""
    INSERT INTO `lab-test-1-415115.weather_IoT_data.weather-records` ({fields})
    VALUES ({values})
    """
    query_job = client.query(query)
    query_job.result()  # Wait for the query job to complete

# Function to query the latest data from BigQuery
def query_latest_data(client, project_id, dataset_id, table_id):
    query = f"""
        SELECT *
        FROM `{project_id}.{dataset_id}.{table_id}`
        ORDER BY date DESC, time DESC
        LIMIT 25
    """
    query_job = client.query(query)
    df = query_job.to_dataframe()
    
    # Convert the date column to string and time column to string in the desired format before concatenation
    df['date'] = df['date'].astype(str)
    df['time'] = df['time'].astype(str)
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])

    # Sort DataFrame by datetime
    df = df.sort_values(by='datetime')
    

    return df

def query_latest_weather(client):
    """Fetches the latest weather data from BigQuery."""
    query = """
    SELECT outdoor_temp, outdoor_humidity, outdoor_weather
    FROM `lab-test-1-415115.weather_IoT_data.weather-records`
    ORDER BY date desc, time desc limit 1
    """
    query_job = client.query(query)
    results = query_job.result()
    row = next(iter(results), None)  # Get the first result if available
    if row:
        return {
            "outdoor_temp": row.outdoor_temp,
            "outdoor_humidity": row.outdoor_humidity,
            "outdoor_weather": row.outdoor_weather
        }
    else:
        raise Exception("No data available")
