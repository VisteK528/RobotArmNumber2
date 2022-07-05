import RPi.GPIO as GPIO
import time
from Endstop import EndStop


GPIO.setmode(GPIO.BCM)
stop = EndStop(SIGNAL_PIN=25, type='up')


while True:
    time.sleep(0.1)
    print(stop.check_sensor())