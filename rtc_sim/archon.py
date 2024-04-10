import socket

class Archon:
    def __init__(self, address, port, timeout=1) -> None:
        self._address = address
        self._port = port
        self._timeout = timeout
        self.connect()
        
    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(self._timeout)
        self.client.connect((self._address, self._port))
        
    def write(self, message):
        message = message.encode('ascii') + b'\n'
        self.client.sendall(message)
        
    def read(self):
        value = b''
        delimiter = b'\n'
        while delimiter not in value:
            data = self.client.recv(32)
            if not data:
                return None
            value += data
            
        return value
    
    def close(self):
        self.client.close()
        
    def decode(self, data) -> str:
        data = data.decode().strip('\n')
        data = data[9:]
        
        return data
    
    def get_timer(self):
        self.write('>01TIMER')
        timer = self.read()
        timer = int(self.decode(timer), 16)
        
        return timer