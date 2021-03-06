import math
from HelperClasses import Conversions


class PositionAlgorithm(Conversions):
    def __init__(self, shoulder_len, elbow_len, effector_len, base_height, waist_joint_offset=0,
                 shoulder_joint_offset=0, elbow_joint_offset=0, pitch_joint_offset=0):
        """
        Robot PositionAlgorithm calculates the position of each joint ( its angle ) in order to place robot arm's
        effector in the desired position

        :param shoulder_len: AB section, |AB| = shoulder_len
        :param elbow_len: BC section, |BC| = elbow_len
        :param effector_len: CD section, |CD| = effector_len
        :param base_height: H = base_height
        """
        # Constant, Initial Variables
        self.ab_sect = shoulder_len
        self.bc_sect = elbow_len
        self.cd_sect = effector_len
        self.h = base_height

        # Arm Points
        self.a = (0, 0)             # Constant (center of the arm coordinate system ), start of the shoulder section
        self.b = (0, 0)             # End of the shoulder and AB section; start of the elbow and BC section
        self.c = (0, 0)             # End of the elbow and BC section; start of the effector and CD section
        self.d = (0, 0)             # End of the effector and CD section; arm set point

        self.ac_sect = 0         # Hypotenuse of the ABC triangle

        # Base Robot Angles ( degrees )
        self.alfa = 0
        self.beta = 0
        self.theta = 0
        self.omega = 0

        # Rad Base Robot Angles
        self.rad_alfa = 0
        self.rad_beta = 0
        self.rad_theta = 0

        # Robot-adapted Base Robot Angles ( degrees )
        self.r_alfa = 0
        self.r_beta = 0
        self.r_theta = 0
        self.r_omega = 0

        # Offsets
        self.waist_joint_offset = waist_joint_offset
        self.shoulder_joint_offset = shoulder_joint_offset
        self.elbow_joint_offset = elbow_joint_offset
        self.pitch_joint_offset = pitch_joint_offset

    def update_base_robot_angles(self):
        """
        Updates alfa, beta and theta values from radians to degrees
        :return: -> None
        """
        self.alfa = self._rad_to_deg(self.rad_alfa)
        self.beta = self._rad_to_deg(self.rad_beta)
        self.theta = self._rad_to_deg(self.rad_theta)

    def update_robot_adapted_base_robot_angles(self):
        """
        Updates the calculated values of alfa, beta and theta by subtracting from them their offsets
        :return: -> None
        """
        self.r_alfa = abs(self.alfa-self.shoulder_joint_offset)
        self.r_beta = abs(self.beta-self.elbow_joint_offset)
        self.r_theta = abs(self.theta-self.pitch_joint_offset)
        self.r_omega = abs(self.omega-self.waist_joint_offset)

    def calc_arm_pos(self, x: float, y: float, z: float, align='horizontal'):
        """
        Calculates the values of alfa, beta, theta and omega values in order to move robot's effector to desired
        position ( X point of coordinates (x, y, z) ) in 3D space and then align it horizontally or vertically depending
        on user's choice
        :return: -> r_alfa (float), r_beta (float), r_theta (float), r_omega(float)
        """
        self.omega = self._rad_to_deg(math.atan2(y, x))
        distance = math.sqrt(pow(x, 2)+pow(y, 2))

        if align == "horizontal":
            self.calc_arm_pos_horizontally(distance, z)
        else:
            self.calc_arm_pos_vertically(distance, z)

        return self.r_alfa, self.r_beta, self.r_theta, self.r_omega

    def calc_arm_pos_horizontally(self, x: float, y: float):
        """
        Calculates values of alfa, beta and theta in order to move robot's effector to preset position (X, Y)
        and align it horizontally
        :return: -> alfa (float), beta (float), theta (float)
        """

        new_x = x - self.cd_sect
        new_y = y - self.h
        self.ac_sect = math.sqrt(new_x**2 + new_y**2)

        alfa2 = math.atan(new_y/new_x)
        alfa1 = math.acos((self.ab_sect**2+self.ac_sect**2-self.bc_sect**2)/(2*self.ab_sect*self.ac_sect))
        self.rad_alfa = alfa2+alfa1

        self.rad_beta = math.acos((self.ab_sect**2+self.bc_sect**2-self.ac_sect**2)/(2*self.ab_sect*self.bc_sect))

        self.rad_theta = math.pi-(self.rad_alfa+self.rad_beta)

        self.update_base_robot_angles()
        self.update_robot_adapted_base_robot_angles()

        self.d = (x, y)
        self.c = (new_x, y)
        b_x = math.sqrt(self.ab_sect**2/(1+math.tan(self.rad_alfa)**2))
        b_y = math.tan(self.rad_alfa) * b_x

        if 90 < self.alfa < 180:
            b_x = math.sqrt(self.ab_sect ** 2 / (1 + math.tan(self.rad_alfa) ** 2))
            b_y = math.tan(self.rad_alfa) * b_x
            b_x *= -1
            b_y *= -1

        self.b = (b_x, b_y)
        self.a = (0, self.h)

        #print(self.a, self.b, self.c, self.d)
        return self.alfa, self.beta, self.theta

    def calc_arm_pos_vertically(self, x: float, y: float):
        """
        Calculates values of alfa, beta and theta in order to move robot's effector to preset position (X, Y)
        and align it vertically
        :return: -> alfa (float), beta (float), theta (float)
        """
        new_y = y - self.h
        new_y2 = new_y + self.cd_sect

        self.ac_sect = math.sqrt(x**2 + new_y2**2)

        alfa2 = math.atan(new_y2 / x)
        alfa1 = math.acos(
            (self.ab_sect ** 2 + self.ac_sect ** 2 - self.bc_sect ** 2) / (2 * self.ab_sect * self.ac_sect))
        self.rad_alfa = alfa2 + alfa1

        self.rad_beta = math.acos(
            (self.ab_sect ** 2 + self.bc_sect ** 2 - self.ac_sect ** 2) / (2 * self.ab_sect * self.bc_sect))

        self.rad_theta = math.pi - (self.rad_alfa + self.rad_beta) - math.pi/2

        self.update_base_robot_angles()
        self.update_robot_adapted_base_robot_angles()

        self.d = (x, y)
        self.c = (x, y+self.cd_sect)
        b_x = round(math.sqrt(self.ab_sect ** 2 / (1 + math.tan(self.rad_alfa) ** 2)), 3)
        b_y = round(math.tan(self.rad_alfa) * b_x, 3)

        if 90 < self.alfa < 180:
            b_x *= -1
            b_y *= -1

        self.b = (b_x, b_y)
        self.a = (0, self.h)

        return self.alfa, self.beta, self.theta

    def calc_arm_pos_horizontally_adapted(self, x: float, y: float):
        """
        Calculates the angles by calling the calc_arm_pos_horizontally method and then updating
        the robot-adapted values
        :return: -> r_alfa (float), r_beta (float), r_theta (float)
        """
        self.calc_arm_pos_horizontally(x, y)
        self.update_robot_adapted_base_robot_angles()

        return self.r_alfa, self.r_beta, self.r_theta

    def calc_arm_pos_vertically_adapted(self, x: float, y: float):
        """
        Calculates the angles by calling the calc_arm_pos_vertically method and then updating
        the robot-adapted values
        :return: -> r_alfa (float), r_beta (float), r_theta (float)
        """
        self.calc_arm_pos_vertically(x, y)
        self.update_robot_adapted_base_robot_angles()

        return self.r_alfa, self.r_beta, self.r_theta