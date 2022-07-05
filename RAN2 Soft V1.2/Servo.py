import pigpio
import time

class Servo:
    def __init__(self, servo_pin):
        self._servo_pin = servo_pin
        self.pi = pigpio.pi()

    def degrees_to_miliseconds(self, degrees):
        value = round((11.111111 * degrees) + 500)
        return value

    def move_servo(self, position):
        value = self.degrees_to_miliseconds(position)
        self.pi.set_servo_pulsewidth(self._servo_pin, value)
        time.sleep(0.1)