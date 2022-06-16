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