import math
import RPi.GPIO as GPIO
import time

class TMC2209:
    def __init__(self, step, dir, en):
        self._STEP = step
        self._DIR = dir
        self._EN = en
        GPIO.setup(self._EN, GPIO.OUT)
        GPIO.output(self._EN, GPIO.LOW)

        GPIO.setup(self._DIR, GPIO.OUT)
        GPIO.setup(self._STEP, GPIO.OUT)

        GPIO.output(self._DIR, GPIO.LOW)

        #Variables
        self._max_speed = 10
        self._max_acceleration = 2000

    def set_max_speed(self, speed):
        self._max_speed = speed

    def set_max_acceleration(self, acceleration):
        self._max_acceleration = acceleration

    def disable(self):
        GPIO.output(self._EN, GPIO.HIGH)

    def enable(self):
        GPIO.output(self._EN, GPIO.LOW)

    def move_steps(self, steps, dir, accel=0.01):
        delays = []
        angle = 1
        accel = accel
        high_speed = 100
        c0 = 2000 * math.sqrt(2*angle/accel)*0.67703

        for i in range(steps):
            d = c0
            if i > 0:
                d = delays[i-1] - ((2*delays[i-1])/(4*i+1))

            if d < high_speed:
                d = high_speed
            delays.append(d)

        delays2 = [delay/1000000 for delay in delays]


        GPIO.output(self._DIR, dir)
        for delay in delays2:
            GPIO.output(self._STEP, GPIO.LOW)
            time.sleep(delay)
            GPIO.output(self._STEP, GPIO.HIGH)

    def constant_accel(self, steps, dir, accel=0.01):
        delays = []
        angle = 1
        accel = accel
        high_speed = 100
        c0 = 2000 * math.sqrt(2*angle/accel)*0.67703

        for i in range(steps):
            d = c0
            if i > 0:
                d = delays[i-1] - ((2*delays[i-1])/(4*i+1))

            if d < high_speed:
                d = high_speed
            delays.append(d)

        delays2 = [delay/1000000 for delay in delays]


        GPIO.output(self._DIR, dir)
        for delay in delays2:
            GPIO.output(self._STEP, GPIO.LOW)
            time.sleep(delay)
            GPIO.output(self._STEP, GPIO.HIGH)

        GPIO.output(self._DIR, GPIO.LOW)
        for delay in delays2:
            GPIO.output(self._STEP, GPIO.LOW)
            time.sleep(delay)
            GPIO.output(self._STEP, GPIO.HIGH)




