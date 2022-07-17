import socket

class HandleConnection:
    def __init__(self, HEADER, FORMAT):
        self.HEADER = HEADER
        self.FORMAT = FORMAT

    def socket_disconnect(self, conn):
        conn.close()

    def socket_connect(self, addr: tuple):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(addr)
        return conn

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

class Client(HandleConnection):
    def __init__(self, IP, PORT, HEADER, FORMAT):
        super().__init__(HEADER=HEADER, FORMAT=FORMAT)
        self.IP = IP
        self.PORT = PORT

        self.connected = False

class Server(HandleConnection):
    def __init__(self, HEADER, FORMAT):
        super().__init__(HEADER=HEADER, FORMAT=FORMAT)
        print("[STARTING] Server is starting...")

        self.DISCONNECT_MESSAGE = "!DISCONNECT"

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = self.server.getsockname()
        self.PORT = 5560
        self.ADDR =(self.IP, self.PORT)

        self.server.bind(self.ADDR)
        self.connected = False

    def start_host(self):
        self.server.listen(1)
        print(f"[LISTENING] Server is listening on {self.ADDR}")
        conn, addr = self.server.accept()
        return conn, addr

