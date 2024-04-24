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

# Display labels for date, time, temperature, and humidity
date_label = M5Label('Date', x=19, y=40, color=0x000, font=FONT_MONT_18, parent=None)
time_label = M5Label('Time:', x=19, y=80, color=0x000, font=FONT_MONT_18, parent=None)
Temp = M5Label('Temp:', x=19, y=142, color=0x000, font=FONT_MONT_22, parent=None)
Humidity = M5Label('Humidity:', x=19, y=183, color=0x000, font=FONT_MONT_22, parent=None)
label0 = M5Label('T', x=163, y=142, color=0x000, font=FONT_MONT_22, parent=None)
label1 = M5Label('H', x=158, y=183, color=0x000, font=FONT_MONT_22, parent=None)

passwd = "vendgelanonoarnaknonoob"
h = hashlib.sha256(passwd.encode('utf-8'))
passwd_hash = binascii.hexlify(h.digest()).decode('utf-8')

while True:
    date_string, time_string = get_datetime_strings()
    date_label.set_text('Date: ' + date_string)
    time_label.set_text('Time: ' + time_string)
    label0.set_text(str(round(env3_0.temperature)))
    label1.set_text(str(round(env3_0.humidity)) + " %")

    # Send data every 5 minutes
    if temp_flag >= 300:
        data = {
            "passwd": passwd_hash,
            "values": {
                "time": time_str,
                "indoor_temp": round(env3_0.temperature),
                "indoor_humidity": round(env3_0.humidity)
            }
        }
        urequests.post("https://flaskapp-vukguwbvha-oa.a.run.app/send-to-bigquery", json=data)
        temp_flag = 0
    temp_flag += 1
    wait_ms(1000)  # wait for one second, then increase the wait time calculation






