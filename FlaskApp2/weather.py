import requests
from datetime import datetime

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
                    'icon': entry['weather'][0]['icon']
                }
            else:
                forecast_dict[date]['min_temperature'] = min(forecast_dict[date]['min_temperature'], entry['main']['temp_min'])
                forecast_dict[date]['max_temperature'] = max(forecast_dict[date]['max_temperature'], entry['main']['temp_max'])
                if entry['weather'][0]['description'] not in forecast_dict[date]['descriptions']:
                    forecast_dict[date]['descriptions'].append(entry['weather'][0]['description'])
                    forecast_dict[date]['icon'] = entry['weather'][0]['icon']

        forecast_list = []
        for date, values in forecast_dict.items():
            forecast_list.append({
                'date': date,
                'min_temperature': values['min_temperature'],
                'max_temperature': values['max_temperature'],
                'descriptions': values['descriptions'][-1],
                'icon': values['icon']
            })

        forecast_list = sorted(forecast_list, key=lambda x: x['date'])[:5]
        return forecast_list
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
