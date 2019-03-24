from nmap import HostDiscovery, TargetSpecification, Ports, database
from argparse import ArgumentParser
from json import dumps


class Processing:
    def __init__(self, results: dict):
        self.__results = results

    # terminal print
    def termprint(self):
        for protocol in self.__results:
            print('PROTOCOL: {}'.format(protocol))
            for target in self.__results[protocol]:
                print('\tTARGET: {}'.format(target))
                for port in self.__results[protocol][target]:
                    if database.setdefault(str(port), False):
                        print('\t\tPORT: {}; Pos_Protocols: {}'.format(port, ', '.join(database[str(port)])))
                    else:
                        print('\t\tPORT: {} {}'.format(port, 'UNKNOW'))

    # like nmap [host] > outfile.txt
    def normaloutput(self, filename):
        with open(filename, 'w') as output:
            for protocol in self.__results:
                output.write('PROTOCOL: {}\n'.format(protocol))
                for target in self.__results[protocol]:
                    output.write('\tTARGET: {}\n'.format(target))
                    for port in self.__results[protocol][target]:
                        if database.setdefault(str(port), False):
                            output.write('\t\tPORT: {} {} \n'.format(port, database[str(port)]))
                        else:
                            output.write('\t\tPORT: {} {}\n'.format(port, 'UNKNOW'))
            output.close()

    # -oJ filespec (XML output)
    def jsonoutput(self, filename):
        with open(filename, 'w') as output:
            output.write(dumps(self.__results))
            output.close()


def main(args=None):
    if not args:
        parser = ArgumentParser()

        # Target specification
        parser.add_argument('target[s]', help='Target[s] to scan', nargs='*')
        parser.add_argument('-iL', dest='inputfromlist', help='-iL filename; Get targets from file; one per line')
        parser.add_argument('--exclude', help='--exclude target,[target2]..; Remove this targets from targets',
                            nargs='*', type=list)
        parser.add_argument('--excludefile',
                            help='--excludefile filename; Exclude all the targets in a file; one per line')
        ## add new Target specification down here

        # Port specification
        parser.add_argument('-p', dest='portrange', help='-p port ranges (Only scan specified ports)', default='1-1000')
        parser.add_argument('-F', dest='fast', help='Fast port scanning', default=False, action='store_const',
                            const=True)
        ## add new port options down here

        # Options
        parser.add_argument('-sT', dest='enabletcp', help='-sT (TCP connect scan)', default=False, action='store_const',
                            const=True)
        parser.add_argument('-sU', dest='enableudp', help='-sU (UDP scans)', default=False, action='store_const',
                            const=True)
        parser.add_argument('-Pn', dest='noping', help='Consider all targets as alive', default=False,
                            action='store_const', const=True)
        parser.add_argument('-sn', dest='noports', help='Do not scan ports', default=False, action='store_const',
                            const=True)
        ## add more options down here

        # Output options
        parser.add_argument('-oN', dest='normaloutput', help='Normal output like "nmap [host] > out.txt"')
        parser.add_argument('-oJ', dest='jsonoutput', help='Store in json file')

        args = vars(parser.parse_args())
    # Target processing handler
    ts = TargetSpecification()
    ts.settargets(args['target[s]'])
    # Port processing handler
    ps = Ports()

    keys_list = list(args.keys())
    first_port_option_index = None
    for number, key in enumerate(keys_list[1:]):
        if key == 'portrange':
            first_port_option_index = number + 1
            break
        if args[key]:
            getattr(ts, key)(args[key])
    first_option_index = None
    for number, key in enumerate(keys_list[first_port_option_index:]):
        if key == 'enabletcp':
            first_option_index = number + first_port_option_index
            break
        if args[key]:
            getattr(ps, key)(args[key])

    targets = ts.gettargets()
    ports = ps.getports()

    # Host handler
    hs = HostDiscovery()
    hs.settargets(targets)
    hs.setports(ports)
    for key in keys_list[first_option_index:]:
        if key == 'normaloutput':
            break
        getattr(hs, key)(args[key])
    results = hs.scan()

    # Do something with the resulted scan
    processing = Processing(results)
    if args['jsonoutput']:
        processing.jsonoutput(args['jsonoutput'])
    elif args['normaloutput']:
        processing.normaloutput(args['normaloutput'])
    else:
        processing.termprint()


if __name__ == '__main__':
    main()
