from http.server import SimpleHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from os import chdir
from argparse import ArgumentParser

# Modular handler
class Modes:
    def simple(self, host, port, directory):
        chdir(directory)
        server = HTTPServer((host, port), SimpleHTTPRequestHandler)
        server.serve_forever()

    def threads(self, host, port, directory):
        chdir(directory)
        server = ThreadingHTTPServer((host, port), SimpleHTTPRequestHandler)
        server.serve_forever()

def main(args=None):
    if not args:
        modes_by_name = f"Available modes are: {', '.join(list(dir(Modes)[26:]))}"
        parser = ArgumentParser()
        parser.add_argument('-mode', help=modes_by_name, dest='mode', default='simple')
        parser.add_argument('-d', '--directory', help='Directory to serve', dest='directory', default='./')
        parser.add_argument('host', help='Host ip for the server')
        parser.add_argument('port', help='Port for the server', type=int, default=80, nargs='?')
        args = vars(parser.parse_args())
    s = Modes()
    getattr(s, args['mode'])(args['host'], args['port'], args['directory'])

if __name__ == '__main__':
    main()