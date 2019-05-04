from paramiko import Transport, SSHClient, AutoAddPolicy
from socket import socket, AF_INET, SOCK_STREAM
import re


def nolimit_recv(session):
    btes = b''
    while True:
        try:
            data = session.recv(1024)
            if len(data) < 1024:
                return btes + data
            btes += data
        except:
            return btes


def create_connection(address):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        s.connect(address)
        return s
    except Exception as e:
        print('Connection could not be made', e, sep='\n')
        exit(-1)


class Client:
    def __init__(self, host, mode):
        self.__mode = mode
        self.__username, self.__address = list(
            map(lambda x: x if ':' not in x else (x.split(':')[0], int(x.split(':')[1])), host.split('@')))
        self.__password = None
        self.__session = None

        self.__transport = Transport(create_connection(self.__address))

    def __authenticate(self):
        self.__password = input(self.__username + '@' + ':'.join([str(x) for x in self.__address]) + '\'s password: ')
        self.__transport.connect(username=self.__username, password=self.__password)
        self.__handler()

    def __command(self):
        self.__session.get_pty(term='vt100', width=10, height=10)
        self.__session.invoke_shell()

    def __handler(self):
        self.__session = self.__transport.open_session()
        self.__command()

    def run(self):
        self.__authenticate()