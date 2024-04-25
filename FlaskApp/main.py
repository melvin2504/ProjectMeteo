from flask import Flask, request
import os
from google.cloud import bigquery
import requests
from datetime import datetime

# You only need to uncomment the line below if you want to run your flask app locally.
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
client = bigquery.Client(project="lab-test-1-415115")


# For authentication

YOUR_HASH_PASSWD = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab" # YOUR_HAS_PASSWD

app = Flask(__name__)

OPENWEATHER_API_KEY = "6b85e31b08c576ddd0a8f6a60e5afc01"


def get_weather(api_key, city):
    """Fetches the current weather for a specified city using OpenWeatherMap's API."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        data = response.json()  # Convert the response to JSON
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        return temperature, humidity, description
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# get the column names of the db
# PROJECT_ID.DATASET_ID.weather-records
q = """
SELECT * FROM `lab-test-1-415115.weather_IoT_data.weather-records` LIMIT 10
"""
query_job = client.query(q)
df = query_job.to_dataframe()

@app.route('/send-to-bigquery', methods=['POST'])
def send_to_bigquery():
    # Check for correct password in the POST request
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401

    # Fetch the weather data
    city = "Lausanne"
    weather_data = get_weather(OPENWEATHER_API_KEY, city)
    if weather_data is None:
        return jsonify({"error": "Failed to fetch weather data"}), 500

    # Extracting the weather data
    temperature, humidity, description = weather_data
    data = request.get_json(force=True)["values"]
    data.update({
        "outdoor_temp": temperature,
        "outdoor_humidity": humidity,
        "outdoor_weather": description
    })

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
        

@app.route('/get_outdoor_weather', methods=['POST'])
def get_outdoor_weather():
    # Verify password from the request
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    
    # Query to select the latest outdoor temperature, humidity, and description records
    query = """
    SELECT outdoor_temp, outdoor_humidity
    FROM `lab-test-1-415115.weather_IoT_data.weather-records`
    ORDER BY timestamp DESC
    LIMIT 1
    """
    try:
        query_job = client.query(query)  # Execute the query
        results = query_job.result()  # Wait for results

        # Extract data from query results
        row = next(iter(results), None)  # Get the first result if available
        if row:
            return jsonify({
                "outdoor_temp": row.outdoor_temp,
                "outdoor_humidity": row.outdoor_humidity
            })
        else:
            return jsonify({"error": "No data available"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



