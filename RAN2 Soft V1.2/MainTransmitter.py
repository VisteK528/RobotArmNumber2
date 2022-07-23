from Connections import Client
from RemoteControl import RemoteControl
import os


class Transmitter(Client):
    """
    Class Transmitter handles all connectivity between remote desktop and local RaspberryPi4 which
    directly drives the Arm.
    """
    def __init__(self, host: str, port: int, HEADER=64, FORMAT='utf-8'):
        super().__init__(host, port, HEADER=HEADER, FORMAT=FORMAT)
        self._ADDRESS = (host, port)
        self.xbox_controller = RemoteControl()

    def console(self):
        """
        Remote Console
        :return: -> None
        """
        self.connection = self.socket_connect(self._ADDRESS)

        while True:
            os.system('cls')
            msg = int(input("Please select type of control:\n1)Console Input\n2)Xbox Controller Input\n"
                            "3)Quit\nYour choice: "))
            if msg == 1:
                print("Console Input Mode activated!")
                while True:
                    message = input("Please type your message or type 'Quit' to leave console input: ")
                    if message.lower() == 'quit':
                        break
                    response = self.send_msg_with_response(self.connection, message)
                    print(response)
            elif msg == 2:
                print("Xbox Controller Input activated!")
                while True:
                    free_mode = self.xbox_controller.control()

                    if free_mode is not None:
                        if free_mode:
                            message = "True"
                            for joint in self.xbox_controller.j:
                                message += ";"
                                message += str(joint)
                            response = self.send_msg_with_response(self.connection, message)
                            print(response)

                        elif not free_mode:
                            message = f"False;{self.xbox_controller.axis.x};{self.xbox_controller.axis.y}" \
                                      f";{self.xbox_controller.axis.z}"
                            response = self.send_msg_with_response(self.connection, message)
                            print(response)

            elif msg == 3:
                break
            else:
                print("Invalid choice!")

        self.connection.close()


host = input("Please type host IP: ")
port = int(input("Please type host port: "))

transmitter = Transmitter(host, port)
transmitter.console()
