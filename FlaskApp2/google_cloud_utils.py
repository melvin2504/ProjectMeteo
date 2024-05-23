from google.cloud import bigquery
from google.cloud import texttospeech
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response

import pandas as pd

def insert_data_to_bigquery(client, data):
        # Prepare the query to insert data into BigQuery
    fields = ', '.join(data.keys())
    values = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()])
    
    query = f"""
    INSERT INTO `lab-test-1-415115.weather_IoT_data.weather-records` ({fields})
    VALUES ({values})
    """
    try:
        query_job = client.query(query)
        query_job.result()  # Wait for the query job to complete
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

def fetch_hourly_max_for_last_7_days(client):
    query = """
    SELECT 
        DATETIME_TRUNC(DATETIME(date, time), HOUR) as hour, 
        MAX(outdoor_temp) as max_outdoor_temp, 
        MAX(outdoor_humidity) as max_outdoor_humidity
    FROM `lab-test-1-415115.weather_IoT_data.weather-records`
    WHERE DATETIME(date, time) >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 7 DAY)
    GROUP BY hour
    ORDER BY hour DESC
    """
    query_job = client.query(query)
    results = query_job.result()
    hourly_data = []
    for row in results:
        hourly_data.append({
            "hour": row.hour,
            "max_outdoor_temp": row.max_outdoor_temp,
            "max_outdoor_humidity": row.max_outdoor_humidity
        })
    return hourly_data

def fetch_min_avg_max(client):
    query = """
    SELECT
      TIMESTAMP(DATETIME(date, time)) AS datetime,
      indoor_temp
    FROM
      `lab-test-1-415115.weather_IoT_data.weather-records`
    WHERE
      date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    ORDER BY
      datetime
    """
    query_job = client.query(query)
    df = query_job.to_dataframe()

    # Ensure datetime is in the correct format and set as index
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    # Resample the dataframe to 3-hour bins and calculate max, min, and mean temperatures
    resampled_df = df['indoor_temp'].resample('3H').agg(['max', 'min', 'mean']).fillna(0)

    # Format the result as a dictionary
    result = {
        'datetime': resampled_df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'max_temp': resampled_df['max'].tolist(),
        'min_temp': resampled_df['min'].tolist(),
        'avg_temp': resampled_df['mean'].tolist(),
    }
    return result

def fetch_min_avg_max_outdoor(client):
    query = """
    SELECT
      TIMESTAMP(DATETIME(date, time)) AS datetime,
      outdoor_temp
    FROM
      `lab-test-1-415115.weather_IoT_data.weather-records`
    WHERE
      date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    ORDER BY
      datetime
    """
    query_job = client.query(query)
    df = query_job.to_dataframe()

    # Ensure datetime is in the correct format and set as index
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    # Resample the dataframe to 3-hour bins and calculate max, min, and mean temperatures
    resampled_df = df['outdoor_temp'].resample('3H').agg(['max', 'min', 'mean']).fillna(0)

    # Format the result as a dictionary
    result = {
        'datetime': resampled_df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'max_temp': resampled_df['max'].tolist(),
        'min_temp': resampled_df['min'].tolist(),
        'avg_temp': resampled_df['mean'].tolist(),
    }
    return result
