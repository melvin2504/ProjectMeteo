import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta

st.title('Weather Dashboard')



def render_basic_bar():
    option = {
        "backgroundColor": 'transparent',
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        "yAxis": {"type": "value"},
        "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}],
    }
    st_echarts(options=option, height="400px")

render_basic_bar()
