import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sqlite3
import os.path
import datetime
import subprocess, sys

def rotateMotor(rotations): 
    for i in range(512 * rotations):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(step_motor_control_pins[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.001)

def readBrightness():
    p = subprocess.Popen("./tsl_read",shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    o, e = p.communicate()
    return float(o.decode('ascii'))
    
#setup
GPIO.setmode(GPIO.BOARD)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "measurementData.db")
conn = sqlite3.connect(db_path)
curs = conn.cursor()

#Variable declarations
step_motor_control_pins = [7,11,13,15]
CO2_sensor_pin = 40
temperature_sensor = Adafruit_DHT.AM2302
#Adafruit uses GPIO pin numbers
temperature_pin = 2

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

for pin in step_motor_control_pins:
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, 0)

#Routine
humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor, temperature_pin)

if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
    
    curs.execute("insert into test values((?), (?), (?))", (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), round(temperature,2), round(humidity,2)))
    conn.commit()
else:
    print('Failed to get reading. Try again!')

if GPIO.input(40):
    print("Sensor is active")
else:
    print("Sensor is inactive")
print("The brightness is:",readBrightness())
rotateMotor(2)

GPIO.cleanup()

