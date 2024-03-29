import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sqlite3
import os.path
from datetime import datetime, timedelta
import subprocess, sys

#TODO database initialization script

humidityThreshold = 60
brightnessThreshold = 200

updateTemperatureHumidityStatus = True
updateBrightnessStatus = True
temperatureHumidityStatus = "Working"
brightnessStatus = "Working"

def rotateMotor(rotations, direction):
    if(direction == "clockwise"):
        modifier = 1
    elif(direction == "counterclockwise"):
        modifier = -1
    else:
        print("Invalid direction! Must be 'clockwise' or 'counterclockwise'")
        return
    for i in range(512 * rotations):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(step_motor_control_pins[pin], halfstep_seq[modifier * halfstep][pin])
            time.sleep(0.001)

def readBrightness():
    global brightnessStatus
    global updateBrightnessStatus
    try:
        p = subprocess.Popen("./tsl_read",shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        o, e = p.communicate()
        brightness=float(o.decode('ascii'))*6.83
        if brightnessStatus == "Not working":
            brightnessStatus = "Working"
            updateBrightnessStatus = True
        if updateBrightnessStatus:
            query = "UPDATE brightness_Sensor SET status = '" + brightnessStatus + "' where id = 1"
            curs.execute(query)
            conn.commit()
            updateBrightnessStatus = False
    except:
        print("Brightness sensor not working")
        brightness = 0
        if brightnessStatus == "Working":
            brightnessStatus = "Not working"
            updateBrightnessStatus = True
        if updateBrightnessStatus:
            query = "UPDATE brightness_Sensor SET status = '" + brightnessStatus + "' where id = 1"
            curs.execute(query)
            conn.commit()
            updateBrightnessStatus = False
    return brightness

def write15minValues():
    global temperatureHumidityStatus
    global updateTemperatureHumidityStatus
    humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor, temperature_pin)
    brightness = readBrightness()
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}% Brightness={2:0.1f}Lux '.format(temperature, humidity,brightness))
        print('Temperature and humidity sensor working')
        if temperatureHumidityStatus == "Not working":
            temperatureHumidityStatus = "Working"
            updateTemperatureHumidityStatus = True
        if updateTemperatureHumidityStatus:
            query = "UPDATE temperature_Humidity_Sensor SET status = '" + temperatureHumidityStatus + "' where id = 1"
            curs.execute(query)
            conn.commit()
            updateTemperatureHumidityStatus = False
            
        if(brightness == 0):
            brightness = "NULL"
        curs.execute("insert into Values_15min values((?), (?), (?),(?), (?))", (datetime.now().strftime("%d/%m/%Y"),datetime.now().strftime("%H:%M:%S"),  round(temperature,2), round(humidity,2),brightness))
        conn.commit()
        if(humidity < humidityThreshold):
            GPIO.output(humidifier_pin, GPIO.HIGH)
        else:
            GPIO.output(humidifier_pin, GPIO.LOW)
        if(brightness != "NULL"):
            if(brightness < brightnessThreshold):
                GPIO.output(light_pin, GPIO.HIGH)
                rotateMotor(2, "clockwise")
            else:
                GPIO.output(light_pin, GPIO.LOW)
                rotateMotor(2, "counterclockwise")
        if temperatureHumidityStatus == "Not working":
            temperatureHumidityStatus = "Working"
            updateTemperatureHumidityStatus = True
        
    else:
        print('Temperature and humidity sensor not working')
        if temperatureHumidityStatus == "Working":
            temperatureHumidityStatus = "Not working"
            updateTemperatureHumidityStatus = True
        if updateTemperatureHumidityStatus:
            query = "UPDATE temperature_Humidity_Sensor SET status = '" + temperatureHumidityStatus + "' where id = 1"
            curs.execute(query)
            conn.commit()
            updateTemperatureHumidityStatus = False

def writeValuesDay():
    d=datetime.now() - timedelta(days=1)
    curs.execute("SELECT AVG(V.Temperature),AVG(V.Humidity),AVG(V.Brightness) FROM Values_15min V Where Date=(?)", (d.strftime("%d/%m/%Y"),))
    row = curs.fetchall()[0] 
    curs.execute("insert into Values_Day values((?), (?),(?), (?))", (d.strftime("%d/%m/%Y"), row[0], row[1] ,row[2]))
    conn.commit()
    
def routine():
    global humidityThreshold
    global brightnessThreshold
    
    while(True):
        write15minValues()
        if not GPIO.input(CO2_sensor_pin):
            print("Fire Alarm!")
            GPIO.output(buzzer_pin, GPIO.HIGH)
        else:
            GPIO.output(buzzer_pin, GPIO.LOW)
        if datetime.now().second<15 and (datetime.now().minute==0  or datetime.now().minute==15 or datetime.now().minute==30 or datetime.now().minute==45) :
            write15minValues()
            if datetime.now().hour==0 and datetime.now().minute==0:
                writeValuesDay()
        curs.execute("select * from humidity_Threshold where id = 1")
        humidityThreshold = curs.fetchone()
        humidityThreshold = humidityThreshold[1]
        curs.execute("select * from brightness_Threshold where id = 1")
        brightnessThreshold = curs.fetchone()
        brightnessThreshold = brightnessThreshold[1]
        time.sleep(15)
    
#setup
GPIO.setmode(GPIO.BOARD)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "measurementData.db")
conn = sqlite3.connect(db_path)
curs = conn.cursor()

#Variable declarations
CO2_sensor_pin = 40
temperature_sensor = Adafruit_DHT.AM2302
temperature_pin = 2 #Adafruit uses GPIO pin numbers
brightness_pin = 22
buzzer_pin = 21
light_pin = 23
humidifier_pin = 24

step_motor_control_pins = [7,11,13,15]
halfstep_seq = [
  [1,0,0,0],
  [1,1,0,0],
  [0,1,0,0],
  [0,1,1,0],
  [0,0,1,0],
  [0,0,1,1],
  [0,0,0,1],
  [1,0,0,1]
]

#GPIO setup
GPIO.setup(CO2_sensor_pin, GPIO.IN)
GPIO.setup(brightness_pin, GPIO.IN)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.output(buzzer_pin, 0)
GPIO.setup(light_pin, GPIO.OUT)
GPIO.output(light_pin, 0)
GPIO.setup(humidifier_pin, GPIO.OUT)
GPIO.output(humidifier_pin, 0)

for pin in step_motor_control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

#Routine
print("Starting routine\n")
routine()

GPIO.cleanup()

