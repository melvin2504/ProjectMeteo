from m5stack import *
from m5stack_ui import *
from uiflow import *
import gc
import time
import unit
import urequests
import network

# Initialize the screen and units
screen = M5Screen()
screen.clean_screen()
screen.set_screen_bg_color(0xd5d5d5)
env3_0 = unit.get(unit.ENV3, unit.PORTA)
motion_sensor = unit.get(unit.PIR, unit.PORTB)
tvoc0 = unit.get(unit.TVOC, unit.PORTC)

# Wi-Fi credentials (default)
SSID2 = "iot-unil"
PASSWORD2 = "4u6uch4hpY9pJ2f9"
SSID1 = "Galaxy S20 FE 5GDEE0"
PASSWORD1 = "........"


# Constants for Wi-Fi connection attempts
MAX_RETRIES = 10
DELAY = 2  # Delay between attempts in seconds

# Global variables for connection state and UI initialization
wifi_connecting = False
wifi_retry = False
ui_initialized = False
connection_attempts = 0
next_connection_attempt = 0

# Initialize variables and constants
temp_flag = 300
last_motion_time = 0
motion_cooldown = 300  # 5 minutes in seconds
outdoor_weather_flag = 600  # Fetch outdoor weather every 10 minutes

# Define thresholds for alerts
LOW_HUMIDITY_THRESHOLD = 30  # Low humidity threshold (30%)
HIGH_HUMIDITY_THRESHOLD = 70  # High humidity threshold (70%)
POOR_AIR_QUALITY_THRESHOLD = 1000  # Poor air quality threshold (1000 ppb TVOC)
ELEVATED_ECO2_THRESHOLD = 1000  # Elevated eCO2 threshold (1000 ppm)

# Initialize labels
alert_message = None

# Password hash (example hash)
passwd_hash = "8eac4757d3804403cb4bbd4015df9d2ad252a1e6890605bacb19e5a01a5f2cab"



# Function to check for motion and fetch advice if motion is detected
def check_motion():
    global last_motion_time
    current_time = time.time()
    if (motion_sensor.state == 1 and (current_time - last_motion_time > motion_cooldown)) or btnA.isPressed():
        fetch_and_play_advice()
        last_motion_time = current_time  # Update the last motion time

# Function to update air quality and check for alerts
def update_air_quality():
    tvoc = tvoc0.TVOC
    eco2 = tvoc0.eCO2
    tvoc_label.set_text('TVOC: {} ppb'.format(tvoc))
    eco2_label.set_text('eCO2: {} ppm'.format(eco2))
    
    # Check for low/high humidity, poor air quality, or elevated eCO2
    if env3_0.humidity < LOW_HUMIDITY_THRESHOLD:
        play_alert("ALERT: Low humidity")
    elif env3_0.humidity > HIGH_HUMIDITY_THRESHOLD:
        play_alert("ALERT: High humidity")
    elif tvoc > POOR_AIR_QUALITY_THRESHOLD:
        play_alert("ALERT: Poor air quality")
    elif eco2 > ELEVATED_ECO2_THRESHOLD:
        play_alert("ALERT: Elevated eCO2")
    else:
        alert_message.set_text("")

# Function to play alert sound and display message
def play_alert(message):
    speaker.playWAV('res/ding.wav', volume=20)
    alert_message.set_text(message)

# Function to get the current date and time as strings
def get_datetime_strings():
    dt = rtc.datetime()  # Get the current datetime tuple from the RTC
    date_string = "{:04d}-{:02d}-{:02d}".format(dt[0], dt[1], dt[2])  # Format the date string (Year-Month-Day)
    time_string = "{:02}:{:02}:{:02}".format(dt[4], dt[5], dt[6])  # Format the time string (Hour:Minute:Second)
    return date_string, time_string

# Function to fetch outdoor weather data
def fetch_outdoor_weather():
    url = 'https://flaskapp5-vukguwbvha-oa.a.run.app/get_outdoor_weather'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch weather data: ", response.status_code)
        return None

