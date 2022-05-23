import time
import RPi.GPIO as GPIO

class Robot:
    pass

class Joint:
    def __init__(self, driver, sensor, gear_teeth, min_pos, max_pos, offset=0, homing_direction="ANTICLOCKWISE"):
        self.driver = driver
        self.sensor = sensor

        self.position = None
        self.min_pos = min_pos
        self.max_pos = max_pos

        self.gear_teeth = gear_teeth

        self.direction = homing_direction
        self.offset = offset

    def set_angle(self, pos):
        if self.position is not None:
            if self.min_pos <= pos < self.max_pos:
                new_pos = self.position - pos - self.offset


                if self.direction == 'ANTICLOCKWISE':
                    if new_pos >= 0:
                        direction = GPIO.HIGH  # Anticlockwise

                    else:
                        direction = GPIO.LOW  # Clockwise
                else:
                    if new_pos >= 0:
                        direction = GPIO.LOW  # Anticlockwise

                    else:
                        direction = GPIO.HIGH  # Clockwise

                new_pos = abs(new_pos)
                steps = ((new_pos/self.driver.motor_resolution)/(self.driver.gear_teeth/self.gear_teeth))*self.driver.driver_resolution
                print("Steps: ", steps)
                self.driver.move_steps(int(steps), direction, accel=0.005)

                self.position = pos - self.offset
                print("New position", self.position)


    def home(self):
        if self.direction == 'ANTICLOCKWISE':
            direction = GPIO.HIGH
            direction2 = GPIO.LOW
        else:
            direction = GPIO.LOW
            direction2 = GPIO.HIGH

        while True:
            self.driver.move_steps(8, direction, accel=0.05)

            if self.sensor.check_sensor():
                self.driver.move_steps(200, direction2, accel=0.001)
                while True:
                    self.driver.move_steps(4, direction, accel=0.01)

                    if self.sensor.check_sensor():
                        break
                break

        self.position = 0
        self.position += self.offset


class EndStop:
    def __init__(self, SIGNAL_PIN, type='up'):
        self._SIGNAL_PIN = SIGNAL_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._SIGNAL_PIN, GPIO.OUT)
        self.type = type

    def check_sensor(self):
        channel = GPIO.input(self._SIGNAL_PIN)

        if self.type == 'up':
            # Endstop inactive"
            if channel == 1:
                return False

            # Enstop active
            if channel == 0:
                return True

        elif self.type == 'down':
            # Endstop inactive"
            if channel == 0:
                return False

            # Enstop active
            if channel == 1:
                return True


