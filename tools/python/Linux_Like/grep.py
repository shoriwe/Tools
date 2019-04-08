from re import search
from argparse import ArgumentParser
from os.path import isfile


class GREP:
    def __init__(self):
        self.__res = None
        self.__lines = None
        self.__encoding = None

    # Regex operation
    def __regex(self):
        for regular_expression in self.__res:
            for line in self.__lines:
                searched = search(regular_expression.strip().encode(), line)
                if searched:
                    try:
                        print(line.strip().decode(self.__encoding))
                    except:
                        print(line.strip())

    def search(self):
        self.__regex()

    # Encoding for the decode operation after regex
    def set_encoding(self, encoding):
        self.__encoding = encoding

    # Set regular expression iterable
    def set_res(self, res: iter):
        self.__res = res

    # Get regular expressions from file
    def set_res_from_file(self, filename):
        with open(filename, 'r') as file:
            self.__res = file.readlines()
            file.close()

    # Set a file to be processed by regex operation
    def set_file(self, filename):
        with open(filename, 'rb') as file:
            self.__lines = file.readlines()
            file.close()

    # Raw text to  be processed by regex operation
    def set_text(self, text, sep=None):
        if type(text) != bytes:
            text = text.encode()
        self.__lines = text.split(sep)


def main(args=None):
    # When args not called
    if not args:
        parser = ArgumentParser()
        parser.add_argument('-f', '--file=', help='File containing regex statements (one per line)', dest='refile',
                            default=False)
        parser.add_argument('-t', '--from-text', help='Grep the text', dest='fromtext', default=False)
        parser.add_argument('-s', '--separator', help='Separator for the -t', dest='separator', default='\n')
        parser.add_argument('-e', '--encoding', help='Encoding for decode results of regex', dest='encoding',
                            default='utf-8')
        parser.add_argument('-r', '--regular-expression', help='Regex statatement', dest='re', nargs='*', default=False)
        parser.add_argument('-F', '--File=', help='File to be processed by regex', dest='file', nargs='*',
                            default=False)
        args = vars(parser.parse_args())
    g = GREP()

    # Take text of file to regex
    if isfile(args['file'][0]):
        g.set_file(args['file'][0])
    else:
        # Raw text as regex input
        if args['fromtext']:
            g.set_text(args['fromtext'], args['separator'])
        else:
            print("What do you want?\nGive me something to regex")
            exit(-1)
    # Regular expression to  be used (can be more than one)
    if args['re']:
        g.set_res(args['re'])
    else:
        # Take regular expression from text file (one per line)
        if args['refile']:
            g.set_res_from_file(args['refile'])
    # Set encoding for the decode operation of the results
    g.set_encoding(args['encoding'])
    # Processed the regex operation
    g.search()


if __name__ == '__main__':
    main()
