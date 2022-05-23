import pygame
import time
pygame.init()

class XboxControl:
    def __init__(self):
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.j = [0 for x in range(6)]

        self.selected_joint = 1

        self.position_change_unit = 0.5
        self.position_change_delay = 0.025

    def check_set_pos_button(self):
        if self.joystick.get_button(0):
            return True
        return False

    def reset_positions(self):
        self.j = [0 for x in range(1, 6)]

    def select_joint(self):

        if 0 < self.selected_joint < 7:
            if self.joystick.get_button(5):
                if self.selected_joint != 6:
                    self.selected_joint += 1
                    time.sleep(0.2)

            if self.joystick.get_button(4):
                if self.selected_joint != 1:
                    self.selected_joint -= 1
                    time.sleep(0.2)
    def update_positions(self):
        pygame.event.pump()

        if -1 < self.j[self.selected_joint - 1] <= 360:
            if self.joystick.get_axis(5) > 0:
                if self.j[self.selected_joint - 1] != 360:
                    self.j[self.selected_joint - 1] += 2

            if self.joystick.get_axis(4) > 0:
                if self.j[self.selected_joint - 1] != 0:
                    self.j[self.selected_joint - 1] -= 2

    def position_btn_triggered(self):
        pygame.event.pump()
        if self.joystick.get_axis(5) > 0 or self.joystick.get_axis(4) > 0:
            current_pos = self.j[self.selected_joint - 1]
            n = 0
            while True:
                print(current_pos)
                pygame.event.pump()
                time.sleep(self.position_change_delay)
                if (self.joystick.get_axis(5) > 0) or (self.joystick.get_axis(4) > 0):
                    if -1 < current_pos <= 360:
                        if self.joystick.get_axis(5) > 0:
                            if current_pos != 360:
                                current_pos += self.position_change_unit

                        if self.joystick.get_axis(4) > 0:
                            if current_pos != 0:
                                current_pos -= self.position_change_unit
                else:
                    time.sleep(self.position_change_delay)
                    n += 1
                if n == 2:
                    self.j[self.selected_joint - 1] = current_pos
                    return

xbox = XboxControl()
while True:
    print(xbox.j, xbox.selected_joint)
    time.sleep(0.001)
    xbox.select_joint()
    xbox.position_btn_triggered()
    #print(xbox.j, xbox.selected_joint)


