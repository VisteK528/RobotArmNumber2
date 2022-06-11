import RPi.GPIO as GPIO
import math

class Movement:
    def __init__(self, motor_step, driver_microstep, motor_shaft_gear_teeth, joint_gear_teeth):
        self._motor_step = motor_step
        self._driver_microstep = driver_microstep
        self._one_pulse_step = self._deg_to_rad(self._motor_step/self._driver_microstep)

        self._motor_shaft_gear_teeth = motor_shaft_gear_teeth
        self._joint_gear_teeth = joint_gear_teeth

        self._speed_gear_ratio = self._motor_shaft_gear_teeth/self._joint_gear_teeth
        self._torque_gear_ratio = self._joint_gear_teeth/self._motor_shaft_gear_teeth

    def _rad_to_deg(self, rad):
        return rad*180/math.pi

    def _deg_to_rad(self, deg):
        return deg*math.pi/180

    def _milisec_to_sec(self, miliseconds):
        return miliseconds / 1000000

    def _sec_to_milisec(self, seconds):
        return seconds * 1000000

    def motor_vel(self, phase_time):
        integral_phase_time = phase_time * self._driver_microstep

        term = (360/self._motor_step) * integral_phase_time

        angular_velocity = (2*math.pi)/term
        return angular_velocity

    def phase_time(self, joint_ang_vel):
        motor_ang_vel = self.motor_vel_from_joint_vel(joint_ang_vel)
        return self._one_pulse_step/motor_ang_vel

    def joint_vel_from_motor_vel(self, motor_ang_vel):
        joint_ang_vel = motor_ang_vel * self._speed_gear_ratio
        return joint_ang_vel

    def motor_vel_from_joint_vel(self, joint_ang_vel):
        motor_ang_vel = joint_ang_vel/self._speed_gear_ratio
        return motor_ang_vel

    def move_steps(self, steps, max_speed, accel):
        max_speed = self.motor_vel_from_joint_vel(max_speed)
        max_speed_delay = self._sec_to_milisec(self._one_pulse_step/max_speed)
        delays = []
        angle = self._one_pulse_step
        c0 = 2000000 * math.sqrt(2 * angle / accel) * 0.13568198123907316536355537605674

        if steps % 2 == 0:
            loops = int(steps / 2)
            even = True
        else:
            loops = int(steps / 2) + 1
            even = False

        for i in range(loops):
            d = c0
            if i > 0:
                d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

            if d < max_speed_delay:
                d = max_speed_delay

            delays.append(d)

        delays_buff = delays.copy()
        if not even:
            delays_buff.pop()
        delays_buff.reverse()

        for x in delays_buff:
            delays.append(x)

        final_delays = [self._milisec_to_sec(x) for x in delays]
        return final_delays

    """ Wymagana optymalizacja kodu ( po co wywoływać tyle razy funkcję self.joint_vel_from_motor_vel?"""
    def accelerate_to_velocity(self, joint_ang_vel, accel=0.5, reverse=False):
        """
        Accelerate from 0 [deg/s] to velocity [deg/s]
        The last delay value is the set velocity delay
        """
        delays = []
        angle = self._one_pulse_step
        c0 = 2000000 * math.sqrt(2 * angle / accel) * 0.13568198123907316536355537605674

        i = 0
        while True:
            d = c0
            if i > 0:
                d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

            delays.append(d)
            current_velocity = self.joint_vel_from_motor_vel(self.motor_vel(self._milisec_to_sec(d)))
            if current_velocity >= joint_ang_vel:
                break
            i += 1

        delays = [self._milisec_to_sec(x) for x in delays]
        if reverse:
            delays.reverse()

        return delays

    """ Do wyrzucenia / poprawy"""
    def constant_angular_velocity(self, joint_angular_velocity):
        motor_velocity = self.motor_vel_from_joint_vel(joint_angular_velocity)

        phase_time = self._one_pulse_step/motor_velocity
        return phase_time

    def calculate_all_variables(self, delays):
        time_series = []
        time_sum = 0
        for delay in delays:
            time_sum += delay
            time_series.append(time_sum)

        motor_ang_vels = []
        for i in range(len(time_series)):
            if i == 0:
                d_t = time_series[i]
            else:
                d_t = time_series[i] - time_series[i - 1]

            d_pos = self._one_pulse_step

            motor_ang_vel = d_pos / d_t

            motor_ang_vels.append(motor_ang_vel)

        joint_ang_vels = [self.joint_vel_from_motor_vel(x) for x in motor_ang_vels]

        accels = []
        for i in range(0, len(joint_ang_vels), 2):
            if i == 0:
                d_v = joint_ang_vels[i]
                d_t = time_series[i]
            else:
                d_v = joint_ang_vels[i] - joint_ang_vels[i - 1]
                d_t = time_series[i] - time_series[i - 1]

            acceleration = round(d_v / d_t, 2)
            accels.append(acceleration)
            accels.append(acceleration)

        pos = []
        pos_value = 0
        for i in range(len(time_series)):
            try:
                temporary_pos = (time_series[i + 1] - time_series[i]) * joint_ang_vels[i + 1] + accels[i + 1] * 0.5 * (
                            time_series[i + 1] - time_series[i]) ** 2
                pos_value += temporary_pos
                pos.append(pos_value)
            except:
                pos.append(pos[len(pos) - 1])
                pass

        return delays, time_series, motor_ang_vels, joint_ang_vels, accels, pos


