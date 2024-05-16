from flask import Flask, request, jsonify, Response
from google.cloud import bigquery, texttospeech
from weather import get_weather, get_daily_forecast, weather_icons
from openai_utils import generate_weather_advice
from google_cloud_utils import insert_data_to_bigquery, query_latest_weather, query_latest_data
from config import OPENWEATHER_API_KEY, YOUR_HASH_PASSWD, GCP_PROJECT_ID
import matplotlib.pyplot as plt
import pandas as pd
import os

# Uncomment the line below if you want to run your flask app locally.
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./lab-test-1-415115-c2f0b755d8b4.json"

app = Flask(__name__)

client = bigquery.Client(project=GCP_PROJECT_ID)
tts_client = texttospeech.TextToSpeechClient()

@app.route('/')
def index():
    return "Welcome to the Weather App!"

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

@app.route('/historical_data_graph', methods=['POST'])
def historical_data_graph():
    # Verify password from the request
    if request.get_json(force=True)["passwd"] != YOUR_HASH_PASSWD:
        return jsonify({"error": "Incorrect Password!"}), 401

    # Query the latest data from BigQuery
    filtered_df = query_latest_data(client, GCP_PROJECT_ID, "weather_IoT_data", "weather-records")
    
    # Plot the data
    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(filtered_df['datetime'], filtered_df['indoor_temp'], marker='o')
    plt.title('Indoor Temperature over the Last 6 Hours')
    plt.ylabel('Temperature (°C)')
    
    plt.subplot(3, 1, 2)
    plt.plot(filtered_df['datetime'], filtered_df['indoor_humidity'], marker='o', color='orange')
    plt.title('Indoor Humidity over the Last 6 Hours')
    plt.ylabel('Humidity (%)')
    
    plt.subplot(3, 1, 3)
    plt.plot(filtered_df['datetime'], filtered_df['indoor_tvoc'], marker='o', color='green')
    plt.title('Indoor Air Quality (TVOC) over the Last 6 Hours')
    plt.ylabel('TVOC (ppb)')
    plt.xlabel('Time')
    
    plt.tight_layout()

    # Save the plot to a file
    plot_path = '/mnt/data/indoor_data_plot.png'
    plt.savefig(plot_path)
    plt.close()

    # Return the plot as an image
    return send_file(plot_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
