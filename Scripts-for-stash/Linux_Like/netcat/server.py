from http.server import HTTPServer, SimpleHTTPRequestHandler
from socket import socket, AddressFamily, SocketKind, AF_INET, SOCK_STREAM, AF_INET6, SOCK_DGRAM
from os import chdir
from threading import Thread
from time import sleep


# Adaptative recv
def get_response(client: socket, buffer_size):
    response = b''
    try:
        while True:
            buffer = client.recv(buffer_size)
            if len(buffer) < buffer_size:
                return response + buffer
            response += buffer
    except:
        return response


# Get the destination for the requests socket proxy
# len = 50 header
# like: 127.0.0.1;12;AF_INET;SOCK_STREAM
# It use "host;port;address_family;protocol....data..."
def get_target_info(buffer):
    address_families = {'AF_INET': AF_INET, 'AF_INET6': AF_INET6}
    protocols = {'SOCK_STREAM': SOCK_STREAM, 'SOCK_DGRAM': SOCK_DGRAM}
    address = buffer.decode('utf-8').replace(' ', '').split(';')

    host = address[0]
    port = int(address[1])
    family = address_families[address[2]]
    protocol = protocols[address[3]]
    print([(host, port), family, protocol])
    return [(host, port), family, protocol]


# Depurate the bytes, return b' ' if its len is 0 otherwise the client can enter in a input bucle
def depurate(bytes_input):
    if not len(bytes_input):
        return b' '
    else:
        return bytes_input


# Handler for the SFTP Server
class SFTPServerHandler:
    def __init__(self, address, admin_username, admin_password, other_users: tuple):
        pass


# Handler for socket for reverse connections
class SocketHanlder:
    def __init__(self, client: socket, stdinput: staticmethod, stdoutput: staticmethod, max_recv_buffer: int,
                 sleep_interval: int):
        # Client socket
        self.__client = client
        # stdinput is a function  that returns bytes to send
        self.__input = stdinput
        # stdoutput is a function that do something with the input (input is bytes)
        self.__output = stdoutput
        # Max buffer limit
        self.__max_recv_buffer = max_recv_buffer
        # -i interval
        self.__sleep_interval = sleep_interval

    # Determine who starts the communication (who is going to send the first message)
    def __who_starts(self):
        self.__client.settimeout(5)
        welcome = get_response(self.__client, self.__max_recv_buffer)
        if len(welcome):
            return True

        else:
            self.__output(b'Input bytes to try to recieve welcome msg')
            self.__client.send(depurate(self.__input()))
            welcome = b'Response: ' + get_response(self.__client, self.__max_recv_buffer) + b'\n###You send first###'
            self.__output(welcome)
        self.__client.settimeout(20)

    def start(self):
        self.__who_starts()
        while True:
            msg = depurate(self.__input())

            sleep(self.__sleep_interval)
            self.__client.send(msg)

            response = get_response(self.__client, self.__max_recv_buffer)
            self.__output(response)


# Handler for the socket proxies
class ProxySocketHandler:
    def __init__(self, client, max_recv_buffer, sleep_time, sniff):
        self.__client = client
        self.__max_recv_buffer = max_recv_buffer
        self.__sleep_time = sleep_time
        self.__sniff = sniff

    def __connect_to_target(self, target_info):
        try:
            s = socket(*target_info[1:])
            s.connect(target_info[0])
            return s
        except Exception as e:
            print(e)
            return None

    def start(self):
        try:
            buffer = get_response(self.__client, self.__max_recv_buffer)
            target_info = get_target_info(buffer)
            target = self.__connect_to_target(target_info)

            # send welcome too the client
            target.settimeout(3)
            welcome = depurate(get_response(target, self.__max_recv_buffer))
            self.__client.send(welcome)
            target.settimeout(20)
            if self.__sniff:
                while True:
                    msg = depurate(get_response(self.__client, self.__max_recv_buffer))

                    target.send(msg)
                    response = depurate(get_response(target, self.__max_recv_buffer))

                    self.__client.send(response)
            else:
                while True:
                    msg = depurate(get_response(self.__client, self.__max_recv_buffer))
                    target.send(msg)
                    response = depurate(get_response(target, self.__max_recv_buffer))
                    self.__client.send(response)
        except Exception as e:
            print(e)


# Server class to hand -l command
class Server:
    def __init__(self, host: str, port: int, target_hosts: list, address_family: AddressFamily, protocol: SocketKind,
                 directory: str, max_number_connections: int, max_recv_buffer: int,
                 sleep_interval, input_header: str, input_formating: str, default_data, sniff: bool):
        self.__host = host
        self.__port = port
        # FOR SOCKET; Accept  the connection if the client side ip is in self.__target_hosts
        self.__target_hosts = target_hosts
        self.__address_family = address_family
        self.__protocol = protocol
        # Directory for HTTP server
        self.__directory = directory
        # For multy reverse connection
        self.__max_number_connecitons = max_number_connections
        # Max buffer size bigger number is equal no less loops to get a msg
        self.__max_recv_buffer = max_recv_buffer
        # Equivalent too -i of netcat
        self.__sleep_interval = sleep_interval
        # Like ">>>" or "shell>"
        self.__input_header = input_header
        # Put the input in a specific format like: format="le {}"; input = "car" ==> "le car"
        self.__input_formating = input_formating
        # Default data to send to the sockets (for listener)
        self.__default_data = default_data
        self.__sniff = sniff

        self.__address = (host, port)

    # HTTP server to serve in the port and directory you want
    def simple_http_server(self):
        try:
            chdir(self.__directory)
            server = HTTPServer((self.__host, self.__port), SimpleHTTPRequestHandler)
            server.serve_forever()
        except Exception as e:
            print(e)

    # Handler  for the reverse connection
    def __reverse_conneciton_handler(self, client, address, stdinput, stdoutpu):
        while True:
            connect_to_client = False
            if len(self.__target_hosts):
                if address[0] in self.__target_hosts:
                    connect_to_client = True
            else:
                connect_to_client = True
            if connect_to_client:
                print('Connection from:', address)
                try:
                    hanlder = SocketHanlder(client, stdinput,
                                            stdoutpu, self.__max_recv_buffer, self.__sleep_interval)
                    hanlder.start()
                except Exception as e:
                    print(address, e)
            client.close()

    # Reverse connection any that tries to connect
    def reverse_connection(self):
        if self.__default_data:
            input_func = lambda: self.__default_data.encode()
        else:
            input_func = lambda: self.__input_formating.format(input(self.__input_header)).encode()
        sock = socket(self.__address_family, self.__protocol)
        sock.bind(self.__address)
        sock.listen(1)
        while True:
            client, address = sock.accept()

            self.__reverse_conneciton_handler(client, address, input_func, lambda x:
            print(x.decode()))

    def __proxy_socket_handler(self, client: socket, address: tuple):
        connect_to_client = False
        if len(self.__target_hosts):
            if address[0] in self.__target_hosts:
                connect_to_client = True
        else:
            connect_to_client = True
        if connect_to_client:
            handler = ProxySocketHandler(client, self.__max_recv_buffer, self.__sleep_interval, self.__sniff)
            Thread(target=handler.start, ).start()

    def proxy_socket(self):
        server = socket(self.__address_family, self.__protocol)
        server.bind(self.__address)
        server.listen(self.__max_number_connecitons)
        while True:
            client, address = server.accept()
            self.__proxy_socket_handler(client, address)

## The server.py also needs
# Proxy HTTP
# FTP server
# SFTP server
# Socket tunneling
