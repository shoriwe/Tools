from socket import socket
from time import sleep
# Adaptative recv
def get_response(client:socket, buffer_size):
    response = b''
    try:
        while True:
            buffer = client.recv(buffer_size)
            if len(buffer) < buffer_size:
                return response + buffer
            response += buffer
    except:
        return response
# Depurate the bytes, return b' ' if its len is 0 otherwise the client can enter in a input bucle
def depurate(bytes_input):
    if not len(bytes_input):
        return b' '
    else:
        return bytes_input
class Client:
    def __init__(self, host, port, address_family, protocol, max_buffer_size, input_formating, input_header, send_interval:int, default_data):
        self.__address = (host, port)
        self.__client = socket(address_family, protocol)
        self.__max_buffer_size = max_buffer_size
        # Put the input in a specific format like: format="le {}"; input = "car" ==> "le car"
        self.__input_formating = input_formating
        # Like >>>
        self.__input_header = input_header
        self.__sleep_interval = send_interval
        # only send this default data in the loop
        self.__default_data = default_data

    def __who_starts(self):
        self.__client.settimeout(2.5)
        welcome = get_response(self.__client, self.__max_buffer_size)
        if len(welcome):
            print(welcome.decode('utf-8'))
            return True

        else:
            print(b'Input bytes to try to recieve welcome msg'.decode('utf-8'))
            if self.__default_data:
                print(self.__default_data)
                self.__client.send(depurate(self.__default_data.encode('utf-8')))
            else:
                self.__client.send(depurate(input().encode('utf-8')))
            welcome = b'Response: ' + get_response(self.__client, self.__max_buffer_size) + b'\n###You send first###'
            print(welcome.decode('utf-8'))
        self.__client.settimeout(20)

    def __connection_handler(self):
        while True:
            sleep(self.__sleep_interval)
            if self.__default_data is None:
                msg = self.__input_formating.format(input(self.__input_header)).encode('utf-8')
                self.__client.send(msg)
            else:
                print('bytes')
                self.__client.send(self.__default_data.encode('utf-8'))
            print(get_response(self.__client, self.__max_buffer_size).decode('utf-8'))

    def connect(self):
        try:
            self.__client.connect(self.__address)
            self.__who_starts()
            self.__connection_handler()
        except Exception as e:
            print(e)