import time
import RPi.GPIO as GPIO
import math

class Movement:
    def __init__(self, motor_step, driver_microstep, motor_shaft_gear_teeth, joint_gear_teeth):
        self._motor_step = motor_step
        self._driver_microstep = driver_microstep

        self._motor_shaft_gear_teeth = motor_shaft_gear_teeth
        self._joint_gear_teeth = joint_gear_teeth

        self._speed_gear_ratio = self._motor_shaft_gear_teeth/self._joint_gear_teeth
        self._torque_gear_ratio = self._joint_gear_teeth/self._motor_shaft_gear_teeth

    def motor_angular_velocity(self, phase_time):
        integral_phase_time = phase_time * self._driver_microstep

        term = (360/self._motor_step) * integral_phase_time

        angular_velocity = (2*math.pi)/term
        return angular_velocity

    def joint_angular_velocity(self, motor_velocity):
        joint_velocity = motor_velocity * self._speed_gear_ratio

        return joint_velocity

    def motor_angular_velocity_from_joint_angular_velocity(self, joint_angular_velocity):
        motor_velocity = joint_angular_velocity/self._speed_gear_ratio

        return motor_velocity

    def _rad_to_deg(self, rad):
        return rad*180/math.pi

    def _deg_to_rad(self, deg):
        return deg*math.pi/180

    def move_steps(self, steps, high_speed, accel=0.01):
        delays = []
        angle = 1
        accel = accel
        c0 = 2000 * math.sqrt(2 * angle / accel) * 0.67703

        if steps % 2 == 0:
            loops = int(steps/2)
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
        return final_delays

    def _sec_to_milisec(self, seconds):
        return seconds / 1000000

    def accelerate_to_velocity(self, joint_angular_velocity, accel=0.01, reverse=False):
        """
        Accelerate from 0 [deg/s] to velocity [deg/s]
        The last delay value is the set velocity delay
        """
        delays = []
        angle = 1
        c0 = 2000 * math.sqrt(2 * angle / accel) * 0.67703

        i = 0
        while True:
            d = c0
            if i > 0:
                d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

            delays.append(d)
            current_velocity = self.joint_angular_velocity(self.motor_angular_velocity(self._sec_to_milisec(d)))
            if current_velocity >= joint_angular_velocity:
                break
            i += 1

        delays = [self._sec_to_milisec(x) for x in delays]
        if reverse:
            delays.reverse()

        return delays

    def constant_angular_velocity(self, joint_angular_velocity):
        motor_velocity = self.motor_angular_velocity_from_joint_angular_velocity(joint_angular_velocity)

        phase_time = (self._deg_to_rad(self._motor_step)/self._driver_microstep)/motor_velocity
        return phase_time