class Joint:
    def __init__(self, driver, sensor, gear_teeth, homing_direction="ANTICLOCKWISE"):
        self.driver = driver
        self.sensor = sensor

        self.position = None
        self._min_pos = 0
        self._max_pos = 360

        self.gear_teeth = gear_teeth

        self.direction = homing_direction
        self._offset = 0
        self._base_angle = 0

        # Homing Variables
        self.homing_velocity = 0.25                     # Angular Velocity
        self.homing_acceleration = 0.5                  # Angular Acceleration
        self.homing_steps = 200

        # Acceleration and Velocity Variables
        self.max_velocity = 0.7                         # Angular Velocity
        self.max_acceleration = 0.75                    # Angular Acceleration

        # Joint Algorithms
        self.movement = Movement(motor_step=self.driver.motor_resolution, driver_microstep=self.driver.driver_resolution,
                                 motor_shaft_gear_teeth=self.driver.gear_teeth, joint_gear_teeth=self.gear_teeth)

    def set_homing_steps(self, homing_steps):
        self.homing_steps = homing_steps

    def set_homing_velocity(self, homing_velocity):
        self.homing_velocity = homing_velocity

    def set_homing_acceleration(self, homing_acceleration):
        self.homing_acceleration = homing_acceleration

    def set_max_velocity(self, max_velocity):
        self.max_velocity = max_velocity

    def set_max_acceleration(self, max_acceleration):
        self.max_acceleration = max_acceleration

    def set_min_pos(self, min_pos):
        self._min_pos = min_pos

    def set_max_pos(self, max_pos):
        self._max_pos = max_pos

    def set_offset(self, offset):
        self._offset = offset

    def set_base_angle(self, base_angle):
        self._base_angle = base_angle

    def _degrees_to_steps(self, degrees):
        steps = ((degrees / self.driver.motor_resolution) / (
                    self.driver.gear_teeth / self.gear_teeth)) * self.driver.driver_resolution
        return steps

    def _move_by_steps(self, steps, direction, max_velocity, max_acceleration):
        delays = self.movement.move_steps(round(steps), max_speed=max_velocity, accel=max_acceleration)

        self.driver.set_direction(direction)
        for delay in delays:
            self.driver.move_del(delay)

    def move_by_angle(self, pos):
        if self.position is not None:
            if self._min_pos <= pos < self._max_pos:
                new_pos = self.position - pos

                if self.direction == 'ANTICLOCKWISE':
                    if new_pos >= 0:
                        direction = 1  # GPIO.HIGH  # Anticlockwise

                    else:
                        direction = 0  # GPIO.LOW  # Clockwise
                else:
                    if new_pos >= 0:
                        direction = GPIO.LOW  # Anticlockwise

                    else:
                        direction = GPIO.HIGH  # Clockwise

                new_pos = abs(new_pos)
                steps = self._degrees_to_steps(new_pos)
                self._move_by_steps(round(steps), direction, self.max_velocity, self.max_acceleration)
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
                self._move_by_steps(self.homing_steps, direction2, self.max_velocity, self.max_acceleration)

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
                    self._move_by_steps(self.homing_steps, direction2, self.max_velocity, self.max_acceleration)

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
        if self._offset != 0:
            if self._offset < 0:
                offset = abs(self._offset)
                steps = ((offset / self.driver.motor_resolution) / (
                        self.driver.gear_teeth / self.gear_teeth)) * self.driver.driver_resolution

                self._move_by_steps(round(steps), direction, self.max_velocity, self.max_acceleration)

            elif self._offset > 0:
                self.move_by_angle(self._offset)
        self.position = 0

