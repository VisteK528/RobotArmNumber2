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

class DM556Driver:
    def __init__(self, DIR, PUL, driver_resolution, motor_resolution, gear_teeth):
        self._DIR = DIR
        self._PUL = PUL

        GPIO.setup(self._PUL, GPIO.OUT)
        GPIO.setup(self._DIR, GPIO.OUT)

        self.driver_resolution = driver_resolution
        self.motor_resolution = motor_resolution
        self.gear_teeth = gear_teeth

    def _sec_to_milisec(self, seconds):
        return seconds / 1000000

    def move_steps(self, steps, dir, high_speed=300, accel=0.01):
        delays = []
        angle = 1
        accel = accel
        c0 = 2000 * math.sqrt(2 * angle / accel) * 0.67703

        if steps % 2 == 0:
            loops = int(steps/2)
            even = True
        else:
            loops = int(steps / 2) + 1
            even = False

        for i in range(loops):
            d = c0
            if i > 0:
                d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

            if d < high_speed:
                d = high_speed

            delays.append(d)

        delays_buff = delays.copy()
        if not even:
            delays_buff.pop()
        delays_buff.reverse()

        for x in delays_buff:
            delays.append(x)

        final_delays = [self._sec_to_milisec(x) for x in delays]

        if dir == 0:
            GPIO.output(self._DIR, GPIO.LOW)
        elif dir == 1:
            GPIO.output(self._DIR, GPIO.HIGH)

        for x in final_delays:
            GPIO.output(self._PUL, GPIO.HIGH)
            self.delayMicroseconds(x)
            GPIO.output(self._PUL, GPIO.LOW)

    def move_step_old(self, steps, dir, accel=0.01):
        #print('Got steps:', steps)

        for i in range(steps):
            if dir == 0:
                GPIO.output(self._DIR, GPIO.LOW)
            elif dir == 1:
                GPIO.output(self._DIR, GPIO.HIGH)
            GPIO.output(self._PUL, GPIO.HIGH)
            self.delayMicroseconds(300)
            GPIO.output(self._PUL, GPIO.LOW)

    def delayMicroseconds(self, n):
        time.sleep(n / 1000000)




