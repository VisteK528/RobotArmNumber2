from Movement import Movement
import RPi.GPIO as GPIO

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