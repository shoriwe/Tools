from socket import AF_INET, SOCK_DGRAM, socket


def myip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 8080))
    ip, port = s.getsockname()
    s.close()
    return ip


def main():
    print(myip())


if __name__ == '__main__':
    main()
