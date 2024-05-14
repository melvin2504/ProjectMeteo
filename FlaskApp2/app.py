from flask import Flask, request, jsonify, Response
from google.cloud import bigquery, texttospeech
from weather import get_weather, get_daily_forecast, weather_icons
from openai_utils import generate_weather_advice
from google_cloud_utils import insert_data_to_bigquery, query_latest_weather
import hashlib
import binascii
import os

# Uncomment the line below if you want to run your flask app locally.
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./lab-test-1-415115-c2f0b755d8b4.json"

app = Flask(__name__)

# Constants and Config
YOUR_HASH_PASSWD = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab"
OPENWEATHER_API_KEY = "6b85e31b08c576ddd0a8f6a60e5afc01"

client = bigquery.Client(project="lab-test-1-415115")
tts_client = texttospeech.TextToSpeechClient()

@app.route('/')
def index():
    return "Welcome to the Weather App!"

@app.route('/get-latest-temperature', methods=['GET'])
def get_latest_temperature():
    try:
        temperature = query_latest_weather(client)
        return jsonify({"temperature": temperature})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
