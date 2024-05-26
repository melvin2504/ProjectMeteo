from flask import Flask, request, jsonify, Response
from google.cloud import bigquery, texttospeech
from openai_utils import generate_weather_advice
from weather import get_weather, get_daily_forecast, weather_icons
from google_cloud_utils import insert_data_to_bigquery, query_latest_weather, query_latest_data, fetch_min_avg_max_outdoor, fetch_min_avg_max, fetch_hourly_max_for_last_7_days, fetch_tvoc_co2
from config import OPENWEATHER_API_KEY, YOUR_HASH_PASSWD, GCP_PROJECT_ID
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import pandas as pd
import tempfile
import os

# Uncomment the line below if you want to run your flask app locally.
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "YOUR JSON FILE"

app = Flask(__name__)

client = bigquery.Client(project=GCP_PROJECT_ID)
tts_client = texttospeech.TextToSpeechClient()

@app.route('/')
def index():
    return "Welcome to the Weather App!"

@app.route('/generate_advice_audio', methods=['POST'])
def generate_advice_audio():
    weather_data = request.get_json(force=True)
    temperature = round(weather_data.get('outdoor_temp'))
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

    try:
        insert_data_to_bigquery(client, data)
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_outdoor_weather', methods=['POST'])
def get_outdoor_weather():
    # Verify password from the request
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401

    try:
        weather_data = query_latest_weather(client)
        icon_code = weather_icons.get(weather_data['outdoor_weather'], '01d')
        weather_data['icon_code'] = icon_code
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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

@app.route('/get-latest-indoor', methods=['POST'])
def get_latest_indoor():
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    
    query = """
    SELECT indoor_temp, indoor_humidity, indoor_tvoc, indoor_eco2
    FROM `lab-test-1-415115.weather_IoT_data.weather-records`
    ORDER BY date DESC, time DESC
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

@app.route('/get-min-avg-max', methods=['POST'])
def get_temperature_stats():
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    data = fetch_min_avg_max(client)
    return jsonify(data)

@app.route('/get-min-avg-max-outdoor', methods=['POST'])
def get_temperature_stats_outdoor():
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    data = fetch_min_avg_max_outdoor(client)
    return jsonify(data)

@app.route('/hourly-max', methods=['POST'])
def get_hourly_max():
    data = fetch_hourly_max_for_last_7_days(client)
    return jsonify(data)

@app.route('/historical_data_graph', methods=['POST'])
def historical_data_graph():
    # Verify password from the request
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401

    # Query the latest data from BigQuery
    filtered_df = query_latest_data(client, GCP_PROJECT_ID, "weather_IoT_data", "weather-records")
    
    # Format datetime column to only show time
    filtered_df['time_only'] = filtered_df['datetime'].dt.strftime('%H:%M:%S')
    
    # Plot the data
    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(filtered_df['time_only'], filtered_df['indoor_temp'], marker='o')
    plt.title('Indoor Temperature (Last 25 Measurements)')
    plt.ylabel('Temperature (°C)')
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))  # Adjust nbins as needed

    plt.subplot(3, 1, 2)
    plt.plot(filtered_df['time_only'], filtered_df['indoor_humidity'], marker='o', color='orange')
    plt.title('Indoor Humidity (Last 25 Measurements)')
    plt.ylabel('Humidity (%)')
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))  # Adjust nbins as needed

    plt.subplot(3, 1, 3)
    plt.plot(filtered_df['time_only'], filtered_df['indoor_tvoc'], marker='o', color='green')
    plt.title('Indoor Air Quality (TVOC) (Last 25 Measurements)')
    plt.ylabel('TVOC (ppb)')
    plt.xlabel('Time')
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))  # Adjust nbins as needed
    
    plt.tight_layout()

    # Save the plot to a temporary file and read it into memory
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
        plt.savefig(tmpfile.name)
        plot_data = Image.open(tmpfile.name).resize((320, 240), Image.LANCZOS)  # Resize to fit M5Stack Core2 screen
        plot_data.save(tmpfile.name, format='PNG')
        plot_data = tmpfile.read()
    
    plt.close()

    # Create a response with the image data
    response = Response(plot_data, mimetype='image/png')
    response.headers['Content-Disposition'] = 'attachment; filename=indoor_data_plot.png'
    
    # Remove the temporary file
    os.remove(tmpfile.name)

    return response

@app.route('/get-tvoc-co2', methods=['POST'])
def get_tvoc_co2():
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401
    df = fetch_tvoc_co2(client)
    return jsonify(df)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
