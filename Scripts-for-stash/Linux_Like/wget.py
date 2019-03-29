from argparse import ArgumentParser
from os import getcwd, mkdir
from os.path import join
from re import finditer, search
from time import sleep
from requests import get
from logging import basicConfig, info, error, CRITICAL, INFO

# Download a file to target output file if specified or it's proper filename
def download(filename, content):
    with open(filename, 'wb') as output:
        output.write(content)
        output.close()

# Extract all the urls from the content of one
def getURLs(content):
    raw_results = finditer(r'((href)|(src))="[^ #]+"'.encode('utf-8'), content)
    urls = list(map(lambda u: u.group().decode('utf-8').replace('href="', '').replace('src="', '').replace('"', ''),
                    raw_results))
    return urls

# Modular handler for wget
class WGETHandler:
    def __init__(self):
        # URLs aldery dowloaded
        self.__usedURLs = []

        ### Variables set by Functions
        # url to be processed
        self.__url = None
        # Output file
        self.__output_file = None
        # Base url for local urls (wget is going to try it's own if you want)
        self.__base = None
        self.__function = None
        # Recursive Download of a site
        self.__recursive = None
        #  Only make a map of a site
        self.__spider = None
        # The deep the recursion download and the spider maping can get
        self.__deep = None
        # Tries per url  request
        self.__tries = None
        # Wait time between request
        self.__wait = None
        # Debug level
        self.__level = None

    # Set the url to be processed
    def setURL(self, url: str):
        self.__url = url

    # Set the deepness of the spidering or recursive download
    def setDeep(self, n: int):
        self.__deep = n

    # set time to be waited between resquests
    def setWait(self, t: float):
        self.__wait = t

    # set the max number of tries per url  request
    def setTries(self, tries: int):
        self.__tries = tries

    # set recursive to a value
    def setRecursive(self, value: bool):
        self.__recursive = value

    # set default output file
    def setOutputFile(self, file):
        self.__output_file = file

    # Set debug level to quiet
    def setQuiet(self, value: bool):
        if value:
            self.__level = CRITICAL

    # Set debug to verbose
    def setVerbose(self, value: bool):
        if value:
            self.__level = INFO

    # Set the spidering
    def setSpider(self, value: bool):
        self.__spider = value

    # Set base url for child urls download
    def setBaseURL(self, url):
        if url:
            self.__base = url
        else:
            if self.__url[-1] != '/':
                ref = self.__url + '/'
            else:
                ref = self.__url
            # Get base if no one was given
            self.__base = search(r'\w{3,5}://(.+)\.\w{1,6}/', ref).group()

    # Get the name of the download
    def getname(self, url, directory, isHTML):
        # PHP arguments
        if self.__output_file and not self.__recursive:
            return self.__output_file
        else:
            full_filename = url.split('/')[-1]

            if isHTML:

                if '.php' not in full_filename and '.html' not in full_filename:
                    filename = full_filename + '.html'
                else:
                    splited_filename = full_filename.split('.')
                    filename = splited_filename[0]
                    end = '.html'
                    for number, f in enumerate(splited_filename[1:]):
                        if 'php?' in f:
                            args = ''.join(splited_filename[1:][number:]).replace('.', '-')
                            end = f'?{args[4:]}.php'
                            break
                    filename = filename + end
            else:
                filename = full_filename
        return join(directory, filename.replace(';', '_').replace(':', '--'))

    # Spidering function
    def spider(self, url, deep, start=None):
        if not start:
            start = deep
        difference = start - deep
        try:
            if deep > 0:
                r = get(url)
                # Debugging
                info(f'{"-"*difference}{url}')
                content = r.content
                urls = getURLs(content)
                for u in urls:
                    if '/' == u[0]:
                        u = self.__base[:len(self.__base) - 1] + u
                    self.spider(u, deep - 1, start)
        except Exception as e:
            error(str(e))

    # Request for download, can be used for recursive and for single file download
    def request(self, url, deep, directory=getcwd()):
        for n in range(self.__tries):
            try:
                if deep > 0:
                    sleep(self.__wait)
                    # This help by not redownload a url
                    self.__usedURLs.append(url)
                    r = get(url)
                    content = r.content
                    # Useful!; if this is not none probably the file is html or php
                    isHTML = search(r'<((script)|(html)|([?]php))>(.+)</(.+)>'.encode(), content)

                    # Name of the file corresponding to the url  and it's format
                    filename = self.getname(url, directory, isHTML)

                    download(filename, content)
                    info(f'File {filename} downloaded')
                    if self.__recursive and deep > 1:
                        # Directory name
                        directory_name = filename.split('.')[0]
                        # this help by not doing cd command
                        current_dir = join(directory, directory_name)
                        if deep > 1:
                            try:
                                mkdir(current_dir)
                            except:
                                pass
                            info(f'Directory {current_dir} created')
                        # Extract all urls inside the content of the file
                        urls = getURLs(content)
                        for url in urls:
                            if '//' != url[:2]:
                                if '/' == url[0]:
                                    url = self.__base[:len(self.__base) - 1] + url
                                if url not in self.__usedURLs:
                                    info('Processing {}'.format(url))
                                    self.request(url, deep - 1, current_dir)
                    break
            except Exception as e:
                error(f'Error with {url}\n{str(e)}')

    def start(self):
        if self.__level:
            level = self.__level
        else:
            level = INFO
        if self.__spider:
            log_format = '%(message)s'
        else:
            log_format = '%(asctime)s:%(levelname)s:%(message)s'
        basicConfig(level=level, filename=self.__output_file, format=log_format)
        if self.__spider:
            self.spider(self.__url, self.__deep)
        else:
            self.request(self.__url, self.__deep)

