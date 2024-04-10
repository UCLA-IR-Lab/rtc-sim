import redis

class Redis:
    def __init__(self, type, address, port, us_path, password, database):
        self._address = address
        self._port = port
        self._us_path = us_path
        self._password = password
        self._database = database
        if type == 0:
            self._redis = self.connect_tcp()
        else:
            self._redis = self.connect_us()
        
    def connect_tcp(self):
        return redis.Redis(host=self._address, port=self._port, password=self._password, db=self._database)
    
    def connect_us(self):
        return redis.Redis(unix_socket_path=self._us_path, password=self._password, db=self._database)
    
    def set_timer(self, data):
        self._redis.set('timer', data)
        
    def get_timer(self):
        return int(self._redis.get('timer'))