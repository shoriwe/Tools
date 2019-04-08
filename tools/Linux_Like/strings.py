from re import finditer
from argparse import ArgumentParser


# Strings command
def strings(filename, min_len, max_len, encoding):
    with open(filename, 'rb') as file:
        # Actually this pattern give the best results (more simmilar to the strings cmd)
        pattern = ('[a-zA-Z0-9 :;\\\|?/!@#$&*+-[\](\){\}\^~_<>\'\"%%\t]{%s,%s}' % (min_len, max_len)).encode()
        for result in finditer(pattern, file.read()):
            try:
                yield result.group().decode(encoding)
            except Exception as e:
                yield result.group()


def main(args=None):
    if not args:
        parser = ArgumentParser()
        parser.add_argument('file', help='File to be processed')
        parser.add_argument('-n', '--min-len', dest='min', help='Minimum length of the word', default=4)
        parser.add_argument('-m', '--max-len', dest='max', help='Maximum length of the word', default=200)
        parser.add_argument('-e', '--encoding', dest='encoding', help='Encoding to decode results', default='utf-8')
        args = vars(parser.parse_args())

    for word in strings(args['file'], args['min'], args['max'], args['encoding']):
        print(word)
if __name__ == '__main__':
    main()