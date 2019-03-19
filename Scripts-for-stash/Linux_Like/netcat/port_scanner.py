from socket import socket, SOCK_STREAM, SOCK_DGRAM, AddressFamily
from threading import Thread
from time import sleep
from json import loads
from datetime import datetime


# Scanner class easy for imports
class Scanner:
    def __init__(self, host: str, family: AddressFamily, target_protocols: list, port_range: iter, max_n_threads: int):
        self.__host = host
        self.__family = family
        self.__target_protocols = target_protocols
        self.__port_range = port_range
        self.__max_n_threads = max_n_threads
        self.__active_threads = 0

        # [[TCP ports], [UDP ports]]
        self.__db = loads(open('./netcat/port_db.json').read())

    # Scan TCP protocol
    def tcp(self, family, port):
        sock = socket(family, SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((self.__host, port))
            # When the port is not in the  database
            try:
                print(('\n'.join([f'-{"TCP":<8} {value:<50} {port:<8}-' for value in self.__db[str(port)]])) + '\n' + (
                            '-' * 70) + '\n', end='')
            except:
                print(f'-{"TCP":<8} {"UNKNOW":<50} {port:<8}-\n' + ('-' * 70) + '\n', end='')
            sock.close()
        except:
            sock.close()
        self.__active_threads -= 1
        exit(-1)

    # Scan for UDP protocol
    def udp(self, family, port):
        sock = socket(family, SOCK_DGRAM)
        sock.settimeout(1)
        try:
            sock.connect((self.__host, port))
            sock.send(b'Data')
            response = sock.recv(10)

            # When the port is not in the database
            try:
                print(('\n'.join([f'-{"UDP":<8} {value:<50} {port:<8}-' for value in self.__db[str(port)]])) + '\n' + (
                        '-' * 70) + '\n', end='')
            except:
                print(f'-{"UDP":<8} {"UNKNOW - %s"%str(response) :<50} {port:<8}-\n' + ('-' * 70) + '\n', end='')

            sock.close()
        except:
            sock.close()
        self.__active_threads -= 1
        exit(-1)

    # Handler for each protocol
    def __handler(self, family, protocol):
        try:
            scan_function = getattr(self, protocol)
            for port in self.__port_range:
                while self.__active_threads >= self.__max_n_threads:
                    sleep(1)
                Thread(target=scan_function, args=(family, port)).start()
                self.__active_threads += 1
        except Exception as e:
            pass

    # Start scanning
    def scan(self):
        start_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
        print(f'\nScan started at {start_time}')
        print('Scanning', self.__host)
        print(f'Scanning protocols:', ', '.join([p.upper() for p in self.__target_protocols]))
        print('Port range:', self.__port_range)
        print()
        print('-' * 70)
        print(f'-{"Protocol":<8} {"Posible Services in that port":<50} {"port":<8}-\n', end='')
        print('-' * 70)
        for protocol in self.__target_protocols:
            Thread(target=self.__handler, args=(self.__family, protocol.lower())).start()
        while True:
            if self.__active_threads <= 0:
                sleep(3)
                if self.__active_threads <= 0:
                    break
            sleep(0.1)
        print(
            f'\nScan started at {start_time}\n{"Finished at":<15} {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")}')
