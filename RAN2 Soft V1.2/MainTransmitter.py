from Connections import Client
from RemoteControl import RemoteControl


class Transmitter(Client):
    def __init__(self, host, port, HEADER=64, FORMAT='utf-8'):
        super().__init__(host, port, HEADER=HEADER, FORMAT=FORMAT)
        self.ADDR = (host, port)
        self.xbox_controller = RemoteControl()

    def console(self):
        self.conn = self.socket_connect(self.ADDR)

        while True:
            msg = int(input("Please select type of control:\n1)Console Input\n2)Xbox Controller Input\n"
                            "3)Quit\nYour choice: "))
            if msg == 1:
                print("Console Input Mode activated!")
                while True:
                    message = input("Please type your message or type 'Quit' to leave console input: ")
                    if message.lower() == 'quit':
                        break
                    response = self.send_msg_with_response(self.conn, message)
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
                            response = self.send_msg_with_response(self.conn, message)
                            print(response)

                        elif not free_mode:
                            message = f"False;{self.xbox_controller.axis.x};{self.xbox_controller.axis.y}" \
                                      f";{self.xbox_controller.axis.z}"
                            response = self.send_msg_with_response(self.conn, message)
                            print(response)

            elif msg == 3:
                break
            else:
                print("Invalid choice!")
            print()

        self.conn.close()


host = input("Please type host IP: ")
port = int(input("Please type host port: "))

transmitter = Transmitter(host, port)
transmitter.console()
