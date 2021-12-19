import time
import RPi.GPIO as GPIO

class Robot:
    pass

class Joint:
    def __init__(self, driver, sensor):
        self.driver = driver
        self.sensor = sensor

        self.position = None

    def home(self):
        while True:
            self.driver.move_to_pos(1, GPIO.LOW, accel=0.01)

            if self.sensor.check_sensor():
                break

        self.position = 0

class EndStop:
    def __init__(self, SIGNAL_PIN):
        self._SIGNAL_PIN = SIGNAL_PIN
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._SIGNAL_PIN, GPIO.OUT)

    def check_sensor(self):
        channel = GPIO.input(self._SIGNAL_PIN)

        #Endstop inactive"
        if channel == 1:
            return False

        #Enstop active
        if channel == 0:
            return True


