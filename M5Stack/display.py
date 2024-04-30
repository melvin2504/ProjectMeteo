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

# Function to choose correct icon
def get_icon(description, is_daytime=True):
    if is_daytime:
        return weather_icons_day.get(description, '01d.png')  # default in case description is not found
    else:
        return weather_icons_night.get(description, '01d.png')

# Set up the RTC to sync time via NTP
rtc.settime('ntp', host='cn.pool.ntp.org', tzone=3)  # Adjust the time zone parameter as needed

def get_datetime_strings():
    dt = rtc.datetime()  # Get the current datetime tuple from the RTC
    # Format the date string (Year-Month-Day)
    date_string = "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])
    # Format the time string (Hour:Minute:Second)
    time_string = "{:02}:{:02}:{:02}".format(dt[4], dt[5], dt[6])
    return date_string, time_string
    
passwd_hash = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab"  

def fetch_outdoor_weather():
    url = 'https://flaskapp3-vukguwbvha-oa.a.run.app/get_outdoor_weather'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash}, headers=headers)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print("Failed to fetch weather data: ", response.status_code)
        return None
        
def fetch_forecast():
    url = 'https://flaskapp3-vukguwbvha-oa.a.run.app/get_daily_forecast'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash, "city": {"lat": 48.8566, "lon": 2.3522}}, headers=headers)  # Example lat/lon for Paris
    if response.status_code == 200:
        forecast_data = response.json()
        return forecast_data
    else:
        print("Failed to fetch forecast data: ", response.status_code)
        return None
        
forecast_label = M5Label('', x=90, y=90, color=0x000, font=FONT_MONT_14, parent=None)  # Adjust x, y for centering

def update_forecast_display():
    forecast_data = fetch_forecast()
    if forecast_data:
        # Parse the first day's data
        first_day = forecast_data[0]
        
        # Extract date components
        year, month, day = map(int, first_day['date'].split('-'))
        if month < 3:
            month += 12
            year -= 1
            
        # Zeller's Congruence to calculate the day of the week
        weekday_num = (day + (13 * (month + 1)) // 5 + year + year // 4 - year // 100 + year // 400) % 7
        weekdays = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]  # Adjusted for Zeller's output
        weekday_name = weekdays[weekday_num]

        # Format temperatures as integers to remove decimals
        min_temp = int(round(float(first_day['min_temperature'])))
        max_temp = int(round(float(first_day['max_temperature'])))

        # Update the label text
        forecast_text = "{}: {}°C / {}°C, {}".format(weekday_name, min_temp, max_temp, first_day['description'])
        forecast_label.set_text(forecast_text)
    else:
        forecast_label.set_text("No forecast data available")
        
# Add an M5Img widget for the weather icon
weather_icon = M5Img('res/01d.png', x=230, y=128, parent=None)  # Adjust position as needed

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
        update_forecast_display()
        if outdoor_weather:
            description = outdoor_weather['outdoor_weather']
            icon_path = 'res/' + outdoor_weather['icon_code'] + '.png'
            weather_icon.set_img_src(icon_path)  # Update the icon on the display
            label2.set_text(str(round(outdoor_weather['outdoor_temp'])) + "°C")
            label3.set_text(str(round(outdoor_weather['outdoor_humidity'])) + "%")
        outdoor_weather_flag = 0  # Reset the counter

    outdoor_weather_flag += 1
    
    date_label.set_text(date_string)
    time_label.set_text(time_string)
    label0.set_text(str(round(env3_0.temperature)) + "°C")
    label1.set_text(str(round(env3_0.humidity)) + "%")

    # Send data every 5 minutes
    if temp_flag >= 300:
        data = {
            "passwd": passwd_hash,
            "values": {
                "date": date_string,
                "time": time_string,
                "indoor_temp": round(env3_0.temperature),
                "indoor_humidity": round(env3_0.humidity)
            }
        }
        urequests.post("https://flaskapp3-vukguwbvha-oa.a.run.app/send-to-bigquery", json=data)
        temp_flag = 0
    temp_flag += 1
    wait_ms(1000)  # wait for one second, then increase the wait time calculation





