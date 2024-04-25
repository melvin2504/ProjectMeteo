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
OPENWEATHER_URL = "https://api.openweathermap.org/data/3.0/weather"


def get_outdoor_weather(city):
    """Fetch outdoor temperature and humidity data from OpenWeather API for a given city."""
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }
    response = requests.get(OPENWEATHER_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "outdoor_temp": data['main']['temp'],
            "outdoor_humidity": data['main']['humidity']
        }
    else:
        raise Exception("Failed to fetch weather data")

# get the column names of the db
# PROJECT_ID.DATASET_ID.weather-records
q = """
SELECT * FROM `lab-test-1-415115.weather_IoT_data.weather-records` LIMIT 10
"""
query_job = client.query(q)
df = query_job.to_dataframe()

@app.route('/send-to-bigquery', methods=['GET', 'POST'])
def send_to_bigquery():
    if request.method == 'POST':
        if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
            raise Exception("Incorrect Password!")
        data = request.get_json(force=True)["values"]

        
        weather_data = get_outdoor_weather("Lausanne")
        data.update(weather_data)

        
        q = """INSERT INTO `lab-test-1-415115.weather_IoT_data.weather-records` 
        """
        names = """"""
        values = """"""
        for k, v in data.items():
            names += f"""{k},"""
            if df.dtypes[k] == float:
                values += f"""{v},"""
            else:
                # string values in the query should be in single qutation!
                values += f"""'{v}',"""
        # remove the last comma
        names = names[:-1]
        values = values[:-1]
        q = q + f""" ({names})""" + f""" VALUES({values})"""
        query_job = client.query(q)
        return {"status": "sucess", "data": data}
    return {"status": "failed"}
        

# For exercise 3: Complete the following endpoint.
# @app.route('/get_outdoor_weather', methods=['GET', 'POST'])
# def get_outdoor_weather():
#     if request.method == 'POST':
#         if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
#             raise Exception("Incorrect Password!")
#         # get the latest outdoor temp values from the db


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