# Main function to execute wget
def main(args=None):
    if not args:
        parser = ArgumentParser()
        parser.add_argument('setURL',
                            help='URL for the requests need to start with [http://, https:// or ftp://]')  # Implemented
        # output file
        parser.add_argument('-o', '--output-file=', dest='setOutputFile',
                            help='Destination of the download URL by default is the original file name',
                            default=None)  # Implemented
        # Debug mode
        parser.add_argument('-v', '--verbose', help='Debug anything', dest='setVerbose', action='store_const',
                            const=True,
                            default=None)  # Implemented
        # Don't print or log nothing
        parser.add_argument('-q', '--quiet', help='Debug only warings', dest='setQuiet', action='store_const',
                            const=True,
                            default=None)  # Implemented
        # Set a base URL for all server linked like /images/image.png with base url it will be requested as http://baseurl/images/image.png
        parser.add_argument('-B', '--base=', help='The base for / urls', default=None, dest='setBaseURL')  # Implemented
        # Max number of tries per url
        parser.add_argument('-t', '--tries=', dest='setTries', help='Max number of tries per url', default=1,
                            type=int)  # Implemented
        # Spidering
        parser.add_argument('--spider', dest='setSpider', default=False, action='store_const', const=True,
                            help='Spidering; make a map from the website')  # Implemented
        # Time to wait between responses
        parser.add_argument('-w', '--wait=', dest='setWait', help='Max number of seconds waited between responses',
                            type=float,
                            default=0)  # Implemented
        # Like cloning a website but nearly to wrong
        parser.add_argument('-r', '--recursive', help='Turn on recursive option (download url inside other urls)',
                            action='store_const', dest='setRecursive', const=True, default=False)  # Implemented
        # The deep that the spider and recursive download can reach
        parser.add_argument('-d', '--deep', dest='setDeep', help='Deepness in the spidering or recursive',
                            default=2, type=int)  # Implemented
        args = vars(parser.parse_args())
    w = WGETHandler()
    # Modular configuration
    for key in args:
        getattr(w, key)(args[key])
    w.start()


if __name__ == '__main__':
    main()