# Function to fetch and play advice based on outdoor weather
def fetch_and_play_advice():
    outdoor_weather = fetch_outdoor_weather()
    if outdoor_weather:
        url = 'https://flaskapp5-vukguwbvha-oa.a.run.app/generate_advice_audio'
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(url, json=outdoor_weather, headers=headers)
        if response.status_code == 200:
            with open('res/advice.wav', 'wb') as f:
                f.write(response.content)
            speaker.playWAV('res/advice.wav', volume=20)
        else:
            print("Failed to fetch advice audio: ", response.status_code)

# Function to fetch forecast data
def fetch_forecast():
    url = 'https://flaskapp5-vukguwbvha-oa.a.run.app/get_daily_forecast'
    headers = {'Content-Type': 'application/json'}
    response = urequests.post(url, json={"passwd": passwd_hash, "city": {"lat": 46.5196535, "lon": 6.6322734}}, headers=headers)  # Lausanne
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch forecast data: ", response.status_code)
        return None

# Initialize a list to keep track of forecast UI elements
forecast_ui_elements = []

# Function to clear the forecast display
def clear_forecast_display():
    global forecast_ui_elements
    for element in forecast_ui_elements:
        element.delete()  # Remove each element from the screen
    forecast_ui_elements.clear()  # Clear the list once all elements are removed

# Function to update the forecast display
def update_forecast_display():
    global forecast_ui_elements
    clear_forecast_display()  # Clear existing forecast display before updating
    
    forecast_data = fetch_forecast()
    if (forecast_data is not None) and (len(forecast_data) > 0):
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


def fetch_and_display_graph():
    url = 'https://flaskapp6-vukguwbvha-oa.a.run.app/historical_data_graph'
    headers = {'Content-Type': 'application/json'}
    graph_file_path = 'res/graph.png'
    
    try:
        # Fetch the graph image from the server
        response = urequests.post(url, json={"passwd": passwd_hash}, headers=headers)
        if response.status_code == 200:
            with open(graph_file_path, 'wb') as f:
                f.write(response.content)
            
            # Ensure the file was written correctly
            file_size = os.stat(graph_file_path)[6]
            if file_size != len(response.content):
                alert_message.set_text("File size mismatch: expected {}, got {}".format(len(response.content) + str(file_size)))
                return
            
            # Clean the screen before displaying the image
            screen.clean_screen()
            
            # Perform garbage collection before displaying the image
            gc.collect()
            free_heap = gc.mem_free()
            alert_message.set_text("Free heap memory before displaying image: " + str(free_heap))
            
            # Display the graph image
            M5Img(graph_file_path, x=0, y=0, parent=None)
            
            # Check free heap memory after displaying the image
            gc.collect()
            free_heap = gc.mem_free()
            alert_message.set_text("Free heap memory after displaying image: " + str(free_heap))
        else:
            alert_message.set_text("Failed to fetch graph image: " + str(response.status_code))
    except Exception as e:
        alert_message.set_text("Exception in fetch_and_display_graph: " + str(e))
    
    # Small delay to allow the system to process
    time.sleep(0.1)

# Function to initialize the main screen UI
def init_main_screen():
    screen.clean_screen()
    gc.collect()
    free_heap = gc.mem_free()
    global state, ui_initialized
    ui_initialized = True
    # Re-create the main screen UI elements
    global date_label, time_label, temperature_icon, humidity_icon
    global inlabel, outlabel, label0, label1, label2, label3
    global air_quality_icon, tvoc_label, eco2_label, alert_message
    
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
    
    air_quality_icon = M5Img('res/icons8-air-16.png', x=200, y=168, parent=None)
    tvoc_label = M5Label('TVOC: 0 ppb', x=230, y=166, color=0x000, font=FONT_MONT_10, parent=None)
    eco2_label = M5Label('eCO2: 0 ppm', x=230, y=186, color=0x000, font=FONT_MONT_10, parent=None)
    
    alert_message = M5Label(' Hello !', x=200, y=213, color=0xff0000, font=FONT_MONT_10, parent=None)
    
    # Set up the RTC to sync time via NTP
    rtc.settime('ntp', host='ch.pool.ntp.org', tzone=2)  # Adjust the time zone parameter as needed
    
    update_forecast_display()


