from Joint import Joint
from Endstop import EndStop
from Drivers import TMC2209, DM556Driver, AN4988Driver
from Servo import Servo
import RPi.GPIO as GPIO
import time
import threading as th
import os
os.system('sudo pigpiod')

import pigpio
from PositionAlgorithm import PositionAlgorithm

# Pi GPIO initialization
pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)

#=======================================================================================================================
#=====================================          Waist           ========================================================
#=======================================================================================================================

waist_driver = TMC2209(en=26, dir=13, step=19, resolution=0.9, gear_teeth=20)
waist_endstop = EndStop(SIGNAL_PIN=12, type='up')

waist_joint = Joint(driver=waist_driver, sensor=waist_endstop, gear_teeth=125, homing_direction='ANTICLOCKWISE')
waist_joint.set_min_pos(-1)
waist_joint.set_max_pos(358)
waist_joint.set_offset(60)

waist_joint.set_max_velocity(0.2)
waist_joint.set_max_acceleration(0.5)

#=======================================================================================================================
#=====================================          Shoulder           =====================================================
#=======================================================================================================================


shoulder_driver = DM556Driver(DIR=15, PUL=14, driver_resolution=46.6667, motor_resolution=1.8, gear_teeth=20)
shoulder_endstop = EndStop(SIGNAL_PIN=6, type='up')

shoulder_joint = Joint(shoulder_driver, shoulder_endstop, gear_teeth=149, homing_direction='CLOCKWISE')
shoulder_joint.set_homing_velocity(0.15)
shoulder_joint.set_max_acceleration(0.05)
shoulder_joint.set_max_pos(150)
shoulder_joint.set_offset(17)

#=======================================================================================================================
#=====================================          Elbow           ========================================================
#=======================================================================================================================

elbow_driver = AN4988Driver(en=18, dir=5, step=7, resolution=0.9, gear_teeth=20)
elbow_driver.set_max_speed(1000)
elbow_endstop = EndStop(SIGNAL_PIN=23, type='down')

elbow_joint = Joint(driver=elbow_driver, sensor=elbow_endstop, gear_teeth=62, homing_direction='CLOCKWISE')
elbow_joint.set_max_pos(70)
elbow_joint.set_base_angle(50.3)

#=======================================================================================================================
#=====================================          Wrist Roll           ===================================================
#=======================================================================================================================

wrist_roll_driver = TMC2209(en=21, dir=16, step=20, resolution=1.8, gear_teeth=1)
wrist_roll_endstop = EndStop(SIGNAL_PIN=24, type="up")

wrist_roll_joint = Joint(driver=wrist_roll_driver, sensor=wrist_roll_endstop, gear_teeth=1, homing_direction='ANTICLOCKWISE')
wrist_roll_joint.set_homing_acceleration(0.25)
wrist_roll_joint.set_homing_velocity(0.5)
wrist_roll_joint.set_max_pos(270)
wrist_roll_joint.set_offset(-22)

#=======================================================================================================================
#=====================================          Wrist Pitch            =================================================
#=======================================================================================================================

wrist_pitch_driver = TMC2209(en=10, dir=9, step=11, resolution=1.8, gear_teeth=20)
wrist_pitch_endstop = EndStop(SIGNAL_PIN=25, type='up')

wrist_pitch_joint = Joint(driver=wrist_pitch_driver, sensor=wrist_pitch_endstop, gear_teeth=40,
                          homing_direction="ANTICLOCKWISE")
wrist_pitch_joint.set_homing_acceleration(0.2)
wrist_pitch_joint.set_homing_velocity(0.25)
wrist_pitch_joint.set_max_acceleration(0.8)
wrist_pitch_joint.set_max_velocity(1.2)
wrist_pitch_joint.set_homing_steps(100)
wrist_pitch_joint.set_max_pos(250)

class Robot:
    def __init__(self, waist, shoulder, elbow, roll, pitch, effector, position_algorithm):
        # Joints and Effectors
        self.waist = waist
        self.shoulder = shoulder
        self.elbow = elbow
        self.roll = roll
        self.pitch = pitch
        self.effector = effector

        # Algorithms
        self.position_algorithm = position_algorithm

        # Variables
        self._homed = None

    def _move_joints_to_the_pos(self, x, y, aligment):
        assert type(x), type(y) == float

        if aligment == 'vertical':
            self.position_algorithm.calc_arm_pos_vertically_adapted(x, y)
        elif aligment == 'horizontal':
            self.position_algorithm.calc_arm_pos_horizontally_adapted(x, y)

        th1 = th.Thread(target=self.shoulder.move_by_angle, args=[self.position_algorithm.r_alfa, ])
        th2 = th.Thread(target=self.elbow.move_by_angle, args=[self.position_algorithm.r_beta, ])
        th3 = th.Thread(target=self.pitch.move_by_angle, args=[self.position_algorithm.r_theta, ])

        th1.start()
        th2.start()
        th3.start()

        th1.join()
        th2.join()
        th3.join()

    def home_all_joints(self, waist=True, shoulder=True, elbow=True, roll=True, pitch=True):
        counter = 0
        try:
            print('Homing all joints...')
            if waist:
                print("Waist homing... ", end='')
                self.waist.home()
                print("Waist homed")
                counter += 1
            if shoulder:
                print("Shoulder homing... ", end='')
                self.shoulder.home()
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

    def console(self):
        while True:
            message = input("").lower().split()

            if message[0] == "vposition":
                x, y = float(message[1]), float(message[2])
                self._move_joints_to_the_pos(x, y, 'vertical')

            elif message[0] == "hposition":
                x, y = float(message[1]), float(message[2])
                self._move_joints_to_the_pos(x, y, 'horizontal')

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
                        self.waist.move_by_angle(float(angle))
                    elif motor == "shoulder":
                        self.shoulder.move_by_angle(float(angle))
                    elif motor == "elbow":
                        self.elbow.move_by_angle(float(angle))
                    elif motor == "roll":
                        self.roll.move_by_angle(float(angle))
                    elif motor == "pitch":
                        self.pitch.move_by_angle(float(angle))
                    elif motor == "servo":
                        self.effector.move_servo(float(angle))
            time.sleep(2)

algorithm = PositionAlgorithm(shoulder_len=20.76355, elbow_len=16.50985, effector_len=7.835, base_height=15,
                              shoulder_joint_offset=180, elbow_joint_offset=50.3, pitch_joint_offset=-111)
servo = Servo(servo_pin=2)
robot = Robot(waist=waist_joint, shoulder=shoulder_joint, elbow=elbow_joint, roll=wrist_roll_joint,
              pitch=wrist_pitch_joint, effector=servo, position_algorithm=algorithm)
robot.home_all_joints(waist=False, shoulder=True, elbow=True, roll=True, pitch=True)
robot.console()