import socket
from time import sleep

class Socket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = False
        self.custom_cmd_recv = False

    def socketDisconnect(self):
        #self.s.send(str.encode("EXIT"))
        self.s.close()

        self.connected = False
    def socketKill(self):
        #self.s.send(str.encode("KILL"))
        self.s.close()

        self.connected = False
    def socketSetup(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.connected = True

    def socketReset(self):
        if self.connected:
            #self.s.send(str.encode("EXIT"))
            self.s.close()
            self.connected = False
            sleep(0.5)
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # client initialization
            self.s.connect((self.host, self.port))  # client connecting to robot server
            self.connected = True

        elif not self.connected:
            self.socketSetup()

    def sendCommand(self, command):
        self.s.send(str(command).encode())
        reply = self.s.recv(1024).decode()
        return reply

    def dataTransfer_inside(self, message):
        try:
            self.s.send(str.encode(message))
            reply = self.s.recv(1024).decode('utf-8')

            self.custom_cmd_recv_data = reply
            self.custom_cmd_recv = True
        except Exception as e:
            print(e)
            pass