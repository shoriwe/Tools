from requests import get
from re import finditer
from argparse import ArgumentParser
from os import getcwd, mkdir
from os.path import join
from ftplib import FTP
from threading import Thread


# Extract all usefull urls of the content of other
def get_urls(content):
    pattern = 'href="[a-zA-Z0-9#./:-_]+"'.encode()
    for result in finditer(pattern, content):
        yield result.group().decode()[6:len(result.group()) - 1]


class WGET:
    def __init__(self):
        self.__urls = None
        self.__urls_bases = None
        self.__ftp_client = None
        self.__auth = ['anonymous', 'anonymous']
        self.__recursive = False
        self.__debug = True
        self.__used_urls = {}

    # When the protocol is http
    # When recursive == True
    def __http_download(self, url, url_base, actual_folder=getcwd(), maximum_deep=2, target=None):

        # This is usefull when use recursive except url re-use
        if not self.__used_urls.setdefault(url, False):
            # hash to create folder and .html file
            url_hash = str(hash(url))
            # Put the url into used urls
            self.__used_urls[url] = url_hash
            # Get the content of the url
            url_content = get(url, auth=tuple(self.__auth)).content

            # check if it is html or a generic file
            if b'<html' in url_content and b'</html' in url_content and '.php' not in url:
                # Sometimes a url with file extension redirect to a html page this extract the file from that page
                if not target or target in url:
                    # like when File:<file_name/file_hash>
                    if ':' in url:
                        # Verify it is a file and not html
                        if '.' in url.split('/')[-1]:
                            splited = url.split('/')[-1].split('.')
                            if len(splited) < 3:
                                format = splited[-1]
                                try:
                                    target = format[:format.index('?')]
                                except:
                                    target = format
                    if self.__debug:
                        print('-' * maximum_deep, 'html', url_hash, actual_folder, url)
                    # Using folder recurssion we avoid cd command
                    actual_folder = join(actual_folder, url_hash)
                    # make dir for html
                    mkdir(actual_folder)
                    # save the html
                    with open(join(actual_folder, str(hash(url))) + '.html', 'wb') as file:
                        file.write(url_content)
                        file.close()
                    if self.__recursive and maximum_deep:
                        for child_url in get_urls(url_content):
                            # Avoid urls with // usually are http://url.com
                            if '//' not in child_url:
                                try:
                                    # Try to create url from actual url
                                    new_url = join(url, child_url).replace('\\', '/')
                                    # Recussion
                                    self.__http_download(new_url, url_base, actual_folder=actual_folder,
                                                         maximum_deep=maximum_deep - 1, target=target)
                                except:
                                    # create url from base
                                    if child_url[0] == '/':
                                        child_url = child_url[1:]
                                    new_url = url_base + child_url
                                    # Recurssion
                                    self.__http_download(new_url, url_base, actual_folder=actual_folder,
                                                         maximum_deep=maximum_deep - 1, target=target)
            # Download the file that is not html
            else:
                if self.__debug:
                    print('-' * maximum_deep, 'file', url_hash, actual_folder, url)
                filename = url.split('/')[-1]
                try:
                    filename = filename[:filename.index('?')]
                except:
                    pass
                with open(join(actual_folder, filename), 'wb') as file:
                    file.write(url_content)
                    file.close()

    # Downloader for ftp server
    def __ftp_requests(self, file, location=getcwd()):
        if self.__debug:
            print('Downloading:', file)
        try:
            # When is file raise error but wehn is dir it not
            dir_listing = list(self.__ftp_client.mlsd(format(file), facts=['type']))
            reference_hash = str(hash(file))
            # Avoid cd command
            mkdir(join(location, reference_hash))
            location = join(location, reference_hash)
            # Start recurssion
            if self.__recursive:
                for result in dir_listing:
                    # When file listed is directory
                    if result[1]['type'] == 'dir':
                        self.__ftp_requests(join(file, result[0]).replace('\\', '/'), location)
                    else:
                        file_location = join(location, result[0])
                        self.__ftp_client.retrbinary('RETR {}'.format(join(file, result[0]).replace('\\', '/')),
                                                     open(file_location, 'wb').write)
        except Exception as e:
            self.__ftp_client.retrbinary('RETR {}'.format(file),
                                         open(join(location, file.split('/')[-1]).replace('\\', '/'), 'wb').write)

    # Handler, usefull for threading
    def __download_hanldrer(self, url, number):
        # When downloading from http protocol http:// or https://
        if 'http' in url[:4]:
            self.__http_download(url, self.__urls_bases[number])
        # When downloading from ftp protocol ftp://
        else:
            ## GET the host, port and start directory
            if 'ftp://' in url:
                host = url[6:]
                self.__ftp_client = FTP()
                if host.count('/'):
                    file = '.' + host[host.index('/'):]
                    host = host.split('/')[0]
                    if ':' in host:
                        address = tuple(host.split(':'))
                        self.__ftp_client.connect(address[0], int(address[1]))
                    else:
                        self.__ftp_client = FTP(host[:host.index('/')], 21)
                else:
                    file = './'
                    if ':' in host:
                        address = tuple(host.split(':'))
                        self.__ftp_client.connect(address[0], int(address[1]))
                    else:

                        self.__ftp_client.connect(host, 21)

                # Login once
                self.__ftp_client.login(*self.__auth)
                # Start doenloading
                self.__ftp_requests(file)
            else:
                pass

    # Default download from ftp and html
    # Download the file in the url
    def download(self):
        for number, url in enumerate(self.__urls):
            Thread(target=self.__download_hanldrer, args=(url, number)).start()

    # Set a url
    def set_url(self, urls):
        self.__urls = urls
        print(urls)
        self.__urls_bases = []
        for url in urls:
            self.__urls_bases.append('/'.join(url.split('/')[:3]))
            if '/' != self.__urls_bases[-1][-1]:
                self.__urls_bases[-1] += '/'

    # Set recursive to True
    # -r --recursive
    def set_recursive(self, status):
        self.__recursive = status

    # Set username for authentications
    def set_user(self, username):
        self.__auth[0] = username

    # Set password for the username
    def set_passw(self, password):
        self.__auth[1] = password

    def turn_off_debug(self, status):
        self.__debug = False


## Need to implement:
# mirror

def main(args=None):
    if not args:
        parser = ArgumentParser()
        parser.add_argument('url(s)', help='URL for the requests need to start with [http://, https:// or ftp://]',
                            nargs='+')
        parser.add_argument('-r', '--recursive', help='Turn on recursive option (download url inside other urls)',
                            action='store_const', dest='set_recursive', const='set_recursive', default=False)
        parser.add_argument('--user=', help='Username for authentication (http, https, ftp)', dest='set_user',
                            default='anonymous')
        parser.add_argument('--password=', help='Password for authentication (http, https, ftp)', dest='set_passw',
                            default='anonymous')
        parser.add_argument('--debug-off', help='Turn off the debug (Don\'t print anything)', dest='turn_off_debug',
                            default=False)
        args = vars(parser.parse_args())
    w = WGET()
    w.set_url(args['url(s)'])
    del args['url(s)']
    for argument in args.keys():
        if args[argument]:
            getattr(w, argument)(args[argument])
    w.download()


if __name__ == '__main__':
    main()
