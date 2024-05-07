import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts
from datetime import datetime
import random
import requests


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

if __name__ == "__main__":
    st.title('Weather Dashboard')
    render_basic_bar()
    temp_gauge()
    render_heatmap()    
    #live_clock()
    


