from socket import AF_INET6, AF_INET, SOCK_STREAM, SOCK_DGRAM, socket
from argparse import ArgumentParser
from logging import basicConfig, info, INFO, CRITICAL
from threading import Thread

## Options for implement
## Tunnel
# -P tunneling port
# -S tunneling  address


# Recieve function (recieve any size buffer)
def recv(client):
    buffer = b''
    while True:
        data = client.recv(1024)
        if len(data) < 1024:
            return buffer + data
        buffer += data


# Check who start sendind data
def checkTheyFirstSend(client, timeout):
    client.settimeout(5)
    try:
        data = recv(client)
        client.settimeout(timeout)
        return data
    except:
        client.settimeout(timeout)
        return False

# Handler for the connection tunnel
class TunnelHandler:
    pass
# Handler for the scanner
class ScannerHandler:
    def __init__(self):
        # Family of all teh socket taht are oging to be created
        self.__family = None
        # protocol of all the sockets that are going to  be created
        self.__protocol = None
        # Host
        self.__address = None
        # Ports as iter
        self.__ports = None
        # Results of the scan
        self.__active_ports = []
        # Useful for multi threading scan
        self.__active_connections = 0

    def setSocket(self, s: socket):
        self.__family = s.family
        self.__protocol = s.proto

    def setAddress(self, address: str):
        self.__address = address

    def setPort(self, *ports):
        self.__ports = ports

    # Start the scanner
    def start(self):
        for port in self.__ports:
            while self.__active_connections >= 100:
                pass
            Thread(target=self.connectionHandler, args=[socket(self.__family, self.__protocol), port]).start()
        while self.__active_connections > 0:
            pass
        for port in self.__active_ports:
            print('OPEN PORT', port)

    def connectionHandler(self, s, target_port):
        self.__active_connections += 1
        try:
            s.connect((self.__address, target_port))
            self.__active_ports.append(target_port)
        except:
            pass
        s.close()
        del s
        self.__active_connections -= 1


# Here we set in easy handling mode the options
class ConfigurationHandler:
    def __init__(self):
        self.__host = None
        self.__ports = None
        # Family of the socket
        self.__family = None
        # Protocol of the socket
        self.__protocol = None
        # Time out of the socket
        self.__timeout = None
        self.__mode = 'Client'  # Client by default

    ## Modular options
    # Set port with -p option
    def setports(self, ports):
        if len(ports):
            self.setPorts(ports)

    # Set address (host) with -s option
    def sethost(self, host):
        if len(host):  # Do not collapse with setHost option
            self.setHost(host)

    # Set host
    def setHost(self, host: str):
        if len(host):
            self.__host = host

    # Set the family of the socket
    def setFamily(self, family):
        self.__family = family

    # Set protocol of the socket: SOCK_STREAM, SOCK_DGRAM
    def setProtocol(self, protocol):
        self.__protocol = protocol

    # Set Timeout of the socket
    def setTimeout(self, timeout: float):
        self.__timeout = timeout

    # Set the veborse mode to print anything or print only errors
    def setVerbose(self, value: bool):
        if value:
            basicConfig(level=INFO, format='%(message)s')
        else:
            basicConfig(level=CRITICAL, format='%(message)s')

    # Set the mode to listen
    def setModeListen(self, value: bool):
        if value:
            self.__mode = 'Listen'

    # Set mode to scan
    def setModeScan(self, value: bool):
        if value:
            self.__mode = 'Scan'

    # Port setup
    def setPorts(self, ports):
        if len(ports):
            ports = ports.split(',')
            buffer = []
            for port in ports:
                if '-' in port:
                    splited_port = port.split('-')

                    buffer += list(range(int(splited_port[0]), int(splited_port[1])+1))
                else:
                    if port.isnumeric():
                        buffer.append(int(port))
            self.__ports = buffer

    ## Function that return processed data
    # Create the socket and return it
    def getSocket(self):
        s = socket(self.__family, self.__protocol)
        s.settimeout(self.__timeout)
        return s

    # return the mode of the session
    def getMode(self):
        return self.__mode

    # Return the address (host)
    def getHost(self):
        return self.__host

    # Return the port or the ports to be used by the handler
    def getPorts(self):
        return self.__ports


