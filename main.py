import RPi.GPIO as GPIO
import time

EN = 21
DIR = 16
STEP = 20
term = 0.1


GPIO.setmode(GPIO.BCM)

GPIO.setup(EN, GPIO.OUT)
GPIO.output(EN, GPIO.LOW)

GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

GPIO.output(DIR, GPIO.LOW)

"""steps = 0
while True:
    GPIO.output(STEP, GPIO.LOW)
    time.sleep(term/1000)
    GPIO.output(STEP, GPIO.HIGH)
    time.sleep(term / 1000)
    steps+= 1
    print(steps)"""

def rotation(part, term, dir, steps=20200, disable=False):

    if dir == 'CLOCKWISE':
        GPIO.output(DIR, GPIO.HIGH)
    elif dir == "ANTICLOCKWISE":
        GPIO.output(DIR, GPIO.LOW)
    else:
        return

    for i in range(int(steps*part)):
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(term / 1000)
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(term / 1000)
        print(i)

    if disable:
        GPIO.output(EN, GPIO.HIGH)

rotation(1, term=0.4, dir="CLOCKWISE", steps=1600, disable=True)