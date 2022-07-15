from Connections import Socket


class Transmitter(Socket):
    def __init__(self, host, port, HEADER=64, FORMAT='utf-8'):
        super().__init__(host, port, HEADER=HEADER, FORMAT=FORMAT)

    def console(self):
        self.socketSetup()
        while True:
            message = input("Please type your message: ")
            self.send_msg(message)
            response = self.recv_msg()
            print(response)


host = input("Please type host IP: ")
port = input("Please type host port: ")

transmitter = Transmitter(host, port)
