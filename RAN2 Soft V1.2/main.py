from Joint import Joint
from Endstop import EndStop
from Drivers import TMC2209, DM556Driver, AN4988Driver
from Servo import Servo
import RPi.GPIO as GPIO
import time
import threading as th
import os
from Connections import Server

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

waist_joint = Joint(driver=waist_driver, sensor=waist_endstop, gear_teeth=125, homing_direction='CLOCKWISE')
waist_joint.set_min_pos(-1)
waist_joint.set_max_pos(358)

waist_joint.set_max_velocity(0.2)
waist_joint.set_max_acceleration(0.5)

#=======================================================================================================================
#=====================================          Shoulder           =====================================================
#=======================================================================================================================


shoulder_driver = DM556Driver(DIR=15, PUL=14, driver_resolution=8, motor_resolution=1.8, gear_teeth=20)
shoulder_endstop = EndStop(SIGNAL_PIN=6, type='up')

shoulder_joint = Joint(shoulder_driver, shoulder_endstop, gear_teeth=149, homing_direction='CLOCKWISE')
shoulder_joint.set_homing_velocity(0.12)
shoulder_joint.set_max_acceleration(0.05)
shoulder_joint.set_max_pos(171)
shoulder_joint.set_offset(15)

#=======================================================================================================================
#=====================================          Elbow           ========================================================
#=======================================================================================================================

elbow_driver = TMC2209(en=18, dir=5, step=7, resolution=0.9, gear_teeth=20)
elbow_endstop = EndStop(SIGNAL_PIN=23, type='up')

elbow_joint = Joint(driver=elbow_driver, sensor=elbow_endstop, gear_teeth=62, homing_direction='ANTICLOCKWISE')
elbow_joint.set_max_pos(70)
elbow_joint.set_base_angle(50.3)

#=======================================================================================================================
#=====================================          Wrist Roll           ===================================================
#=======================================================================================================================

wrist_roll_driver = TMC2209(en=21, dir=16, step=20, resolution=1.8, gear_teeth=1)
wrist_roll_endstop = EndStop(SIGNAL_PIN=24, type="up")

wrist_roll_joint = Joint(driver=wrist_roll_driver, sensor=wrist_roll_endstop, gear_teeth=1,
                         homing_direction='ANTICLOCKWISE')
wrist_roll_joint.set_homing_acceleration(0.25)
wrist_roll_joint.set_homing_velocity(0.5)
wrist_roll_joint.set_homing_steps(100)

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
wrist_pitch_joint.set_homing_velocity(0.4)
wrist_pitch_joint.set_homing_steps(100)

wrist_pitch_joint.set_max_acceleration(0.8)
wrist_pitch_joint.set_max_velocity(1.2)
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

        # Joints
        self.joints = [self.waist, self.shoulder, self.elbow, self.roll, self.pitch]
        self.joints_names = ["Waist", "Shoulder", "Elbow", "Roll", "Pitch"]
        self.joints_names_dict = {x: i for i, x in enumerate(self.joints_names)}

        # Positions
        self.positions = [self.waist.position, self.shoulder.position, self.elbow.position,
                          self.roll.position, self.pitch.position]
        # Algorithms
        self.position_algorithm = position_algorithm

        # Variables
        self._homed = None

    def _move_all_joints_to_the_pos(self, joint_values):
        for i, joint_value in enumerate(joint_values):
            if joint_value is None:
                joint_values[i] = self.positions[i]

        threads = [th.Thread(target=self.waist.move_by_angle, args=[joint_values[0]]),
                   th.Thread(target=self.shoulder.move_by_angle, args=[joint_values[1]]),
                   th.Thread(target=self.elbow.move_by_angle, args=[joint_values[2]]),
                   th.Thread(target=self.roll.move_by_angle, args=[joint_values[3]]),
                   th.Thread(target=self.pitch.move_by_angle, args=[joint_values[4]])]

        # Start all threads
        for thread in threads:
            thread.start()

        # Join all threads
        for thread in threads:
            thread.join()

    def _move_joints_to_the_cords(self, x: float, y: float, z: float, alignment: str):

        self.position_algorithm.calc_arm_pos(x, y, z, alignment)

        joint_values = [self.position_algorithm.r_omega, self.position_algorithm.r_alfa,
                        self.position_algorithm.r_beta, None, self.position_algorithm.r_theta]

        self._move_all_joints_to_the_pos(joint_values)

    def home_all_joints(self, waist=True, shoulder=True, elbow=True, roll=True, pitch=True):
        homing_enabled = [waist, shoulder, elbow, roll, pitch]
        counter = 0

        print("Homing all joints...")
        try:
            for i, joint in enumerate(self.joints):
                if homing_enabled[i]:
                    print(f"{self.joints_names[i]} homing...", end='')
                    joint.home()
                    print(f"{self.joints_names[i]} homed")
                    counter += 1

            if counter == 5:
                print("All joints homed successfully!")
            else:
                print("Selected joints homed successfully!")

            self._homed = True
        except Exception as e:
            print(f'Homing failed due to the error: {e}')

    def _remote_control(self):
        self.server = Server(HEADER=64, FORMAT='utf-8')
        conn, address = self.server.start_host()

        while self.server.connected:
            msg = self.server.recv_msg(conn).decode(self.server.FORMAT)
            if msg == self.server.DISCONNECT_MESSAGE:
                self.server.connected = False
            else:
                data = msg.split(";")
                free_mode = data.pop(0)

                joint_values = [float(value) for value in data]
                if free_mode:
                    self._move_all_joints_to_the_pos(joint_values)

                elif not free_mode:
                    self._move_joints_to_the_cords(*joint_values, alignment='horizontal')

            self.server.send_msg(conn, "Message Received")
        conn.close()

    def console(self):
        while True:
            message = input(">").lower().split()

            if message[0] == "vposition":
                x, y, z = float(message[1]), float(message[2]), float(message[3])
                self._move_joints_to_the_cords(x, y, z, 'vertical')

            elif message[0] == "hposition":
                x, y, z = float(message[1]), float(message[2]), float(message[3])
                self._move_joints_to_the_cords(x, y, z, 'horizontal')

            elif message[0] == 'remote':
                self._remote_control()

            elif message[0] == "move":
                motor, angle = message[1], message[2]
                self.joints[self.joints_names_dict[motor]].move_by_angle(float(angle))

            elif message[0] == "home":
                motor = message[1]
                self.joints[self.joints_names_dict[motor]].home()

            time.sleep(1)


algorithm = PositionAlgorithm(shoulder_len=20.76355, elbow_len=16.50985, effector_len=7.835, base_height=15,
                              waist_joint_offset=0, shoulder_joint_offset=180, elbow_joint_offset=50.3,
                              pitch_joint_offset=-111)
servo = Servo(servo_pin=2)
robot = Robot(waist=waist_joint, shoulder=shoulder_joint, elbow=elbow_joint, roll=wrist_roll_joint,
              pitch=wrist_pitch_joint, effector=servo, position_algorithm=algorithm)
# robot.home_all_joints(waist=False, shoulder=True, elbow=True, roll=True, pitch=True)
robot.console()
