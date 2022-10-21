import socket

class Client():
    def __init__(self, host, port):
        self.HEADER = 256
        self.PORT = int(port)
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = str(host)
        self.ADDR = (self.SERVER, self.PORT)

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    def send(self, msg):
        try:
            message = msg.encode(self.FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            echo = self.client.recv(2048).decode(self.FORMAT)
            print(echo)
            return(echo)
        except Exception as e:
            return(str(e))
    
    def disconnect(self):
        self.send(self.DISCONNECT_MESSAGE)


