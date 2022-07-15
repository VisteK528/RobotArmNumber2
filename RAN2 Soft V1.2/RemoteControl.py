import pygame
import time
pygame.init()


class RemoteControl:
    """
    Controlling the Robot Arm via connected Xbox Controller
    """
    def __init__(self):
        class Axis:
            def __init__(self):
                self.x = 0
                self.y = 0
                self.z = 0

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.selected_joint = 1
        self.j = [0 for _ in range(6)]

        self._free_mode = False
        self.axis = Axis()

        #Gripper Control
        self.gripper_pos = 150
        self._gripper_change_unit = 1.5
        self._gripper_change_delay = 0.025

        #Positon Control
        self._position_change_unit = 0.1
        self._position_change_delay = 0.025

        #Free Control
        self._free_change_unit = 0.5
        self._free_change_delay = 0.025

        #Maximum Position
        self._max_pos = 40

    def check_apply_button(self):
        """
        Checks if the 'A' button has been pressed down
        :return: -> bool
        """
        if self.joystick.get_button(0):
            return True
        return False

    def _reset_position_control_axes(self):
        pass

    def _reset_free_control_pos(self):
        self.j = [0 for _ in range(1, 6)]

    def _select_joint(self):
        """
        Selects the joint which value has to be updated
        :return: -> None
        """
        if 0 < self.selected_joint < 7:
            if self.joystick.get_button(5):
                if self.selected_joint != 6:
                    self.selected_joint += 1
                    time.sleep(0.2)

            if self.joystick.get_button(4):
                if self.selected_joint != 1:
                    self.selected_joint -= 1
                    time.sleep(0.2)

    def _update_positions(self):
        """
        Updates the position of the selected joint
        :return: -> None
        """
        pygame.event.pump()
        value = self.joystick.get_axis(1)

        if -1 < self.j[self.selected_joint - 1] <= 360:
            if value < -0.8:
                if self.j[self.selected_joint - 1] != 360:
                    self.j[self.selected_joint - 1] += self._free_change_unit
                    time.sleep(self._free_change_delay)

            elif value > 0.8:
                if self.j[self.selected_joint - 1] != 0:
                    self.j[self.selected_joint - 1] -= self._free_change_unit
                    time.sleep(self._free_change_delay)

    def _round_data(self, ndigits):
        """
        Rounds values of the axis and gripper position
        :param ndigits: Sets the accuracy/approximation of the rounding
        :return: -> None
        """
        self.axis.x = round(self.axis.x, ndigits)
        self.axis.y = round(self.axis.y, ndigits)
        self.axis.z = round(self.axis.z, ndigits)

        self.gripper_pos = round(self.gripper_pos, ndigits)

    def _get_gripper_data(self):
        """
        Updates gripper position
        :return: -> None
        """
        gripper_plus_axis = self.joystick.get_axis(5) + 1
        gripper_minus_axis = self.joystick.get_axis(4) + 1

        scaled_gripper_plus_axis = abs(round(self._gripper_change_unit * gripper_plus_axis, 2))
        scaled_gripper_minus_axis = abs(round(self._gripper_change_unit * gripper_minus_axis, 2))

        if gripper_plus_axis >= 0 and (self.gripper_pos + scaled_gripper_plus_axis) <= 180:
            self.gripper_pos += scaled_gripper_plus_axis
            time.sleep(self._gripper_change_delay)

        if gripper_minus_axis >= 0 and (self.gripper_pos - scaled_gripper_minus_axis) >= 0:
            self.gripper_pos -= scaled_gripper_minus_axis
            time.sleep(self._gripper_change_delay)

    def free_control(self):
        """
        Selects joint to be updated and updates it if the user decides so.
        Updates gripper position
        :return: -> None
        """
        self._select_joint()
        self._update_positions()
        self._get_gripper_data()

    def position_control(self):
        """
        Checks controller's axis 0 and 1 and hat 0 in order to update X, Y and Z coordinates of the end effector
        Updates gripper position
        :return: -> None
        """
        x_axis = self.joystick.get_axis(0)
        y_axis = self.joystick.get_axis(1)
        z_axis = self.joystick.get_hat(0)

        # X Axis
        if x_axis > 0.8 and abs(self.axis.x+self._position_change_unit) <= self._max_pos:
            self.axis.x += self._position_change_unit
            time.sleep(self._position_change_delay)

        elif x_axis < -0.8 and abs(self.axis.x-self._position_change_unit) <= self._max_pos:
            self.axis.x -= self._position_change_unit
            time.sleep(self._position_change_delay)

        # Y Axis
        if y_axis < -0.8 and abs(self.axis.y + self._position_change_unit) <= self._max_pos:
            self.axis.y += self._position_change_unit
            time.sleep(self._position_change_delay)

        elif y_axis > 0.8 and abs(self.axis.y - self._position_change_unit) <= self._max_pos:
            self.axis.y -= self._position_change_unit
            time.sleep(self._position_change_delay)

        # Z Axis
        if z_axis[1] == 1 and abs(self.axis.z + self._position_change_unit) <= self._max_pos:
            self.axis.z += self._position_change_unit
            time.sleep(self._position_change_delay)

        elif z_axis[1] == -1 and abs(self.axis.z - self._position_change_unit) <= self._max_pos:
            self.axis.z -= self._position_change_unit
            time.sleep(self._position_change_delay)

        self._get_gripper_data()
        self._round_data(ndigits=2)

    def save_and_apply_changes(self):
        pass

    def control(self):
        """
        Gets the data of all Xbox Controller Events, selects controlling mode (Free mode or Position Mode)
        and runs its method accordingly
        :return: -> None
        """
        pygame.event.pump()
        if self.joystick.get_button(2):
            self._free_mode = False

        elif self.joystick.get_button(3):
            self._free_mode = True

        if self._free_mode:
            self.free_control()
        else:
            self.position_control()

        if self.check_apply_button():
            self.save_and_apply_changes()