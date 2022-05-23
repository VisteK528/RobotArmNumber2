from robot import Joint, EndStop
from tmc2209_driver import TMC2209, DM556Driver
import RPi.GPIO as GPIO
from usb_control import DriverSerialControl
from algorithm import Algorithm
import time
import threading as th
import socket
import pigpio

# Pi GPIO initialization
pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)

# Shoulder 20:124 -> 200 steps per revolution, ~9925.55 steps per one shoulder revolution
waist_driver = TMC2209(en=26, dir=13, step=19, resolution=0.9, gear_teeth=20)
waist_endstop = EndStop(SIGNAL_PIN=12, type='up')
waist_joint = Joint(driver=waist_driver, sensor=waist_endstop, min_pos=-1, max_pos=358, gear_teeth=125,
                    homing_direction='ANTICLOCKWISE')

# driver = DriverSerialControl(port="/dev/ttyACM0", baudrate=115200, resolution=1.8, gear_teeth=20)
shoulder_driver = DM556Driver(DIR=15, PUL=14, driver_resolution=46.6667, motor_resolution=1.8, gear_teeth=20)
shoulder_endstop = EndStop(SIGNAL_PIN=6, type='up')
shoulder_joint = Joint(shoulder_driver, shoulder_endstop, gear_teeth=149, min_pos=0, max_pos=181, homing_direction='CLOCKWISE')

elbow_driver = TMC2209(en=18, dir=8, step=7, resolution=0.9, gear_teeth=20)
elbow_endstop = EndStop(SIGNAL_PIN=23, type='down')
elbow_joint = Joint(driver=elbow_driver, sensor=elbow_endstop, gear_teeth=62, min_pos=0, max_pos=70,
                    homing_direction='ANTICLOCKWISE')

wrist_roll_driver = TMC2209(en=21, dir=16, step=20, resolution=1.8, gear_teeth=1)
wrist_roll_driver.set_max_speed(4000)
wrist_roll_endstop = EndStop(SIGNAL_PIN=24, type="up")
wrist_roll_joint = Joint(driver=wrist_roll_driver, sensor=wrist_roll_endstop, min_pos=0, max_pos=270, gear_teeth=1,
                         homing_direction='CLOCKWISE')

wrist_pitch_driver = TMC2209(en=10, dir=9, step=11, resolution=1.8, gear_teeth=20)
wrist_pitch_driver.set_max_speed(4000)
wrist_pitch_endstop = EndStop(SIGNAL_PIN=25, type='up')
wrist_pitch_joint = Joint(driver=wrist_pitch_driver, sensor=wrist_pitch_endstop, min_pos=0, max_pos=250, gear_teeth=40,
                          homing_direction="ANTICLOCKWISE")


class Servo:
    def __init__(self, servo_pin):
        self._servo_pin = servo_pin

    def degrees_to_miliseconds(self, degrees):
        value = round((11.111111 * degrees) + 500)
        return value

    def move_servo(self, position):
        value = self.degrees_to_miliseconds(position)
        pi.set_servo_pulsewidth(self._servo_pin, value)
        time.sleep(0.1)


class Robot:
    def __init__(self, waist, shoulder, elbow, roll, pitch, effector):
        self.waist = waist
        self.shoulder = shoulder
        self.elbow = elbow
        self.roll = roll
        self.pitch = pitch
        self.effector = effector

        #Variables
        self._homed = None

    def home_all_joints(self):
        try:
            print('Homing all joints...')
            self.shoulder.position = 0
            self.shoulder.set_angle(10)
            print("Waist homing... ", end='')
            self.waist.home()
            print("Waist homed")
            self.waist.set_angle(60)
            print("Shoulder homing... ", end='')
            self.shoulder.home()
            self.shoulder.set_angle(17)  # Horizontally aligned
            self.shoulder.position = 0
            print("Shoulder homed")
            print("Elbow homing... ", end='')
            self.elbow.home()
            print("Elbow homed")
            print("Wrist Roll homing... ", end='')
            self.roll.home(offset=15)
            print("Wrist Roll homed")
            print("Wrist pitch homing... ", end='')
            self.pitch.home()
            print("Wrist pitch homed")
            print("All joints homed successfully!")

            self._homed = True
        except Exception as e:
            print(f"Homing failed due to error: {e}")


    def console(self):
        while True:
            motor = input('Podaj silnik: ')
            angle = input('Podaj kąt: ')
            if str(angle) == 'HOME':
                if motor == "WAIST":
                    self.waist.home()
                elif motor == "SHOULDER":
                    self.shoulder.home()
                elif motor == "ELBOW":
                    self.elbow.home()
                elif motor == "ROLL":
                    self.roll.home(offset=17)
                elif motor == "PITCH":
                    self.pitch.home()
            else:
                if motor == "WAIST":
                    self.waist.set_angle(float(angle))
                elif motor == "SHOULDER":
                    self.shoulder.set_angle(float(angle))
                elif motor == "ELBOW":
                    self.elbow.set_angle(float(angle))
                elif motor == "ROLL":
                    self.roll.set_angle(float(angle))
                elif motor == "PITCH":
                    self.pitch.set_angle(float(angle))
                elif motor == "SERVO":
                    self.effector.move_servo(float(angle))
            time.sleep(2)

servo = Servo(servo_pin=2)
robot = Robot(waist=waist_joint, shoulder=shoulder_joint, elbow=elbow_joint, roll=wrist_roll_joint,
              pitch=wrist_pitch_joint, effector=servo)
robot.home_all_joints()
robot.console()



