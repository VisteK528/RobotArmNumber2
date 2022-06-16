import pigpio
import time
import RPi.GPIO as GPIO

# Pi GPIO initialization
pi = pigpio.pi()

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

class Servo:
    def degrees_to_miliseconds(self, degrees):
        value = round((11.111111 * degrees) + 500)
        return value
    def move_servo(self, servo_pin, position):
        value = self.degrees_to_miliseconds(position)
        pi.set_servo_pulsewidth(servo_pin, value)
        time.sleep(0.1)


servo = Servo()
while True:
    angle = int(input("Podaj kąt: "))
    servo.move_servo(2, angle)
    time.sleep(2)