class Joint:
    def __init__(self, driver, sensor, gear_teeth, min_pos, max_pos, offset=0, base_angle=0, homing_direction="ANTICLOCKWISE"):
        self.driver = driver
        self.sensor = sensor

        self.position = None
        self.min_pos = min_pos
        self.max_pos = max_pos

        self.gear_teeth = gear_teeth

        self.direction = homing_direction
        self.offset = offset
        self.base_angle = base_angle

        # Homing Variables
        self.homing_velocity = 0.25                     # Angular Velocity
        self.homing_acceleration = 0.01                 # NOT ANGULAR VALUE             HAS TO BE CHANGED TO THE ANGULAR

        self.homing_steps = 200

        # Acceleration and Velocity Variables
        self.max_velocity = 0.2                         # Angular Velocity
        self.max_velocity = 1                           # NOT ANGULAR VALUE             HAS TO BE CHANGED TO THE ANGULAR

        self.velocity = 0.35                            # Angular Velocity
        self.acceleration = 0.01                        # NOT ANGULAR VALUE             HAS TO BE CHANGED TO THE ANGULAR

        # Joint Algorithms
        self.movement = Movement(motor_step=self.driver.motor_resolution, driver_microstep=self.driver.driver_resolution,
                                 motor_shaft_gear_teeth=self.driver.gear_teeth, joint_gear_teeth=self.gear_teeth)

    def _degrees_to_steps(self, degrees):
        steps = ((degrees / self.driver.motor_resolution) / (
                    self.driver.gear_teeth / self.gear_teeth)) * self.driver.driver_resolution
        return steps

    def set_angle(self, pos):
        if self.position is not None:
            if self.min_pos <= pos < self.max_pos:
                new_pos = self.position - pos

                if self.direction == 'ANTICLOCKWISE':
                    if new_pos >= 0:
                        direction = 1#GPIO.HIGH  # Anticlockwise

                    else:
                        direction = 0#GPIO.LOW  # Clockwise
                else:
                    if new_pos >= 0:
                        direction = GPIO.LOW  # Anticlockwise

                    else:
                        direction = GPIO.HIGH  # Clockwise

                new_pos = abs(new_pos)
                steps = self._degrees_to_steps(new_pos)
                self.driver.move_steps(int(steps), direction, accel=self.driver.max_acceleration)

                self.position = pos

    def home(self):
        if self.direction == 'ANTICLOCKWISE':
            direction = GPIO.HIGH
            direction2 = GPIO.LOW
        else:
            direction = GPIO.LOW
            direction2 = GPIO.HIGH

        # Calculate delays for the motor to accelerate smoothly to the set homing velocity ( Angular Velocity )
        # ( During PHASE 1 and PHASE 2 of the Homing procedure )
        accel_dels = self.movement.accelerate_to_velocity(self.homing_velocity)
        accel_dels2 = self.movement.accelerate_to_velocity(self.homing_velocity/5)

        # Calculate delays for the motor to move smoothly with constant, homing velocity ( Angular Velocity )
        # ( During PHASE 1 and PHASE 2 of the Homing procedure )
        phase_time1 = self.movement.constant_angular_velocity(self.homing_velocity)
        phase_time2 = self.movement.constant_angular_velocity(self.homing_velocity/5)

        # Start the homing procedure
        while True:
            # Set forward direction
            self.driver.set_direction(direction)

            # Move through all calculated motor delays to accelerate to homing velocity ( Angular Velocity )
            for x in accel_dels:
                # Make 1 microstep in proper period of time
                self.driver.move_del(x)

                # If the Endstop sensor detects the trigger during the accelerating procedure, abort.
                if self.sensor.check_sensor():
                    break

            # If the Endstop still detects the trigger, start the PHASE 2
            if self.sensor.check_sensor():
                # Go backwards by the set number of homing_steps
                self.driver.move_steps(self.homing_steps, direction2, accel=self.homing_acceleration)

                # Set forward direction
                self.driver.set_direction(direction)

                # Move through all calculated motor delays to accelerate to second homing velocity ( Angular Velocity )
                for x2 in accel_dels2:
                    # Make 1 microstep in proper period of time
                    self.driver.move_del(x2)

                    # If the Endstop sensor detects the trigger during the accelerating procedure, abort.
                    if self.sensor.check_sensor():
                        break
                # If the Endstop still detects the trigger, end the homing procedure
                if self.sensor.check_sensor():
                    break
                else:
                    while True:
                        # Move forward with constant second homing velocity until the Endstop is triggered
                        self.driver.move_del(phase_time2)

                        # If the Endstop still detects the trigger, end the homing procedure
                        if self.sensor.check_sensor():
                            break
                    break
            else:
                while True:
                    # Move forward with constant homing velocity until the Endstop is triggered
                    self.driver.move_del(phase_time1)

                    # If the Endstop sensor detects the trigger, stop the motor.
                    if self.sensor.check_sensor():
                        break
                # If the Endstop still detects the trigger, start the PHASE 2
                if self.sensor.check_sensor():
                    # Go backwards by the set number of homing_steps
                    self.driver.move_steps(self.homing_steps, direction2, accel=self.homing_acceleration)

                    # Set forward direction
                    self.driver.set_direction(direction)

                    # Move through all calculated motor delays to accelerate to second homing velocity ( Angular Velocity )
                    for x2 in accel_dels2:
                        # Make 1 microstep in proper period of time
                        self.driver.move_del(x2)

                        # If the Endstop sensor detects the trigger during the accelerating procedure, abort.
                        if self.sensor.check_sensor():
                            break
                    # If the Endstop still detects the trigger, end the homing procedure
                    if self.sensor.check_sensor():
                        break
                    else:
                        while True:
                            # Move forward with constant second homing velocity until the Endstop is triggered
                            self.driver.move_del(phase_time2)

                            # If the Endstop detects the trigger, end the homing procedure
                            if self.sensor.check_sensor():
                                break
            break
        self.position = 0
        if self.offset != 0:
            if self.offset < 0:
                offset = abs(self.offset)
                steps = ((offset / self.driver.motor_resolution) / (
                        self.driver.gear_teeth / self.gear_teeth)) * self.driver.driver_resolution
                self.driver.move_steps(int(steps), direction, accel=0.005)
            elif self.offset > 0:
                self.set_angle(self.offset)
        self.position = 0

