import math
import RPi.GPIO as GPIO
import time


class TMC2209:
    def __init__(self, step, dir, en, resolution, gear_teeth):
        self._STEP = step
        self._DIR = dir
        self._EN = en
        if self._EN is not None:
            GPIO.setup(self._EN, GPIO.OUT)
            GPIO.output(self._EN, GPIO.LOW)

        GPIO.setup(self._DIR, GPIO.OUT)
        GPIO.setup(self._STEP, GPIO.OUT)

        GPIO.output(self._DIR, GPIO.LOW)

        #Variables
        self.motor_resolution = resolution
        self.driver_resolution = 8
        self.gear_teeth = gear_teeth

        self.max_speed = 1000
        self.max_acceleration = 0.05

    def set_max_speed(self, speed):
        self.max_speed = speed

    def set_max_acceleration(self, acceleration):
        self.max_acceleration = acceleration

    def disable(self):
        GPIO.output(self._EN, GPIO.HIGH)

    def enable(self):
        GPIO.output(self._EN, GPIO.LOW)

    def move_steps(self, steps, dir, accel=0.01):
        delays = []
        angle = 1
        high_speed = self.max_speed
        accel = accel
        c0 = 2000 * math.sqrt(2 * angle / accel) * 0.67703

        if steps % 2 == 0:
            for i in range(int(steps / 2)):
                d = c0
                if i > 0:
                    d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

                # print('D: ', d, ' ', 'High speed: ', high_speed)
                if d < high_speed:
                    # print('here')
                    d = high_speed
                delays.append(d)

            delays_buff = delays.copy()
            delays_buff.reverse()

            for x in delays_buff:
                delays.append(x)

            delays2 = [delay / 1000000 for delay in delays]

        else:
            for i in range(int(steps / 2) + 1):
                d = c0
                if i > 0:
                    d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

                if d < high_speed:
                    d = high_speed
                delays.append(d)

            delays_buff = delays.copy()
            delays_buff.pop()
            delays_buff.reverse()

            for x in delays_buff:
                delays.append(x)

            delays2 = [delay / 1000000 for delay in delays]

        GPIO.output(self._DIR, dir)
        for delay in delays2:
            GPIO.output(self._STEP, GPIO.LOW)
            time.sleep(delay)
            GPIO.output(self._STEP, GPIO.HIGH)

    def set_direction(self, direction):
        GPIO.output(self._DIR, direction)

    def move_del(self, delay):
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

class AN4988Driver:
    def __init__(self, step, dir, en, resolution, gear_teeth):
        self._STEP = step
        self._DIR = dir
        self._EN = en
        if self._EN is not None:
            GPIO.setup(self._EN, GPIO.OUT)
            GPIO.output(self._EN, GPIO.LOW)

        GPIO.setup(self._DIR, GPIO.OUT)
        GPIO.setup(self._STEP, GPIO.OUT)

        GPIO.output(self._DIR, GPIO.LOW)

        #Variables
        self.motor_resolution = resolution
        self.driver_resolution = 8
        self.gear_teeth = gear_teeth

        self.max_speed = 500
        self.max_acceleration = 0.05

    def set_max_speed(self, speed):
        self.max_speed = speed

    def set_max_acceleration(self, acceleration):
        self.max_acceleration = acceleration

    def disable(self):
        GPIO.output(self._EN, GPIO.HIGH)

    def enable(self):
        GPIO.output(self._EN, GPIO.LOW)

    def move_steps(self, steps, dir, accel=0.01):
        delays = []
        angle = 1
        high_speed = self.max_speed
        accel = accel
        c0 = 2000 * math.sqrt(2 * angle / accel) * 0.67703

        if steps % 2 == 0:
            for i in range(int(steps / 2)):
                d = c0
                if i > 0:
                    d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

                # print('D: ', d, ' ', 'High speed: ', high_speed)
                if d < high_speed:
                    # print('here')
                    d = high_speed
                delays.append(d)

            delays_buff = delays.copy()
            delays_buff.reverse()

            for x in delays_buff:
                delays.append(x)

            delays2 = [delay / 1000000 for delay in delays]

        else:
            for i in range(int(steps / 2) + 1):
                d = c0
                if i > 0:
                    d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

                if d < high_speed:
                    d = high_speed
                delays.append(d)

            delays_buff = delays.copy()
            delays_buff.pop()
            delays_buff.reverse()

            for x in delays_buff:
                delays.append(x)

            delays2 = [delay / 1000000 for delay in delays]

        #self.enable()
        #GPIO.output(self._DIR, dir)
        for delay in delays2:
            GPIO.output(self._DIR, dir)
            GPIO.output(self._STEP, GPIO.LOW)
            time.sleep(delay)
            GPIO.output(self._STEP, GPIO.HIGH)
        GPIO.output(self._STEP, GPIO.LOW)
        #self.disable()

class DM556Driver:
    def __init__(self, DIR, PUL, driver_resolution, motor_resolution, gear_teeth):
        self._DIR = DIR
        self._PUL = PUL

        GPIO.setup(self._PUL, GPIO.OUT)
        GPIO.setup(self._DIR, GPIO.OUT)

        self.driver_resolution = driver_resolution
        self.motor_resolution = motor_resolution
        self.gear_teeth = gear_teeth

        self.max_speed = 2000
        self.max_acceleration = 0.05

    def set_max_speed(self, speed):
        self.max_speed = speed

    def set_max_acceleration(self, acceleration):
        self.max_acceleration = acceleration

    def set_direction(self, direction):
        GPIO.output(self._DIR, direction)

    def move_del(self, delay):
        GPIO.output(self._PUL, GPIO.LOW)
        time.sleep(delay)
        GPIO.output(self._PUL, GPIO.HIGH)

    def _sec_to_milisec(self, seconds):
        return seconds / 1000000

    def move_steps(self, steps, dir, accel=0.01):
        delays = []
        angle = 1
        high_speed = self.max_speed
        accel = accel
        c0 = 2000 * math.sqrt(2 * angle / accel) * 0.67703

        if steps % 2 == 0:
            loops = int(steps / 2)
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

        for x in final_delays:
            if dir == 0:
                GPIO.output(self._DIR, GPIO.LOW)
            elif dir == 1:
                GPIO.output(self._DIR, GPIO.HIGH)

            GPIO.output(self._PUL, GPIO.LOW)
            time.sleep(x)
            GPIO.output(self._PUL, GPIO.HIGH)

    def delayMicroseconds(self, n):
        time.sleep(n / 1000000)