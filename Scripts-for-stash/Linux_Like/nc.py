from argparse import ArgumentParser
from socket import AF_INET, AF_INET6, SOCK_STREAM, SOCK_DGRAM
from netcat import Server, Client, Scanner


# Return family as AF_INET or AF_INET6
def get_family(family):
    if family.upper() == 'IPV4':
        return AF_INET
    return AF_INET6


# Use the protocol as SOCK_STREAM or SOCK_DGRAM
def get_protocol(protocol):
    if protocol.upper() == 'TCP':
        return SOCK_STREAM
    return SOCK_DGRAM


# Transform the arguments None to pythons None
def defaultdata(data):
    if len(data):
        return data
    return None


# Transform the argument rangen "1-8" to python range "range(1,9)"
def get_range(string_range):
    splited_string_range = string_range.split('-')
    return range(int(splited_string_range[0]), int(splited_string_range[1]) + 1)


# If you want to add a new option try to di it like follows
class Options:
    def __init__(self, args):
        self.__args = args
        self.__handler = None

    def server_object_handler(self):
        args = self.__args
        self.__handler = Server(args['host'], args['port'], args['targets'], get_family(args['family']),
                                get_protocol(args['protocol']),
                                args['directory'], args['maxbind'], args['buffersize'], args['interval'],
                                args['input-header'], args['formating'], defaultdata(args['defaultdata']),
                                args['sniff'])

    def listener(self):
        self.server_object_handler()
        self.__handler.reverse_connection()

    def http(self):
        self.server_object_handler()
        self.__handler.simple_http_server()

    def proxy(self):
        self.server_object_handler()
        self.__handler.proxy_socket()

    def client(self):
        args = self.__args
        self.__handler = Client(args['host'], args['port'], get_family(args['family']), get_protocol(args['protocol']),
                                args['buffersize'], args['formating'], args['input-header'], args['interval'],
                                defaultdata(args['defaultdata']))
        self.__handler.connect()

    def scan(self):
        args = self.__args
        if '*' == args['host'][0][-1]:
            base = '.'.join(args['host'][0].split('.')[:len(args['host'][0].split('.')) - 1])
            for number in range(1, 256):
                try:
                    host = base + '.' + str(number)
                    self.__handler = Scanner(host, get_family(args['family']), [args['protocol']],
                                             get_range(args['port-range']), args['max-n-threads'])
                    self.__handler.scan()
                except:
                    pass
        self.__handler = Scanner(args['host'][0], get_family(args['family']), [args['protocol']],
                                 get_range(args['port-range']),
                                 args['max-n-threads'])
        self.__handler.scan()


def main(args=None):
    if not args:
        parser = ArgumentParser()

        parser.add_argument('host', help='Host to use can be ipv4 or ipv6', default='127.0.0.1', nargs='*')
        parser.add_argument('port', help='Port to use', default=4444, nargs='*')

        # Variables
        # Variables can't output bools because this is the way we identify options like scan, client, proxy...
        # if you need something similar to your new function use 0 and 1 as booleans for if statements
        parser.add_argument('-ss', '--sniff', help='Help sniff the input process', dest='sniff', default=0,
                            action='store_const',
                            const=1)
        parser.add_argument('-af', '--address-family', help='IPV6 or IPV4', dest='family', default='IPV4')
        parser.add_argument('-ap', '--address-protocol', help='TCP or UDP', dest='protocol', default='TCP')
        parser.add_argument('-dd', '--default-data', help='Default data to send throught sockets', default='',
                            dest='defaultdata')
        parser.add_argument('-t', '--target-hosts',
                            help='Only accept connections from this hosts (for listener and proxy)',
                            dest='targets', type=list, nargs='*', default=[])
        parser.add_argument('-d', '--http-directory-root', help='Base root for the http server', default='./',
                            dest='directory')
        parser.add_argument('-ih', '--input-header', help='Like >>> when you tipe something', dest='input-header',
                            default='>>>')
        parser.add_argument('-if', '--input-formating',
                            help='The formating for the input like "{}-12" => "{}".format(input())', dest='formating',
                            default='{}')
        parser.add_argument('-b', '--max-buffer-size', help='Size of recv buffer', default=1024, type=int,
                            dest='buffersize')
        parser.add_argument('-mc', '--max-bind-connections', help='Max number of incoming connections', type=int,
                            dest='maxbind',
                            default=10)
        parser.add_argument('-pr', '--port-range', help='The port ranges for the scan default is 1-1000',
                            default='1-1000',
                            dest='port-range')
        parser.add_argument('-mt', '--max-threads',
                            help='Maximum number of threads to be active at the same time in a port scanning default is 200',
                            default=500, dest='max-n-threads', type=int)
        parser.add_argument('-sl', '--slow-send', help='Set a time to wait betwen send intervals (seconds)',
                            dest='interval',
                            default=0, type=int)

        # Options note that only type bool count as options
        parser.add_argument('-l', '--listener',
                            help='Bind connection for and communicate throught socket also works for reverse connection',
                            dest='listener', default=False,
                            action='store_const', const=True)
        parser.add_argument('-p', '--socket-proxy',
                            help='Proxy with sockets send outgoing connection with the header "127.0.0.1;12;AF_INET;SOCK_STREAM":50 to make a connection betwen target and host note that you don\'t need to specify any time only in the first message',
                            dest='proxy', const=True, default=False, action='store_const')
        parser.add_argument('-http', '--http-server', help='Starts a http server in the address specified', dest='http',
                            const=True,
                            default=False, action='store_const')
        parser.add_argument('-s', '--scan',
                            help='Scan for ports of an specified target * at the for any target in all the range',
                            dest='scan', const=True, default=False, action='store_const')
        args = vars(parser.parse_args())
    o = Options(args)
    reversed_keys = list(reversed(list(args.keys())))
    for key in reversed_keys:
        if type(args[key]) == bool:
            if args[key]:
                getattr(o, key)()
                exit(-1)
    getattr(o, 'client')()


if __name__ == '__main__':
    main()