class OldJoint:
    def __init__(self, driver, sensor, gear_teeth, min_pos, max_pos, offset=0,
                 base_angle=0, homing_direction="ANTICLOCKWISE"):
        self.driver = driver
        self.sensor = sensor

        self.position = None
        self.min_pos = min_pos
        self.max_pos = max_pos

        self.gear_teeth = gear_teeth

        self.direction = homing_direction
        self.offset = offset

        self.base_angle = base_angle

    def _degrees_to_steps(self, degrees):
        steps = ((degrees / self.driver.motor_resolution) / (
                    self.driver.gear_teeth / self.gear_teeth)) * self.driver.driver_resolution
        return steps

    def set_angle(self, pos):
        if self.position is not None:
            if self.min_pos <= pos < self.max_pos:
                new_pos = self.position - pos
                #print("New pos: ", new_pos)

                if self.direction == 'ANTICLOCKWISE':
                    if new_pos >= 0:
                        direction = 1#GPIO.HIGH  # Anticlockwise

                    else:
                        direction = 0#GPIO.LOW  # Clockwise
                else:
                    if new_pos >= 0:
                        direction = GPIO.LOW  # Anticlockwise

                    else:
                        direction = GPIO.HIGH  # Clockwise

                new_pos = abs(new_pos)
                steps = self._degrees_to_steps(new_pos)
                #print(steps)
                #print("Steps: ", int(steps), "   ", "Direction: ", direction)
                self.driver.move_steps(int(steps), direction, accel=self.driver.max_acceleration)

                self.position = pos
                #print("New position", self.position)

    def home(self, multipicator=1):
        if self.direction == 'ANTICLOCKWISE':
            direction = GPIO.HIGH
            direction2 = GPIO.LOW
        else:
            direction = GPIO.LOW
            direction2 = GPIO.HIGH

        while True:
            self.driver.move_steps(int(4*multipicator), direction, accel=0.1)

            if self.sensor.check_sensor():
                self.driver.move_steps(int(200), direction2, accel=0.001)
                while True:
                    self.driver.move_steps(2, direction, accel=0.01)

                    if self.sensor.check_sensor():
                        break
                break

        self.position = 0
        if self.offset != 0:
            if self.offset < 0:
                offset = abs(self.offset)
                steps = ((offset / self.driver.motor_resolution) / (
                        self.driver.gear_teeth / self.gear_teeth)) * self.driver.driver_resolution
                print("Steps: ", steps)
                self.driver.move_steps(int(steps), direction, accel=0.005)
            elif self.offset > 0:
                self.set_angle(self.offset)
        self.position = 0


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


