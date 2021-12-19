import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)


DIG = 6
GPIO.setup(DIG, GPIO.OUT)



while True:
    channel = GPIO.input(DIG)
    print(channel)
    time.sleep(0.01)





