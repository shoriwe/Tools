from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread


# Some kind of pind aproaching the ConnectionRefusedError exeption
class Ping:
    def __init__(self):
        # Only have this number of  threads active at the same time
        self.__max_number_of_threads = 500
        self.__active_threads = 0

        self.__alive_targets = []

    # Handler for thread each target
    def __ping_handler(self, target):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect((target, 80))
            self.__alive_targets.append(target)
        except Exception as e:
            if type(e) == ConnectionRefusedError:
                self.__alive_targets.append(target)
        s.close()
        del s
        self.__active_threads -= 1
        exit(-1)

    # Only a ping function
    def ping(self, targets):
        for target in targets:
            while self.__active_threads >= self.__max_number_of_threads:
                pass
            self.__active_threads += 1
            Thread(target=self.__ping_handler, args=([target])).start()
        while self.__active_threads > 0:
            pass

    def getalive(self):
        return self.__alive_targets

# Port Scanner handler
class PortScanner:
    def __init__(self, family, protocol, port_range):
        # IP family
        self.__family = family
        # UDP or TCP
        self.__protocol = protocol
        # Port range
        self.__port_range = port_range

        self.__ports = {}

        # Only have this number of  threads active at the same time
        self.__max_number_of_threads = 500
        self.__active_threads = 0

    def __target_handler(self, target, port):
        s = socket(self.__family, self.__protocol)
        s.settimeout(10)
        try:
            s.connect((target, port))
            if self.__protocol == SOCK_DGRAM:
                s.send(b'bytes')
                s.recv(1024)

            self.__ports[target].append(port)
        except:
            pass
        s.close()
        del s
        self.__active_threads -= 1
        exit(-1)

    # Scan all required ports of all targets
    def scan(self, targets):
        for target in targets:
            self.__ports[target] = []
            for port in self.__port_range:
                while self.__active_threads >= self.__max_number_of_threads:
                    pass
                self.__active_threads += 1
                Thread(target=self.__target_handler, args=([target, port])).start()
        while self.__active_threads > 0:
            pass

    def getports(self):
        return self.__ports

class Ports:
    def __init__(self):
        self.__ports = []

    # -p port ranges (Only scan specified ports)
    def portrange(self, ports):
        ranges = []
        for port in ports.split(','):
            if '-' in port:
                splited_port = port.split('-')
                ranges += list(range(int(splited_port[0]), int(splited_port[1])+1))
            else:
                ranges.append(int(port))
        self.__ports += ranges

    # -F (Fast (limited port) scan)
    def fast(self, n):
        self.__ports += [21, 22, 23, 80, 135, 139, 443, 445, 1000, 4444, 8080]

    def getports(self):
        return list(set(self.__ports))

class HostDiscovery:
    def __init__(self):
        self.__family = AF_INET
        self.__protocols = {}

        self.__ports = []
        self.__targets = []

        self.__results = {}

        self.__noports = False
        self.__noping = False

    # Can be only one
    def settargets(self, targets):
        ts = []
        for target in targets:
            if '*' == target.split('.')[-1]:
                splited_target = target.split('.')
                base = '.'.join(splited_target[:len(splited_target)-1])
                for number in range(256):
                    ts.append(base+'.'+str(number))
            else:
                ts.append(target)
        self.__targets += ts

    def setports(self, ports):
        self.__ports += ports

    # -sT (TCP connect scan)
    def enabletcp(self, n):
        if n:
            self.__protocols["SOCK_STREAM"] = SOCK_STREAM

    # -sU (UDP scans)
    def enableudp(self, n):
        if n:
            self.__protocols["SOCK_DGRAM"] = SOCK_DGRAM

    # -sn (No port scan)
    def noports(self, n):
        self.__noports = n

    # -Pn (No ping)
    def noping(self, n):
        self.__noping = n

    def scan(self):
        # Filter alive from down targets
        if not self.__noping:
            ping = Ping()
            ping.ping(self.__targets)
            self.__targets = ping.getalive()
        if not self.__noports:
            for protocol in self.__protocols.keys():
                portscanner = PortScanner(self.__family, self.__protocols[protocol], self.__ports)
                portscanner.scan(self.__targets)
                self.__results[protocol] = portscanner.getports()

        return self.__results