class OldMovement:
    def __init__(self, motor_step, driver_microstep, motor_shaft_gear_teeth, joint_gear_teeth):
        self._motor_step = motor_step
        self._driver_microstep = driver_microstep
        self._one_pulse_step = self._deg_to_rad(self._motor_step/self._driver_microstep)

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

    def _milisec_to_sec(self, miliseconds):
        return miliseconds / 1000000

    def _sec_to_milisec(self, seconds):
        return seconds * 1000000

    def motor_vel(self, phase_time):
        integral_phase_time = phase_time * self._driver_microstep

        term = (360/self._motor_step) * integral_phase_time

        angular_velocity = (2*math.pi)/term
        return angular_velocity

    def phase_time(self, joint_ang_vel):
        motor_ang_vel = self.motor_vel_from_joint_vel(joint_ang_vel)
        return self._one_pulse_step/motor_ang_vel

    def joint_vel_from_motor_vel(self, motor_ang_vel):
        joint_ang_vel = motor_ang_vel * self._speed_gear_ratio
        return joint_ang_vel

    def motor_vel_from_joint_vel(self, joint_ang_vel):
        motor_ang_vel = joint_ang_vel/self._speed_gear_ratio
        return motor_ang_vel

    def new_move_steps(self, steps, max_speed, accel):
        max_speed = self.motor_vel_from_joint_vel(max_speed)
        max_speed_delay = self._sec_to_milisec(self._one_pulse_step/max_speed)
        delays = []
        angle = self._one_pulse_step
        c0 = 2000000 * math.sqrt(2 * angle / accel) * 0.13568198123907316536355537605674

        if steps % 2 == 0:
            loops = int(steps / 2)
            even = True
        else:
            loops = int(steps / 2) + 1
            even = False

        for i in range(loops):
            d = c0
            if i > 0:
                d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

            if d < max_speed_delay:
                d = max_speed_delay

            delays.append(d)

        delays_buff = delays.copy()
        if not even:
            delays_buff.pop()
        delays_buff.reverse()

        for x in delays_buff:
            delays.append(x)

        final_delays = [self._milisec_to_sec(x) for x in delays]
        return final_delays

    """ Wymagana optymalizacja kodu ( po co wywoływać tyle razy funkcję self.joint_vel_from_motor_vel?"""
    def accelerate_to_velocity(self, joint_ang_vel, accel=0.5, reverse=False):
        """
        Accelerate from 0 [deg/s] to velocity [deg/s]
        The last delay value is the set velocity delay
        """
        delays = []
        angle = self._one_pulse_step
        c0 = 2000000 * math.sqrt(2 * angle / accel) * 0.13568198123907316536355537605674

        i = 0
        while True:
            d = c0
            if i > 0:
                d = delays[i - 1] - ((2 * delays[i - 1]) / (4 * i + 1))

            delays.append(d)
            current_velocity = self.joint_vel_from_motor_vel(self.motor_vel(self._milisec_to_sec(d)))
            if current_velocity >= joint_ang_vel:
                break
            i += 1

        delays = [self._milisec_to_sec(x) for x in delays]
        if reverse:
            delays.reverse()

        return delays

    """ Do wyrzucenia / poprawy"""
    def constant_angular_velocity(self, joint_angular_velocity):
        motor_velocity = self.motor_vel_from_joint_vel(joint_angular_velocity)

        phase_time = self._one_pulse_step/motor_velocity
        return phase_time

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

    def move_by_angle(self, pos):
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
                self.move_by_angle(self.offset)
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