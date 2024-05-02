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
motion_sensor = unit.get(unit.PIR, unit.PORTB)
tvoc0 = unit.get(unit.TVOC, unit.PORTC)
temp_flag = 300



# Set up the RTC to sync time via NTP
rtc.settime('ntp', host='ch.pool.ntp.org', tzone=2)  # Adjust the time zone parameter as needed

def check_motion():
    if motion_sensor.state == 1:
        greeting_label.set_text('Bonjour Melvin')
    else:
        greeting_label.set_text('')
        
def update_air_quality():
    tvoc = tvoc0.TVOC
    eco2 = tvoc0.eCO2
    tvoc_label.set_text('TVOC: {} ppb'.format(tvoc))
    eco2_label.set_text('eCO2: {} ppm'.format(eco2))


def get_datetime_strings():
    dt = rtc.datetime()  # Get the current datetime tuple from the RTC
    # Format the date string (Year-Month-Day)
    date_string = "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])
    # Format the time string (Hour:Minute:Second)
    time_string = "{:02}:{:02}:{:02}".format(dt[4], dt[5], dt[6])
    return date_string, time_string
    
passwd_hash = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab"  

def fetch_outdoor_weather():
    url = 'https://flaskapp-vukguwbvha-oa.a.run.app/get_outdoor_weather'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash}, headers=headers)
    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print("Failed to fetch weather data: ", response.status_code)
        return None
        
def fetch_forecast():
    url = 'https://flaskapp-vukguwbvha-oa.a.run.app/get_daily_forecast'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash, "city": {"lat": 46.5196535, "lon": 6.6322734}}, headers=headers) #lausanne
    if response.status_code == 200:
        forecast_data = response.json()
        return forecast_data
    else:
        print("Failed to fetch forecast data: ", response.status_code)
        return None
        
forecast_label = M5Label('', x=90, y=90, color=0x000, font=FONT_MONT_14, parent=None)  # Adjust x, y for centering

# Initialize a list to keep track of forecast UI elements
forecast_ui_elements = []

def clear_forecast_display():
    global forecast_ui_elements
    # Iterate through the list of UI elements and remove each from the screen
    for element in forecast_ui_elements:
        element.delete()
    # Clear the list once all elements are removed
    forecast_ui_elements.clear()

def update_forecast_display():
    global forecast_ui_elements
    # Clear existing forecast display before updating
    clear_forecast_display()
    
    forecast_data = fetch_forecast()
    if forecast_data:
        start_x = 20
        y = 55
        x_offset = 60

        for i, day_forecast in enumerate(forecast_data[:5]):
            year, month, day = map(int, day_forecast['date'].split('-'))
            if month < 3:
                month += 12
                year -= 1
            weekday_num = (day + (13 * (month + 1)) // 5 + year + year // 4 - year // 100 + year // 400) % 7
            weekdays = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
            weekday_name = weekdays[weekday_num]

            current_x = start_x + i * x_offset

            # Create and store labels for the forecast
            day_label = M5Label(weekday_name, x=current_x, y=y, color=0x000, font=FONT_MONT_10, parent=None)
            temp_label_text = "{}°C / {}°C".format(int(round(float(day_forecast['min_temperature']))), int(round(float(day_forecast['max_temperature']))))
            temp_label = M5Label(temp_label_text, x=current_x, y=y + 20, color=0x000, font=FONT_MONT_10, parent=None)
            icon_file = 'res/{}.png'.format(day_forecast['icon'])
            icon = M5Img(icon_file, x=current_x, y=y + 40, parent=None)

            # Add the created elements to the list
            forecast_ui_elements.extend([day_label, temp_label, icon])
    else:
        no_data_label = M5Label("No forecast data available", x=20, y=30, color=0x000, font=FONT_MONT_10, parent=None)
        forecast_ui_elements.append(no_data_label)




# Display labels for date, time, temperature, and humidity
date_label = M5Label('Date', x=19, y=20, color=0x000, font=FONT_MONT_18, parent=None)
time_label = M5Label('Time', x=230, y=20, color=0x000, font=FONT_MONT_18, parent=None)
temperature_icon = M5Img('res/icons8-temperature-32.png', x=19, y=155, parent=None)
humidity_icon = M5Img('res/icons8-humidity-32.png', x=19, y=200, parent=None)
inlabel = M5Label('In', x=76, y=147, color=0x000, font=FONT_MONT_10, parent=None)
outlabel = M5Label('Out', x=151, y=147, color=0x000, font=FONT_MONT_10, parent=None)
label0 = M5Label('T', x=63, y=162, color=0x000, font=FONT_MONT_22, parent=None)
label1 = M5Label('H', x=63, y=203, color=0x000, font=FONT_MONT_22, parent=None)
label2 = M5Label('OT', x=143, y=162, color=0x000, font=FONT_MONT_22, parent=None)
label3 = M5Label('OH', x=143, y=203, color=0x000, font=FONT_MONT_22, parent=None)
# Display labels for air quality data
air_quality_icon = M5Img('res/icons8-air-16.png', x=200, y=168, parent=None)
tvoc_label = M5Label('TVOC: 0 ppb', x=230, y=166, color=0x000, font=FONT_MONT_10, parent=None)
eco2_label = M5Label('eCO2: 0 ppm', x=230, y=186, color=0x000, font=FONT_MONT_10, parent=None)
# Label for displaying greeting
greeting_label = M5Label('', x=230, y=213, color=0x000, font=FONT_MONT_10, parent=None)


passwd = "vendgelanonoarnaknonoob"
h = hashlib.sha256(passwd.encode('utf-8'))
passwd_hash = binascii.hexlify(h.digest()).decode('utf-8')

outdoor_weather_flag = 600  # Fetch outdoor weather every 10 minutes

while True:
    date_string, time_string = get_datetime_strings()
    update_air_quality()
    check_motion()
    if outdoor_weather_flag >= 600:
        outdoor_weather = fetch_outdoor_weather()
        update_forecast_display()
        if outdoor_weather:
            description = outdoor_weather['outdoor_weather']
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
                "indoor_humidity": round(env3_0.humidity),
                "indoor_tvoc": tvoc0.TVOC,
                "indoor_eco2": tvoc0.eCO2
            }
        }
        urequests.post("https://flaskapp-vukguwbvha-oa.a.run.app/send-to-bigquery", json=data)
        temp_flag = 0
    temp_flag += 1
    wait_ms(1000)  # wait for one second, then increase the wait time calculation

