from m5stack import *
from m5stack_ui import *
from uiflow import *
import time
import unit
import urequests
import hashlib
import binascii
import ntptime
import machine

screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xd5d5d5)
env3_0 = unit.get(unit.ENV3, unit.PORTA)
temp_flag = 300

# Set up the RTC to sync time via NTP
rtc.settime('ntp', host='cn.pool.ntp.org', tzone=2)  # Adjust the time zone parameter as needed

def get_datetime_strings():
    dt = rtc.datetime()  # Get the current datetime tuple from the RTC
    # Format the date string (Year-Month-Day)
    date_string = "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])
    # Format the time string (Hour:Minute:Second)
    time_string = "{:02}:{:02}:{:02}".format(dt[4], dt[5], dt[6])
    return date_string, time_string
    
passwd_hash = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab"  

def fetch_outdoor_weather():
    url = 'https://flaskapp4-vukguwbvha-oa.a.run.app/get_outdoor_weather'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch weather data: ", response.status_code)
        return None

# Display labels for date, time, temperature, and humidity
date_label = M5Label('Date', x=19, y=40, color=0x000, font=FONT_MONT_18, parent=None)
time_label = M5Label('Time', x=230, y=40, color=0x000, font=FONT_MONT_18, parent=None)
temperature_icon = M5Img('res/icons8-temperature-32.png', x=19, y=135, parent=None)
humidity_icon = M5Img('res/icons8-humidity-32.png', x=19, y=180, parent=None)
label0 = M5Label('T', x=63, y=142, color=0x000, font=FONT_MONT_22, parent=None)
label1 = M5Label('H', x=63, y=183, color=0x000, font=FONT_MONT_22, parent=None)
label2 = M5Label('OT', x=143, y=142, color=0x000, font=FONT_MONT_22, parent=None)
label3 = M5Label('OH', x=143, y=183, color=0x000, font=FONT_MONT_22, parent=None)

passwd = "vendgelanonoarnaknonoob"
h = hashlib.sha256(passwd.encode('utf-8'))
passwd_hash = binascii.hexlify(h.digest()).decode('utf-8')

outdoor_weather_flag = 600  # Fetch outdoor weather every 10 minutes

while True:
    date_string, time_string = get_datetime_strings()
    if outdoor_weather_flag >= 600:
        outdoor_weather = fetch_outdoor_weather()
        if outdoor_weather:
            label2.set_text(str(round(outdoor_weather['outdoor_temp'])) + "°C")
            label3.set_text(str(round(outdoor_weather['outdoor_humidity'])) + "%")
        outdoor_weather_flag = 0  # Reset the counter

    outdoor_weather_flag += 1
    
    date_label.set_text(date_string)
    time_label.set_text(time_string)
    label0.set_text(str(round(env3_0.temperature)) + "°C")
    label1.set_text(str(round(env3_0.humidity)) + "%")

    # Send data every 2 minutes
    if temp_flag >= 120:
        data = {
            "passwd": passwd_hash,
            "values": {
                "date": date_string,
                "time": time_string,
                "indoor_temp": round(env3_0.temperature),
                "indoor_humidity": round(env3_0.humidity)
            }
        }
        urequests.post("https://flaskapp4-vukguwbvha-oa.a.run.app/send-to-bigquery", json=data)
        temp_flag = 0
    temp_flag += 1
    wait_ms(1000)  # wait for one second, then increase the wait time calculation


