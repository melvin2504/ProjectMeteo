from flask import Flask, request, jsonify, Response
import os
from google.cloud import bigquery
from google.cloud import texttospeech
import requests
from datetime import datetime
from openai import OpenAI
import pandas as pd

# You only need to uncomment the line below if you want to run your flask app locally.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./lab-test-1-415115-c2f0b755d8b4.json"

# Initialize the OpenAI client
clientAI = OpenAI(
    api_key="sk-proj-ewEynB9LGERMFCdacv2lT3BlbkFJj8xC95U78WlMP1ZZ9Aiu",
)

client = bigquery.Client(project="lab-test-1-415115")
# Google Text-to-Speech client initialization
tts_client = texttospeech.TextToSpeechClient()

# For authentication

YOUR_HASH_PASSWD = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab" # YOUR_HAS_PASSWD

app = Flask(__name__)

OPENWEATHER_API_KEY = "6b85e31b08c576ddd0a8f6a60e5afc01"

weather_icons = {
    'thunderstorm with light rain': '11d',
    'thunderstorm with rain': '11d',
    'thunderstorm with heavy rain': '11d',
    'light thunderstorm': '11d',
    'thunderstorm': '11d',
    'heavy thunderstorm': '11d',
    'ragged thunderstorm': '11d',
    'thunderstorm with light drizzle': '11d',
    'thunderstorm with drizzle': '11d',
    'thunderstorm with heavy drizzle': '11d',
    'light intensity drizzle': '09d',
    'drizzle': '09d',
    'heavy intensity drizzle': '09d',
    'light intensity drizzle rain': '09d',
    'drizzle rain': '09d',
    'heavy intensity drizzle rain': '09d',
    'shower rain and drizzle': '09d',
    'heavy shower rain and drizzle': '09d',
    'shower drizzle': '09d',
    'light rain': '10d',
    'moderate rain': '10d',
    'heavy intensity rain': '10d',
    'very heavy rain': '10d',
    'extreme rain': '10d',
    'freezing rain': '13d',
    'light intensity shower rain': '09d',
    'shower rain': '09d',
    'heavy intensity shower rain': '09d',
    'ragged shower rain': '09d',
    'light snow': '13d',
    'snow': '13d',
    'heavy snow': '13d',
    'sleet': '13d',
    'light shower sleet': '13d',
    'shower sleet': '13d',
    'light rain and snow': '13d',
    'rain and snow': '13d',
    'light shower snow': '13d',
    'shower snow': '13d',
    'heavy shower snow': '13d',
    'mist': '50d',
    'smoke': '50d',
    'haze': '50d',
    'sand/dust whirls': '50d',
    'fog': '50d',
    'sand': '50d',
    'dust': '50d',
    'volcanic ash': '50d',
    'squalls': '50d',
    'tornado': '50d',
    'clear sky': '01d',  
    'few clouds': '02d',  
    'scattered clouds': '03d',  
    'broken clouds': '04d',  
    'overcast clouds': '04d'  
}

#OUTILsss 

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

def fetch_hourly_max_for_last_7_days():
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

def fetch_min_avg_max():
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

def fetch_min_avg_max_outdoor():
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

@app.route('/')
def index():
    return "Welcome to the Weather App!"

@app.route('/get-latest-indoor', methods=['GET'])
def get_latest_indoor():
    query = """
    SELECT indoor_temp, indoor_humidity, indoor_tvoc, indoor_eco2
    FROM `lab-test-1-415115.weather_IoT_data.weather-records`
    ORDER BY time DESC
    LIMIT 1
    """
    try:
        query_job = client.query(query)
        results = query_job.result()  # Wait for the job to complete.

        for row in results:
            indoor_data = {
                "indoor_temp": row.indoor_temp,
                "indoor_humidity": row.indoor_humidity,
                "indoor_tvoc": row.indoor_tvoc,
                "indoor_eco2": row.indoor_eco2
            }
            return jsonify(indoor_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route('/hourly-max', methods=['POST'])
def get_hourly_max():
    data = fetch_hourly_max_for_last_7_days()
    return jsonify(data)

def generate_weather_advice(outdoor_temp, outdoor_weather):
    """
    Generate weather advice using GPT-3.5 based on the provided temperature and weather conditions.
    """
    prompt = (
        f"Today, the weather is {outdoor_weather} with a temperature of {outdoor_temp}°C. "
        "Tell how much degrees it is and the outside weather. Give some advice before going outside."
    )

    chat_completion = clientAI.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo",
        max_tokens=100,
        temperature=0.7
    )

    advice = chat_completion.choices[0].message.content.strip()
    return advice