def connect_wifi():
    """Connects to WiFi with retry logic."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    attempts = 0

    # Create a label for connection status
    connection_label = M5Label('', x=19, y=42, color=0xff0000, font=FONT_MONT_10, parent=None)

    # Try connecting to the first network
    while not wlan.isconnected() and attempts < MAX_RETRIES:
        connection_label.set_text('Connecting to {}... Attempt {}'.format(SSID1, attempts + 1))
        wlan.connect(SSID1, PASSWORD1)
        time.sleep(DELAY)
        attempts += 1

    # If not connected, try connecting to the second network
    if not wlan.isconnected():
        attempts = 0  # Reset attempts for the second network
        while not wlan.isconnected() and attempts < MAX_RETRIES:
            connection_label.set_text('Connecting to {}... Attempt {}'.format(SSID2, attempts + 1))
            wlan.connect(SSID2, PASSWORD2)
            time.sleep(DELAY)
            attempts += 1

    if wlan.isconnected():
        connection_label.set_text('')
        return True
    else:
        connection_label.set_text('Connection failed after {} attempts.'.format(MAX_RETRIES))
        return False

# Function to check Wi-Fi connection and reconnect if necessary
def check_wifi_connection():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        global wifi_retry
        wifi_retry = True

# Connect to Wi-Fi initially
wifi_retry = True

while True:
    if wifi_retry:
        connect_wifi()
        wifi_retry = False
    
    if wifi_connecting:
        connect_wifi()
    
    check_wifi_connection()  # Check Wi-Fi connection periodically

    if not wifi_connecting and wifi_retry:
        connect_wifi()
        
    # Initialize the main UI if not already initialized
    if not ui_initialized:
        init_main_screen()
    
    # Update date and time labels
    date_string, time_string = get_datetime_strings()
    date_label.set_text(date_string)
    time_label.set_text(time_string)
    
    # Update indoor temperature and humidity labels
    label0.set_text(str(round(env3_0.temperature)) + "°C")
    label1.set_text(str(round(env3_0.humidity)) + "%")
    
    # Update air quality data
    update_air_quality()
    
    # Fetch outdoor weather and update forecast display every 10 minutes
    if outdoor_weather_flag >= 600:
        outdoor_weather = fetch_outdoor_weather()
        update_forecast_display()
        if outdoor_weather:
            label2.set_text(str(round(outdoor_weather['outdoor_temp'])) + "°C")
            label3.set_text(str(round(outdoor_weather['outdoor_humidity'])) + "%")
        outdoor_weather_flag = 0  # Reset the counter

    outdoor_weather_flag += 1
    
    # Send data to BigQuery every 5 minutes
    if temp_flag >= 300:
        #date_string, time_string = get_datetime_strings()
        data = {
            "passwd": passwd_hash,
            "values": {
                #"date": date_string,
                #"time": time_string,
                "indoor_temp": round(env3_0.temperature),
                "indoor_humidity": round(env3_0.humidity),
                "indoor_tvoc": tvoc0.TVOC,
                "indoor_eco2": tvoc0.eCO2
            }
        }
        urequests.post("https://flaskapp5-vukguwbvha-oa.a.run.app/send-to-bigquery", json=data)
        temp_flag = 0  # Reset the counter
    
    temp_flag += 1
    
    # Check for motion and fetch advice if necessary
    check_motion()
    free_heap = gc.mem_free()
        # Show the graph image when button B is pressed
    if btnB.isPressed():
        fetch_and_display_graph()
        
        # Return to the main screen when button C is pressed
    if btnC.isPressed():
        init_main_screen()
    wait_ms(1000)