# Handler for socket as client and the tunnel
class ClientHandler:
    def __init__(self):
        # Socket for the server
        self.__socket = None
        self.__address = None
        self.__port = None

    def setSocket(self, s: socket):
        self.__socket = s

    def setAddress(self, address: str):
        self.__address = address

    def setPort(self, port):
        self.__port = port

    def start(self):
        self.__socket.connect((self.__address, self.__port))

    def connectionHandler(self):
        while True:
            # Check if we start sending
            welcome = checkTheyFirstSend(self.__socket, self.__socket.gettimeout())
            if welcome:
                info(welcome.decode('utf-8'))
            while True:
                input_buffer = input().encode('utf-8')
                self.__socket.sendall(input_buffer)
                response = recv(self.__socket)
                try:
                    info(response.decode('utf-8'))
                except:
                    # Some kind of check to not print a file content
                    if len(response) < 10000:
                        info(str(response))


# Handler for the listener
class ServerHandler:
    def __init__(self):
        # Socket for the server
        self.__socket = None
        self.__address = None
        self.__port = None

    def setSocket(self, s: socket):
        self.__socket = s

    # Set address (host) for the socket
    def setAddress(self, address: str):
        self.__address = address

    # Set the port of the connection
    def setPort(self, port):
        self.__port = port

    # Enable server mode
    def start(self):
        self.__socket.bind((self.__address, self.__port))
        self.__socket.listen(1)
        try:
            self.connectionHandler()
        except Exception as e:
            info(str(e))

    # Handler for the server session
    def connectionHandler(self):
        client, address = self.__socket.accept()
        welcome = checkTheyFirstSend(client, self.__socket.gettimeout())
        if welcome:
            info(welcome.decode('utf-8'))
        while True:
            input_buffer = input().encode('utf-8')
            client.sendall(input_buffer)
            response = recv(client)
            # Try to decode and print the response
            try:
                info(response.decode('utf-8'))
            except:
                # Some kind of check to not print a file content
                if len(response) < 10000:
                    info(str(response))


def main(args=None):
    # Modes and its classes
    modes = {'Listen': ServerHandler, 'Client': ClientHandler, 'Scan': ScannerHandler}
    if not args:
        parser = ArgumentParser()
        parser.add_argument('setHost', help='Set target host', nargs='?', default='')  # Implemented
        # Port or ports for the connection or scanner
        parser.add_argument('setPorts',
                            help='Port[s] to be used (when is scan mode; you can set ranges like 10-50 and multi values are comma "," separated)',
                            nargs='?', default='')
        # Set address family
        parser.add_argument('-6', help='Set address family to IPV6', dest='setFamily', action='store_const',
                            const=AF_INET6, default=AF_INET)  # Implemented
        # Set address protocol
        parser.add_argument('-u', help='Set address protocol to UDP', dest='setProtocol', action='store_const',
                            const=SOCK_DGRAM, default=SOCK_STREAM)  # Implemented
        # Server mode
        parser.add_argument('-l', '--listen', help='Listen for incoming connections', dest='setModeListen',
                            action='store_const', const=True, default=False)  # Implemented
        # Verbose mode
        parser.add_argument('-v', '--verbose', help='Verbose mode', dest='setVerbose', action='store_const', const=True,
                            default=False)  # Implemented
        # Timeout limit for connections
        parser.add_argument('-w', '--wait', help='Connection timeout', dest='setTimeout', default=3600,
                            type=float)  # Implemented
        # Set port[s] with an option
        parser.add_argument('-p', '--port', dest='setports', help='Set the port or  ports to be processed',
                            default='')  # Implemented
        # Set address (host) with an option
        parser.add_argument('-s', '--address', dest='sethost', help='Set host to be processed with an option',
                            default='')
        # Enable scanner mode
        parser.add_argument('-z', '--scan', dest='setModeScan', help='Set mode to scan', action='store_const',
                            const=True, default=False)
        args = vars(parser.parse_args())
    c = ConfigurationHandler()
    for key in args:
        getattr(c, key)(args[key])
    s = c.getSocket()
    mode = c.getMode()
    host = c.getHost()

    # Select one of the handlers; corresponding to the user options
    handler = modes[mode]()
    # Set the host target to the handler
    handler.setAddress(host)
    # Set the socket to be used by the handler
    handler.setSocket(s)
    handler.setPort(*c.getPorts())
    handler.start()


if __name__ == '__main__':
    main()