@app.route('/generate_advice_audio', methods=['POST'])
def generate_advice_audio():
    weather_data = request.get_json(force=True)
    temperature = weather_data.get('outdoor_temp')
    description = weather_data.get('outdoor_weather').lower()

    # Generate the base message with current weather description and temperature
    message = generate_weather_advice(temperature, description)

    # Setup the synthesis input with the generated message
    synthesis_input = texttospeech.SynthesisInput(text=message)
    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US', ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    # Perform the text-to-speech request
    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Return the audio content as a WAV file in the HTTP response
    return Response(response.audio_content, mimetype='audio/wav')


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
    if request.get_json(force=True)["password"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    
    # Query to select the latest outdoor temperature, humidity, and description records
    query = """
    SELECT outdoor_temp, outdoor_humidity, outdoor_weather
    FROM `lab-test-1-415115.weather_IoT_data.weather-records`
    ORDER BY date desc, time desc limit 1
    """
    try:
        query_job = client.query(query)  # Execute the query
        results = query_job.result()  # Wait for results



        # Extract data from query results
        row = next(iter(results), None)  # Get the first result if available
        if row:
            icon_code = weather_icons.get(row.outdoor_weather, '01d')  # Get icon code, use 'default' if not found
            return jsonify({
                "outdoor_temp": row.outdoor_temp,
                "outdoor_humidity": row.outdoor_humidity,
                "outdoor_weather": row.outdoor_weather,
                "icon_code": icon_code  # Include the icon code in the response
            })
        else:
            return jsonify({"error": "No data available"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    
@app.route('/get-min-avg-max', methods=['POST'])
def get_temperature_stats():
    if request.get_json(force=True)["password"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    data = fetch_min_avg_max()
    return jsonify(data)

@app.route('/get-min-avg-max-outdoor', methods=['POST'])
def get_temperature_stats_outdoor():
    if request.get_json(force=True)["password"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    data = fetch_min_avg_max_outdoor()
    return jsonify(data)

@app.route('/get_daily_forecast', methods=['POST'])
def daily_forecast():
    # Authenticate the request
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    
    # Get city information from the request
    city_info = request.get_json(force=True).get("city")
    if not city_info or 'lat' not in city_info or 'lon' not in city_info:
        return jsonify({"error": "City information is incomplete"}), 400
    
    # Fetch the forecast
    forecast = get_daily_forecast(OPENWEATHER_API_KEY, city_info)
    if forecast:
        return jsonify(forecast)
    else:
        return jsonify({"error": "Failed to fetch forecast"}), 500

def get_daily_forecast(api_key, city):
    """Fetches the weather forecast for the next 5 days for a specified city using OpenWeatherMap's API."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={city['lat']}&lon={city['lon']}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecast_dict = {}
        for entry in data['list']:
            date = datetime.utcfromtimestamp(entry['dt']).strftime('%Y-%m-%d')
            if date not in forecast_dict:
                forecast_dict[date] = {
                    'min_temperature': entry['main']['temp_min'],
                    'max_temperature': entry['main']['temp_max'],
                    'descriptions': [entry['weather'][0]['description']],
                    'icon': entry['weather'][0]['icon']  # Store the icon code
                }
            else:
                # Update min and max temperatures
                forecast_dict[date]['min_temperature'] = min(forecast_dict[date]['min_temperature'], entry['main']['temp_min'])
                forecast_dict[date]['max_temperature'] = max(forecast_dict[date]['max_temperature'], entry['main']['temp_max'])
                # Append description and update icon if it's not already included
                if entry['weather'][0]['description'] not in forecast_dict[date]['descriptions']:
                    forecast_dict[date]['descriptions'].append(entry['weather'][0]['description'])
                    forecast_dict[date]['icon'] = entry['weather'][0]['icon']  # Assuming the last description has the relevant icon

        forecast_list = []
        for date, values in forecast_dict.items():
            forecast_list.append({
                'date': date,
                'min_temperature': values['min_temperature'],
                'max_temperature': values['max_temperature'],
                'descriptions': values['descriptions'][-1],  
                'icon': values['icon']  # Include the related icon code
            })

        forecast_list = sorted(forecast_list, key=lambda x: x['date'])[:5]
        return forecast_list
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
