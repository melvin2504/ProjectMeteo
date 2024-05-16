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

        # Fill the dictionary with the data
        for _, row in df.iterrows():
            day_str = row['hour'].strftime('%A')
            hour_str = row['hour'].strftime('%I%p').lstrip('0').lower()
            temp_dict[(day_str, hour_str)] = row['max_outdoor_temp']
            humidity_dict[(day_str, hour_str)] = row['max_outdoor_humidity']

        # Prepare data for the heatmap
        temp_data = []
        humidity_data = []
        for day in days:
            for hour in hours:
                temp_value = temp_dict.get((day, hour), None)
                humidity_value = humidity_dict.get((day, hour), None)
                if temp_value is not None:
                    temp_data.append([hours.index(hour), days.index(day), temp_value])
                if humidity_value is not None:
                    humidity_data.append([hours.index(hour), days.index(day), humidity_value])

        # Define heatmap options for temperature
        temp_heatmap_options = {
            "tooltip": {
                "position": "top"
            },
            "grid": {
                "height": "50%",
                "top": "10%"
            },
            "xAxis": {
                "type": "category",
                "data": hours,
                "splitArea": {
                    "show": True
                }
            },
            "yAxis": {
                "type": "category",
                "data": days,
                "splitArea": {
                    "show": True
                }
            },
            "visualMap": {
                "min": df['max_outdoor_temp'].min(),
                "max": df['max_outdoor_temp'].max(),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "15%"
            },
            "series": [{
                "name": "Max Outdoor Temperature",
                "type": "heatmap",
                "data": temp_data,
                "label": {
                    "show": True
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
            "tooltip": {
                "position": "top"
            },
            "grid": {
                "height": "50%",
                "top": "10%"
            },
            "xAxis": {
                "type": "category",
                "data": hours,
                "splitArea": {
                    "show": True
                }
            },
            "yAxis": {
                "type": "category",
                "data": days,
                "splitArea": {
                    "show": True
                }
            },
            "visualMap": {
                "min": df['max_outdoor_humidity'].min(),
                "max": df['max_outdoor_humidity'].max(),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "15%"
            },
            "series": [{
                "name": "Max Outdoor Humidity",
                "type": "heatmap",
                "data": humidity_data,
                "label": {
                    "show": True
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





def render_heatmap():
    # Time slots and days
    hours = [
        '12am', '1am', '2am', '3am', '4am', '5am', '6am',
        '7am', '8am', '9am','10am','11am',
        '12pm', '1pm', '2pm', '3pm', '4pm', '5pm',
        '6pm', '7pm', '8pm', '9pm', '10pm', '11pm'
    ]
    
    days = [
        'Saturday', 'Friday', 'Thursday',
        'Wednesday', 'Tuesday', 'Monday', 'Sunday'
    ]
    
    # Data points [day, hour, value]
    data = [
        [0,0,5],[0,1,1],[0,2,0],[0,3,0],[0,4,0],[0,5,0],[0,6,0],[0,7,0],[0,8,0],[0,9,0],[0,10,0],[0,11,2],[0,12,4],[0,13,1],[0,14,1],[0,15,3],[0,16,4],[0,17,6],[0,18,4],[0,19,4],[0,20,3],[0,21,3],[0,22,2],[0,23,5],[1,0,7],[1,1,0],[1,2,0],[1,3,0],[1,4,0],[1,5,0],[1,6,0],[1,7,0],[1,8,0],[1,9,0],[1,10,5],[1,11,2],[1,12,2],[1,13,6],[1,14,9],[1,15,11],[1,16,6],[1,17,7],[1,18,8],[1,19,12],[1,20,5],[1,21,5],[1,22,7],[1,23,2],[2,0,1],[2,1,1],[2,2,0],[2,3,0],[2,4,0],[2,5,0],[2,6,0],[2,7,0],[2,8,0],[2,9,0],[2,10,3],[2,11,2],[2,12,1],[2,13,9],[2,14,8],[2,15,10],[2,16,6],[2,17,5],[2,18,5],[2,19,5],[2,20,7],[2,21,4],[2,22,2],[2,23,4],[3,0,7],[3,1,3],[3,2,0],[3,3,0],[3,4,0],[3,5,0],[3,6,0],[3,7,0],[3,8,1],[3,9,0],[3,10,5],[3,11,4],[3,12,7],[3,13,14],[3,14,13],[3,15,12],[3,16,9],[3,17,5],[3,18,5],[3,19,10],[3,20,6],[3,21,4],[3,22,4],[3,23,1],[4,0,1],[4,1,3],[4,2,0],[4,3,0],[4,4,0],[4,5,1],[4,6,0],[4,7,0],[4,8,0],[4,9,2],[4,10,4],[4,11,4],[4,12,2],[4,13,4],[4,14,4],[4,15,14],[4,16,12],[4,17,1],[4,18,8],[4,19,5],[4,20,3],[4,21,7],[4,22,3],[4,23,0],[5,0,2],[5,1,1],[5,2,0],[5,3,3],[5,4,0],[5,5,0],[5,6,0],[5,7,0],[5,8,2],[5,9,0],[5,10,4],[5,11,1],[5,12,5],[5,13,10],[5,14,5],[5,15,7],[5,16,11],[5,17,6],[5,18,0],[5,19,5],[5,20,3],[5,21,4],[5,22,2],[5,23,0],[6,0,1],[6,1,0],[6,2,0],[6,3,0],[6,4,0],[6,5,0],[6,6,0],[6,7,0],[6,8,0],[6,9,0],[6,10,1],[6,11,0],[6,12,2],[6,13,1],[6,14,3],[6,15,4],[6,16,0],[6,17,0],[6,18,0],[6,19,0],[6,20,1],[6,21,2],[6,22,2],[6,23,6]
    ]
    # Remapping the data format from JavaScript to Python's index order
    data = [[item[1], item[0], item[2] or '-'] for item in data]
    
    options = {
        "tooltip": {
            "position": 'top'
        },
        "grid": {
            "height": '50%',
            "top": '10%'
        },
        "xAxis": {
            "type": 'category',
            "data": hours,
            "splitArea": {
                "show": True
            }
        },
        "yAxis": {
            "type": 'category',
            "data": days,
            "splitArea": {
                "show": True
            }
        },
        "visualMap": {
            "min": 0,
            "max": 10,
            "calculable": True,
            "orient": 'horizontal',
            "left": 'center',
            "bottom": '15%'
        },
        "series": [
            {
                "name": 'Punch Card',
                "type": 'heatmap',
                "data": data,
                "label": {
                    "show": True
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    }
    
    # Display the chart
    st_echarts(options=options, height="500px")

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

if __name__ == "__main__":
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h1 style="margin: 0;">Weather Dashboard</h1>
            <h2 style="margin: 0;">{datetime.now().strftime("%d-%B-%Y")}</h2>
        </div>
        """, unsafe_allow_html=True)
    city_lat = 46.5197
    city_lon = 6.6323
    forecast = fetch_daily_forecast(city_lat, city_lon, YOUR_HASH_PASSWD)
    hourly = fetch_hourly_max(YOUR_HASH_PASSWD)
    display_forecast(forecast)
    render_heatmap_2(hourly)
    render_basic_bar()
    temp_gauge()
    render_heatmap()    
    #live_clock()


