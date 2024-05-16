import time
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta
import requests
from PIL import Image
import pytz

YOUR_HASH_PASSWD = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(BASE_DIR, 'Icons')  # Path to the Icons folder
IMAGE_DIR = os.path.join(BASE_DIR, 'Images')  # Path to the Images folder

def fetch_latest_temperature():
    url = 'http://127.0.0.1:8080/get-latest-temperature'  # Endpoint URL
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['temperature']  # Assumes the response is {'temperature': value}
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error('Failed to fetch latest temperature: {}'.format(e))
        return None

def fetch_outdoor_weather(password):
    response = requests.post("http://localhost:8080/get_outdoor_weather", json={"password": password})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch outdoor weather data")
        return None
    
def fetch_daily_forecast(city_lat, city_lon, password):
    url = 'http://127.0.0.1:8080/get_daily_forecast'  # Adjust the URL if Flask is running on a different host or port
    headers = {'Content-Type': 'application/json'}
    data = {
        "passwd": password,
        "city": {
            "lat": city_lat,
            "lon": city_lon
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        forecast = response.json()
        return forecast
    else:
        st.error(f"Failed to retrieve forecast: {response.json().get('error', 'Unknown error')}")
        return None

def fetch_hourly_max(password):
    response = requests.post("http://localhost:8080/hourly-max", json={"password": password})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch hourly max data")
        return None 

def temp_gauge():
    latest_temp = fetch_latest_temperature()
    st.write(f"Latest temperature: {latest_temp} °C")
    options = {
        "series": [
            {
                "type": 'gauge',
                "center": ['50%', '60%'],
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 60,
                "splitNumber": 12,
                "itemStyle": {
                    "color": '#FFAB91'
                },
                "progress": {
                    "show": True,
                    "width": 30
                },
                "pointer": {
                    "show": False
                },
                "axisLine": {
                    "lineStyle": {
                        "width": 30
                    }
                },
                "axisTick": {
                    "distance": -45,
                    "splitNumber": 5,
                    "lineStyle": {
                        "width": 2,
                        "color": '#999'
                    }
                },
                "splitLine": {
                    "distance": -52,
                    "length": 14,
                    "lineStyle": {
                        "width": 3,
                        "color": '#999'
                    }
                },
                "axisLabel": {
                    "distance": -20,
                    "color": '#999',
                    "fontSize": 20
                },
                "anchor": {
                    "show": False
                },
                "title": {
                    "show": False
                },
                "detail": {
                    "valueAnimation": True,
                    "width": '60%',
                    "lineHeight": 40,
                    "borderRadius": 8,
                    "offsetCenter": [0, '-15%'],
                    "fontSize": 60,
                    "fontWeight": 'bolder',
                    "formatter": '{value} °C',
                    "color": 'inherit'
                },
                "data": [
                    {
                        "value": 20
                    }
                ]
            },
            {
                "type": 'gauge',
                "center": ['50%', '60%'],
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 60,
                "itemStyle": {
                    "color": '#FD7347'
                },
                "progress": {
                    "show": True,
                    "width": 8
                },
                "pointer": {
                    "show": False
                },
                "axisLine": {
                    "show": False
                },
                "axisTick": {
                    "show": False
                },
                "splitLine": {
                    "show": False
                },
                "axisLabel": {
                    "show": False
                },
                "detail": {
                    "show": False
                },
                "data": [
                    {
                        "value": 20
                    }
                ]
            }
        ]
    }


    
    options["series"][0]["data"][0]["value"] = latest_temp
    options["series"][1]["data"][0]["value"] = latest_temp
    st_echarts(options=options, height="500px")

def render_basic_bar():
    option = {
        "backgroundColor": 'transparent',
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        "yAxis": [
            {"type": "value", "name": "Temperature"},  # First y-axis for temperature
            {"type": "value", "name": "Humidity", "axisLabel": {"formatter": '{value}%'}, "min": 0, "max": 100}  # Second y-axis for humidity
        ],
        "series": [
            {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line", "name": "Temperature", "itemStyle": {"color": "red"}},
            {"data": [45, 50, 55, 60, 65, 70, 75], "type": "bar", "yAxisIndex": 1, "name": "Humidity", "itemStyle": {"color": "navy"}}
        ],

    }
    st_echarts(options=option, height="400px")

def round_time_to_nearest_hour(time):
    return (time + timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)

#skkr samarche
def render_heatmap_2(data):
    if data:
        # Convert the data into a DataFrame
        df = pd.DataFrame(data)
        df['hour'] = pd.to_datetime(df['hour'])

        # Define the timezone for UTC+1
        local_tz = pytz.timezone('Etc/GMT-1')

        # Convert 'hour' column to local time and round to nearest hour
        df['hour'] = df['hour'].apply(lambda x: round_time_to_nearest_hour(x + timedelta(hours=1)))

        # Generate list of the last 7 days with hours
        end_date = datetime.now(local_tz)
        start_date = end_date - timedelta(days=6)
        days = [(end_date - timedelta(days=i)).strftime('%A') for i in range(7)][::-1]

        # Specified hours for display
        hours = [
            '12am', '1am', '2am', '3am', '4am', '5am', '6am',
            '7am', '8am', '9am', '10am', '11am',
            '12pm', '1pm', '2pm', '3pm', '4pm', '5pm',
            '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'
        ]

        # Create a dictionary to hold the hourly max data
        temp_dict = {(day, hour): None for day in days for hour in hours}
        humidity_dict = {(day, hour): None for day in days for hour in hours}

        # Fill the dictionary with the max values for each hour
        for _, row in df.iterrows():
            day_str = row['hour'].strftime('%A')
            hour_str = row['hour'].strftime('%I%p').lstrip('0').lower()
            if temp_dict[(day_str, hour_str)] is None or row['max_outdoor_temp'] > temp_dict[(day_str, hour_str)]:
                temp_dict[(day_str, hour_str)] = row['max_outdoor_temp']
            if humidity_dict[(day_str, hour_str)] is None or row['max_outdoor_humidity'] > humidity_dict[(day_str, hour_str)]:
                humidity_dict[(day_str, hour_str)] = row['max_outdoor_humidity']

        # Prepare data for the heatmap
        temp_data = []
        humidity_data = []
        for day in days:
            for hour in hours:
                temp_value = temp_dict.get((day, hour), None)
                humidity_value = humidity_dict.get((day, hour), None)
                if temp_value is not None:
                    temp_data.append([hours.index(hour), days.index(day), int(temp_value)])
                if humidity_value is not None:
                    humidity_data.append([hours.index(hour), days.index(day), int(humidity_value)])

        # Define heatmap options for temperature
        temp_heatmap_options = {
            "backgroundColor": "#0e1117",  # Set the background to dark
            "tooltip": {
                "position": "top",
                "formatter": 'Temp: {c} °C',
                "textStyle": {
                    "color": "#fff"  # Tooltip text color
                }
            },
            "grid": {
                "height": "50%",
                "top": "10%",
                "backgroundColor": "#0e1117"
            },
            "xAxis": {
                "type": "category",
                "data": hours,
                "splitArea": {
                    "show": True
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "#fff"  # X-axis line color
                    }
                },
                "axisLabel": {
                    "color": "#fff"  # X-axis label color
                }
            },
            "yAxis": {
                "type": "category",
                "data": days,
                "splitArea": {
                    "show": True
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "#fff"  # Y-axis line color
                    }
                },
                "axisLabel": {
                    "color": "#fff"  # Y-axis label color
                }
            },
            "visualMap": {
                "min": df['max_outdoor_temp'].min(),
                "max": df['max_outdoor_temp'].max(),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "15%",
                "inRange": {
                    "color": ['#3c8dbc', '#d35400']  # Color gradient for the heatmap
                },
                "textStyle": {
                    "color": "#fff"  # Visual map text color
                }
            },
            "series": [{
                "name": "Max Outdoor Temperature",
                "type": "heatmap",
                "data": temp_data,
                "label": {
                    "show": True,
                    "color": "#fff"  # Label color
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }

        # Define heatmap options for humidity
        humidity_heatmap_options = {
            "backgroundColor": "#0e1117",  # Set the background to dark
            "tooltip": {
                "position": "top",
                "formatter": 'Humidity: {c} %',
                "textStyle": {
                    "color": "#fff"  # Tooltip text color
                }
            },
            "grid": {
                "height": "50%",
                "top": "10%",
                "backgroundColor": "#0e1117"
            },
            "xAxis": {
                "type": "category",
                "data": hours,
                "splitArea": {
                    "show": True
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "#fff"  # X-axis line color
                    }
                },
                "axisLabel": {
                    "color": "#fff"  # X-axis label color
                }
            },
            "yAxis": {
                "type": "category",
                "data": days,
                "splitArea": {
                    "show": True
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "#fff"  # Y-axis line color
                    }
                },
                "axisLabel": {
                    "color": "#fff"  # Y-axis label color
                }
            },
            "visualMap": {
                "min": df['max_outdoor_humidity'].min(),
                "max": df['max_outdoor_humidity'].max(),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "15%",
                "inRange": {
                    "color": ['#D0E6F5', '#3399FF']  # Blue gradient for the heatmap
                },
                "textStyle": {
                    "color": "#fff"  # Visual map text color
                }
            },
            "series": [{
                "name": "Max Outdoor Humidity",
                "type": "heatmap",
                "data": humidity_data,
                "label": {
                    "show": True,
                    "color": "#fff"  # Label color
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }

        # Render heatmaps
        st.write("## Heatmap of Max Outdoor Temperature")
        st_echarts(options=temp_heatmap_options, height="500px")

        st.write("## Heatmap of Max Outdoor Humidity")
        st_echarts(options=humidity_heatmap_options, height="500px")

def display_outdoor_weather(weather_data):
    if weather_data:
        st.write("### Current Outdoor Weather")

        cols = st.columns(3)
        
        # Display weather icon and description
        icon_path = os.path.join(ICON_DIR, f"{weather_data['icon_code']}.png")
        with cols[0]:
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                st.image(icon_image, width=50)
            else:
                st.error(f"Icon file {icon_path} not found.")
            st.write(f"**{weather_data['outdoor_weather'].capitalize()}**")
        
        # Display temperature icon and value
        temp_icon_path = os.path.join(IMAGE_DIR, "icons8-temperature-32_white.png")
        with cols[1]:
            if os.path.exists(temp_icon_path):
                temp_icon_image = Image.open(temp_icon_path)
                st.image(temp_icon_image, width=30)
            else:
                st.error(f"Temperature icon file {temp_icon_path} not found.")
            st.write(f"{weather_data['outdoor_temp']} °C")

        # Display humidity icon and value
        humidity_icon_path = os.path.join(IMAGE_DIR, "icons8-humidity-32_white.png")
        with cols[2]:
            if os.path.exists(humidity_icon_path):
                humidity_icon_image = Image.open(humidity_icon_path)
                st.image(humidity_icon_image, width=30)
            else:
                st.error(f"Humidity icon file {humidity_icon_path} not found.")
            st.write(f"{weather_data['outdoor_humidity']} %")

            
def display_forecast(forecast_data):
    # Using columns in Streamlit to display each piece of data
    cols = st.columns(len(forecast_data))
    days = [datetime.strptime(day['date'], "%Y-%m-%d").strftime('%a') for day in forecast_data]
    temps = [f"{round(day['min_temperature'])}°C / {round(day['max_temperature'])}°C" for day in forecast_data]
    icons = [os.path.join(ICON_DIR, f"{day['icon']}.png") for day in forecast_data]

    for col, day, temp, icon_path in zip(cols, days, temps, icons):
        with col:
            st.write(day)
            image = Image.open(icon_path)
            st.image(image)  # Adjust the width as necessary
            st.write(temp)

def main():
    st.sidebar.title("Navigation")
    st.sidebar.markdown("## Pages")
    page = st.sidebar.radio("Select a page", ["Welcome", "Graphics"], label_visibility='collapsed')

    if page == "Welcome":
        st.title("Weather Dashboard")
        st.subheader(f"{datetime.now().strftime('%d-%b-%Y')}")
        city_lat = 46.5197
        city_lon = 6.6323
        forecast = fetch_daily_forecast(city_lat, city_lon, YOUR_HASH_PASSWD)
        display_forecast(forecast)
        outdoor_weather = fetch_outdoor_weather(YOUR_HASH_PASSWD)
        if outdoor_weather:
            display_outdoor_weather(outdoor_weather)

    elif page == "Graphics":
        st.title("Weather Graphics")
        hourly = fetch_hourly_max(YOUR_HASH_PASSWD)
        render_heatmap_2(hourly)
        render_basic_bar()
        temp_gauge()


if __name__ == "__main__":
    main()





