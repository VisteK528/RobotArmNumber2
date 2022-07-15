import socket
from time import sleep

class Socket:
    def __init__(self, host, port, HEADER=64, FORMAT='uft-8'):
        self.host = host
        self.port = port
        self.connected = False

        self._HEADER = HEADER
        self._FORMAT = FORMAT

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

    def recv_msg(self):
        data = b''
        msg_length = int(self.s.recv(self._HEADER).decode(self._FORMAT))
        data += self.s.recv(msg_length)
        return data

    def send_msg(self, msg: str):
        msg = msg.encode(self._FORMAT)
        msg_length = str(len(msg)).encode(self._FORMAT)
        msg_length += b' ' * (self._HEADER - len(msg_length))
        self.s.send(msg_length)
        self.s.send(msg)

class HandleConnection:
    def __init__(self, HEADER, FORMAT):
        self.HEADER = HEADER
        self.FORMAT = FORMAT

    def recv_msg(self, conn):
        data = b''
        msg_length = int(conn.recv(self.HEADER).decode(self.FORMAT))
        data += conn.recv(msg_length)
        return data

    def send_msg(self, conn, msg: str):
        msg = msg.encode(self.FORMAT)
        msg_length = str(len(msg)).encode(self.FORMAT)
        msg_length += b' ' * (self.HEADER - len(msg_length))
        conn.send(msg_length)
        conn.send(msg)

class Server(HandleConnection):
    def __init__(self, HEADER, FORMAT):
        super().__init__(HEADER=HEADER, FORMAT=FORMAT)
        print("[STARTING] Server is starting...")
        PORT = 33000
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, PORT)
        self.DISCONNECT_MESSAGE = "!DISCONNECT"

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        self.connected = False

    def start_host(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER}")
        conn, addr = self.server.accept()
        return conn, addr

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected   [ID] {ID}")

        self.connected = True
        while self.connected:
            msg_length = conn.recv(self._HEADER).decode(self._FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self._FORMAT)
                if msg == self.DISCONNECT_MESSAGE:
                    self.connected = False
                print(msg)
            conn.send("Msg received".encode(self._FORMAT))

        conn.close()
        return False

