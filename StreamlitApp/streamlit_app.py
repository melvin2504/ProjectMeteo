import time
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts
from datetime import datetime




def live_clock():
    time_display = st.empty()  # Create a placeholder
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")  # Format the time as Hour:Minute:Second
        time_display.markdown(f"**Current Time: {current_time}**")  # Update the placeholder with the current time
        time.sleep(1)  # Wait for 1 second before updating again

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
            {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line", "name": "Temperature"},
            {"data": [45, 50, 55, 60, 65, 70, 75], "type": "bar", "yAxisIndex": 1, "name": "Humidity"}  # Changed to bar plot for humidity
        ],
    }
    st_echarts(options=option, height="400px")

if __name__ == "__main__":
    st.title('Weather Dashboard')
    render_basic_bar()
    live_clock()
    


