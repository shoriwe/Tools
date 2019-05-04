import ftplib
from argparse import ArgumentParser
# Function to download files
def download(filename):
    # This works for retrbinary()
    def write_bytes(btes):
        with open(filename, 'wb') as file:
            file.write(btes)
            file.close()
    return write_bytes
# FTP session handler
class FTP:
    def __init__(self):
        self.__session = ftplib.FTP()
        self.__address = [None, None]
        self.__mode = True
    ## Setup options
    #  Interactively change mode
    def changemode(self, args):
        if not args:
            mode = input('Do you want a pasv connection Y/n').strip()
            if not len(mode) or 'y' in mode.lower():
                # PASV mode
                mode = True
            else:
                # ACTV mode
                mode = False
        else:
            mode = {'PASV':True, 'ACTV':False}[args[0]]
        # Stablish the mode
        self.__session.set_pasv(mode)
    def HOST(self, value):
        self.__address[0] = value
    def PORT(self, value):
        self.__address[1] = value
    ## Commands implemented
    # Login into the server interactively
    def login(self, args):
        # Login as anonymous
        if '-a' in args:
            self.__session.login()
        # When we login as a specific user
        elif len(args) == 3:
            self.__session.login(args[1], args[2])
        # Interactive mode
        else:
            while True:
                print('Interactive login')
                # Try to log in until we got it
                try:
                    # When we only provide a username
                    if len(args) < 2:
                        username = input('Username: ').strip()
                    else:
                        username = args[1]
                    password = input('Password: ').strip()
                    self.__session.login(username, password)
                    print('Logged in')
                    break
                except:
                    print('Login failed')
    # ls command ftp implementation
    def ls(self, args):
        args[0] = 'LIST'
        self.other(args)
    # cd command
    def cd(self, args):
        args[0] = 'CWD'
        self.other(args)
    # Connect to target if no one was specified before
    def open(self, args):
        # Interactive
        if not args or len(args) <= 1:
            args = ['open'] + input('to:').strip().split(' ')
            # When no port is provided we use 21 as default
        if len(args) <= 2:
            args.append(21)
        host, port = args[1], int(args[2])
        self.__session.connect(host, port)
        print(self.__session.welcome)

    def rename(self, args):
        # argv mode
        if len(args) == 3:
            old_name = args[1]
            new_name = args[2]
        else:
            # Interactive mode
            if len(args) == 1:
                old_name = input('Old filename:').strip()
            if len(args) <= 2:
                new_name = input('New filename: ').strip()
        # Send request for change filename
        self.__session.sendcmd(f'RNFR {old_name}')
        # Send new filename
        print(self.__session.sendcmd(f'RNTO {new_name}'))

    # multiple puts
    def mput(self, args):
        for arg in args[1:]:
            # this is only a loop operation of put
            try:
                self.put([None, arg]) # by default put only accept iterables
            except Exception as e:
                print(e)
    # quit; exit from the program when quit is called
    def quit(self, args):
        try:
            self.other(args)
        except Exception as e:
            print(e)
        exit(-1)
    # Classic upload command
    def put(self, args):
        # File object to get bytes
        file = open(args[1], 'rb')
        # Send the bytes of the file object
        response = self.__session.storbinary(f'STOR {args[1]}', file)
        file.close()
        print(response)
    # Classic download command in ftp
    def get(self, args):
        # In this case args is filename
        filename = args[1].replace('\\', '/').split('/')[-1]
        self.__session.retrbinary(f'RETR {args[1]}', download(filename))
    # execute any other command
    def other(self, args):
        # Except not implemented cmds
        try:
            cmd = ' '.join(args)
            if 'ls' in args[0][:3].lower() or 'list' in args[0].lower():
                print(self.__session.retrlines(cmd))
            else:
                print(self.__session.sendcmd(cmd))
        except Exception as e:
            print(e)
    # Remove file or directory (directory recursively)
    def rm(self, args):
        # Remove Tree
        if '-r' in args:
            # Do not send this argument
            args.remove('-r')
            args[0] = 'RMDA'
        # Remove file
        else:
            args[0] = 'DELE'
        self.other(args[:2])
    # Remove empty directory
    def rmdir(self, args):
        args[0] = 'RMD'
        self.other(args)
    # Make directory command
    def mkdir(self, args):
        args[0] = 'MKD'
        self.other(args)
    def start(self):
        # Connect to server if arguments was provided in argv
        if all(self.__address):
            self.open(['open',*self.__address])
        # Start interactive session
        while True:
            cmd = input('ftp>').strip()
            # Never send empty data
            if not len(cmd):
                cmd = 'NOOP'
            # Always store the cmd splited
            cmd = cmd.split(' ')
            # Depureate spaces
            cmd = list(filter(len, cmd))
            # if the command was implemented
            try:
                getattr(self, cmd[0])(cmd)
            except Exception as e:
                print(e)
                # Try to send it as a normal cmd
                self.other(cmd)
# main function to execute the script
def main(args=None):
    if not args:
        parser = ArgumentParser()
        parser.add_argument('HOST', help='Host ip')
        parser.add_argument('PORT', help='HOST port', default=21, type=int)
        parser.add_argument('-A', help='Use active mode', default=False, action='store_const', const=['ACTV'], dest='changemode')
        parser.add_argument('-p', help='Use pasv mode', default=False, action='store_const', const=['PASV'], dest='changemode')
        args =  vars(parser.parse_args())
    # FTP session handler
    ftp = FTP()
    for key in args.keys():
        if args[key]:
            getattr(ftp, key)(args[key])
    ftp.start()
if __name__ == '__main__':
    main()