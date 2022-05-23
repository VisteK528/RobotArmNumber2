from robot import Joint, EndStop
from tmc2209_driver import TMC2209, DM556Driver, AN4988Driver
import RPi.GPIO as GPIO
import time
import pigpio
from RaspberryPi.pos_algorithm import PositionAlgorithm

# Pi GPIO initialization
pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)

# Shoulder 20:124 -> 200 steps per revolution, ~9925.55 steps per one shoulder revolution
waist_driver = TMC2209(en=26, dir=13, step=19, resolution=0.9, gear_teeth=20)
waist_endstop = EndStop(SIGNAL_PIN=12, type='up')
waist_joint = Joint(driver=waist_driver, sensor=waist_endstop, min_pos=-1, max_pos=358, gear_teeth=125, offset=60,
                    homing_direction='ANTICLOCKWISE')

# driver = DriverSerialControl(port="/dev/ttyACM0", baudrate=115200, resolution=1.8, gear_teeth=20)
shoulder_driver = DM556Driver(DIR=15, PUL=14, driver_resolution=46.6667, motor_resolution=1.8, gear_teeth=20)
shoulder_driver.set_max_speed(500)
shoulder_endstop = EndStop(SIGNAL_PIN=6, type='up')
shoulder_joint = Joint(shoulder_driver, shoulder_endstop, gear_teeth=149, min_pos=0, max_pos=181, offset=17,
                       homing_direction='CLOCKWISE')

elbow_driver = AN4988Driver(en=18, dir=5, step=7, resolution=0.9, gear_teeth=20)
elbow_driver.set_max_speed(1000)
elbow_endstop = EndStop(SIGNAL_PIN=23, type='down')
elbow_joint = Joint(driver=elbow_driver, sensor=elbow_endstop, gear_teeth=62, min_pos=0, max_pos=70, base_angle=50.3,
                    homing_direction='CLOCKWISE')

wrist_roll_driver = TMC2209(en=21, dir=16, step=20, resolution=1.8, gear_teeth=1)
wrist_roll_driver.set_max_speed(4000)
wrist_roll_endstop = EndStop(SIGNAL_PIN=24, type="up")
wrist_roll_joint = Joint(driver=wrist_roll_driver, sensor=wrist_roll_endstop, min_pos=0, max_pos=270, gear_teeth=1, offset=-22,
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

        # Variables
        self._homed = None

    def home_all_joints(self, waist=True, shoulder=True, elbow=True, roll=True, pitch=True):
        counter = 0
        try:
            print('Homing all joints...')
            #self.shoulder.position = 0
            #self.shoulder.set_angle(10)
            if waist:
                print("Waist homing... ", end='')
                self.waist.home()
                print("Waist homed")
                counter += 1
            if shoulder:
                print("Shoulder homing... ", end='')
                self.shoulder.home(multipicator=3)
                print("Shoulder homed")
                counter += 1
            if elbow:
                print("Elbow homing... ", end='')
                self.elbow.home()
                print("Elbow homed")
                counter += 1
            if roll:
                print("Wrist Roll homing... ", end='')
                self.roll.home()
                print("Wrist Roll homed")
                counter += 1
            if pitch:
                print("Wrist pitch homing... ", end='')
                self.pitch.home()
                print("Wrist pitch homed")
                counter += 1

            if counter == 5:
                print("All joints homed successfully!")
            else:
                print("Selected joints homed successfully!")

            self._homed = True
        except Exception as e:
            print(f"Homing failed due to error: {e}")

    def console(self, algorithm):
        while True:
            message = input("").lower().split()

            if message[0] == "position":
                x, y = float(message[1]), float(message[2])

                algorithm.calc_arm_pos_horizontally_adapted(x, y)

                time.sleep(0.5)
                self.shoulder.set_angle(algorithm.r_alfa)
                time.sleep(0.5)
                self.elbow.set_angle(algorithm.r_beta)
                time.sleep(0.5)
                self.pitch.set_angle(algorithm.r_theta)
                time.sleep(0.5)
            elif message[0] == "move":
                motor, angle = message[1], message[2]
                if str(angle) == 'home':
                    if motor == "waist":
                        self.waist.home()
                    elif motor == "shoulder":
                        self.shoulder.home()
                    elif motor == "elbow":
                        self.elbow.home()
                    elif motor == "roll":
                        self.roll.home()
                    elif motor == "pitch":
                        self.pitch.home()
                else:
                    if motor == "waist":
                        self.waist.set_angle(float(angle))
                    elif motor == "shoulder":
                        self.shoulder.set_angle(float(angle))
                    elif motor == "elbow":
                        self.elbow.set_angle(float(angle))
                    elif motor == "roll":
                        self.roll.set_angle(float(angle))
                    elif motor == "pitch":
                        self.pitch.set_angle(float(angle))
                    elif motor == "servo":
                        self.effector.move_servo(float(angle))
            time.sleep(2)

    def position(self, algorithm):
        while True:
            x, y = input("Podaj koordynaty: ").split()
            x, y = float(x), float(y)

            algorithm.calc_arm_pos_horizontally_adapted(x, y)

            time.sleep(0.5)
            self.shoulder.set_angle(algorithm.r_alfa)
            time.sleep(0.5)
            self.elbow.set_angle(algorithm.r_beta)
            time.sleep(0.5)
            self.pitch.set_angle(algorithm.r_theta)
            time.sleep(0.5)

algorithm = PositionAlgorithm(shoulder_len=20.76355, elbow_len=16.50985, effector_len=12, base_height=13,
                              shoulder_joint_offset=180, elbow_joint_offset=50.3, pitch_joint_offset=-111)
servo = Servo(servo_pin=2)
robot = Robot(waist=waist_joint, shoulder=shoulder_joint, elbow=elbow_joint, roll=wrist_roll_joint,
              pitch=wrist_pitch_joint, effector=servo)
robot.home_all_joints(waist=False, shoulder=True, elbow=True, roll=True, pitch=True)
#robot.home_all_joints()
robot.console(algorithm=algorithm)
#robot.position(algorithm)



