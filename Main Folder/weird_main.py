

class Robot:
    pass

class PositionAlgorithm:
    pass

class Joint:
    def __init__(self, driver, sensor, gear_teeth, min_pos, max_pos, offset=0, homing_direction="ANTICLOCKWISE"):

        # Joint Stepper Motor Driver
        self.driver = driver

        # Joint Position sensor, end limit switch
        self.sensor = sensor

        # Current Joint position, if not homed, position is None
        self.position = None

        # Range of movement of Joint in degrees
        self.min_pos = min_pos
        self.max_pos = max_pos

        self.gear_teeth = gear_teeth

        # Rotation direction ( CLOCKWISE OR ANTICLOCKWISE
        self.direction = homing_direction
        self.offset = offset

    def set_new_position(self, pos):
        # None homed safety check
        if self.position is not None:

            # Movement range check
            if self.min_pos <= pos < self.max_pos:
                diff = self.position - pos - self.offset

                if self.direction == 'ANTICLOCKWISE':
                    if diff >= 0:
                        direction = GPIO.HIGH  # Anticlockwise

                    else:
                        direction = GPIO.LOW  # Clockwise
                else:
                    if diff >= 0:
                        direction = GPIO.LOW  # Anticlockwise

                    else:
                        direction = GPIO.HIGH  # Clockwise

                new_pos = abs(diff)
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

class TMC2209:
    def __init__(self, EN_PIN, DIR_PIN, STEP_PIN, driver_resolution=8):
        self._EN_PIN = EN_PIN
        self._DIR_PIN = DIR_PIN
        self._STEP_PIN = STEP_PIN

        self.driver_resolution = driver_resolution

    def set_max_angular_velocity(self, angular_velocity):
        self._max_angular_velocity = angular_velocity

    def set_max_angular_acceleration(self, angular_acceleration):
        self._max_angular_acceleration = angular_acceleration

    def move_steps(self):
        pass


class AN4988:
    pass

class Movement:
    pass
