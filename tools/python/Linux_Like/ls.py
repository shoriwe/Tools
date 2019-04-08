# Build in Python 3.7
# made by walogo
from argparse import ArgumentParser
from os import listdir, getcwd, stat, chdir
from os.path import isdir, join, getsize, getctime, islink
from stat import filemode
from sys import platform
from datetime import datetime


# Get extension of file
def get_extension(file):
    return file.split('.')[-1].upper()


# This function help because sometimes getsize return 0
def get_size_of(file):
    if isdir(file):
        size = 0
        for f in listdir(file):
            f_location = join(file, f)
            size += get_size_of(f_location)
        return size
    return getsize(file)


# Get the datetime of the creation of a file
def get_creation_date(file):
    try:
        if platform == 'win32':
            return datetime.fromtimestamp(getctime(file)).strftime('%Y %b %d %H:%M')
        else:
            s = stat(file)
            try:
                return datetime.fromtimestamp(s.st_ctime).strftime('%Y %b %d %H:%M')
            except:
                return datetime.fromtimestamp(s.st_mtime).strftime('%Y %b %d %H:%M')
    except:
        return 'UNKN OWU NK NOWUN'


# Get the permissions of a file chmod style
def get_permissions(file):
    try:
        return filemode(stat(file).st_mode)
    except:
        return '--UNKNOW--'


# Get the size of a file (sometimes the os.getsize return 0 this except that)
def getsize_join(folder):
    size_table = ['B ', 'kB', 'MB', 'GB', 'TB', 'PT', 'EB', 'ZB', 'YB']

    def size_of(file):
        try:
            size = get_size_of(join(folder, file))
            str_size = str(size)[:6]
            for number, metric in enumerate(size_table):
                if size < 100:
                    if '.' not in str_size:
                        if len(str_size + '.') <= 6:
                            str_size += '.'
                    while len(str_size) < 6:
                        str_size += '0'
                    return [size * (1000 * number + 1), str_size, metric]
                size = size / 1000
                str_size = str(size)[:6]
        except:
            return [0, 'UNKNOW', '  ']

    return size_of


# ls class
# Using a class let us to avoid global variables
class Ls:
    def __init__(self):
        self.__folder = None
        self.__files = None
        self.__processable = None

    # This is recursive printing function
    def folder_listing(self, folder, ntabs=0):
        for file in listdir(folder):
            file_location = join(folder, file).replace('\\', '/')
            try:
                if isdir(file_location):
                    print(('\t' * ntabs) + self.get_color(file_location))
                    self.folder_listing(file_location, ntabs + 1)
                else:
                    print(("\t" * (ntabs)) + self.get_color(file_location))
            except:
                print(("\t" * ntabs) + f"Permission denied {self.get_color(file_location)}")

    # Get the color of the given file
    # The colors used are the same a the original ls
    def get_color(self, file, recursive=False):
        # Directories Blues
        f_root = join(self.__folder, file)
        if recursive:
            f_root = file
        if isdir(f_root):
            return '\u001b[34m' + file + '\033[0m'
        # Symlinks Sky Blue
        elif islink(f_root):
            return '\033[94m' + file + '\033[0m'
        else:
            # More executable formats
            executables = ['0XE', '73K', '89K', 'A6P', 'AC', 'ACC', 'ACR', 'ACTM', 'AHK', 'AIR', 'APP', 'ARSCRIPT',
                           'AS',
                           'ASB', 'AWK', 'AZW2', 'BEAM', 'BTM', 'CEL', 'CELX', 'CHM', 'COF', 'CRT', 'DEK', 'DLD', 'DMC',
                           'DOCM', 'DOTM', 'DXL', 'EAR', 'EBM', 'EBS', 'EBS2', 'ECF', 'EHAM', 'ELF', 'ES', 'EX4',
                           'EXOPC',
                           'EZS', 'FAS', 'FKY', 'FPI', 'FRS', 'FXP', 'GS', 'HAM', 'HMS', 'HPF', 'HTA', 'IIM', 'IPF',
                           'ISP',
                           'JAR', 'JS', 'JSX', 'KIX', 'LO', 'LS', 'MAM', 'MCR', 'MEL', 'MPX', 'MRC', 'MS', 'MS', 'MXE',
                           'NEXE', 'OBS', 'ORE', 'OTM', 'PEX', 'PLX', 'POTM', 'PPAM', 'PPSM', 'PPTM', 'PRC', 'PVD',
                           'PWC',
                           'PYC', 'PYO', 'QPX', 'RBX', 'ROX', 'RPJ', 'S2A', 'SBS', 'SCA', 'SCAR', 'SCB', 'SCRIPT',
                           'SMM',
                           'SPR', 'TCP', 'THM', 'TLB', 'TMS', 'UDF', 'UPX', 'URL', 'VLX', 'VPM', 'WCM', 'WIDGET', 'WIZ',
                           'WPK', 'WPM', 'XAP', 'XBAP', 'XLAM', 'XLM', 'XLSM', 'XLTM', 'XQT', 'XYS', 'ZL9', 'ACTION',
                           'APK',
                           'APP', 'BAT', 'BIN', 'CMD', 'COM', 'COMMAND', 'CPL', 'CSH', 'EXE', 'GADGET', 'INF1', 'INS',
                           'INX', 'IPA', 'ISU', 'JOB', 'JSE', 'KSH', 'LNK', 'MSC', 'MSI', 'MSP', 'MST', 'OSX', 'OUT',
                           'PAF',
                           'PIF', 'PRG', 'PS1', 'REG', 'RGS', 'RUN', 'SCR', 'SCT', 'SHB', 'SHS', 'U3P', 'VB', 'VBE',
                           'VBS',
                           'VBSCRIPT', 'WORKFLOW', 'WS', 'WSF', 'WSH', 'PY', 'RB', 'JS', 'SH', 'HTML', 'PHP']

            # More archive formats
            archives = ['ECC', 'PAR', 'PAR2', 'REV', '7Z', 'S7Z', 'ACE', 'AFA', 'ALZ', 'APK', 'ARC', 'ARJ', 'B1', 'B6Z',
                        'BA', 'BH', 'CAB', 'CAR', 'CFS', 'CPT', 'DAR', 'DD', 'DGC', 'DMG', 'EAR', 'GCA', 'HA', 'HKI',
                        'ICE',
                        'JAR', 'KGB', 'LZH,LHA', 'LZX', 'PAK',
                        'PARTIMG', 'PAQ6', 'PAQ7', 'PAQ', 'PEA', 'PIM', 'PIT', 'QDA', 'RAR', 'RK', 'SDA', 'SEA',
                        'SEN', 'SFX', 'SHK', 'SIT', 'SITX', 'SQX', 'TARGZ', 'TGZ', 'TARZ', 'TARBZ2,', 'TBZ2', 'TARLZMA',
                        'TLZTARXZ', 'TXZ'
                , 'UCA', 'UHA', 'WAR', 'WIM', 'XAR', 'XP3', 'YZ1', 'ZIP,ZIPX', 'ZOO', 'ZPAQ',
                        'ZZ', 'BZ2', 'GZ', 'LZ', 'LZMA', 'LZO', 'RZ', 'SFARK', 'SZ', '?Q?', '?Z?', 'XZ',
                        'Z', 'Z', '??_', 'A,AR', 'CPIO', 'SHAR', 'LBR', 'LBR', 'ISO', 'LBR', 'MAR', 'SBX', 'TAR']

            images = ['PNG', 'GIF', 'JPG', 'JPEG', 'BMP', 'TIF', 'TIFF', 'EPS', 'RAW', 'CR2', 'ORF', 'SR2']

            # File extension (fe)
            fe = get_extension(file)
            # Executables Green
            if fe in executables:
                return '\u001b[32m' + file + '\033[0m'
            # Archives Red
            elif fe in archives:
                return "\033[1;31m" + file + '\033[0m'
            # Images Pink
            elif fe in images:
                return '\u001b[36m' + file + '\033[0m'
            # Devices Yellow
            else:
                return file

    # Return if the list is processable
    def isProcessable(self):
        return self.__processable

    ##  Set folder to be used
    def set_folder(self, folder):
        self.__folder = folder

    ## Directory listing
    # -a --all
    def all(self):
        self.__files = [[file, getsize_join(self.__folder)(file)] for file in listdir(self.__folder)]
        self.__processable = True

    # -R --recursive
    # It also print
    def recursive(self):
        iferror = self.__folder
        try:
            actual = getcwd()
            chdir(self.__folder)
            self.__folder = getcwd()
            chdir(actual)
        except:
            self.__folder = iferror

        self.folder_listing(self.__folder)
        self.__files = []
        self.__processable = False

    # -A --almost-all
    def almostall(self):
        self.__files = [[file, getsize_join(self.__folder)(file)] for file in listdir(self.__folder) if '.' != file[0]]
        self.__processable = True

    # -d --directory
    def directory(self):
        self.__files = [self.__folder, getsize(self.__folder)]
        self.__folder = ''
        self.__processable = True

    ##  Process listing
    # -F --classify
    def classify(self):
        sorting_key = lambda l: isdir(join(self.__folder, l[0]))
        self.__files.sort(key=sorting_key)

    # -r --reverse
    def reverse(self):
        self.__files.reverse()

    # -s --size
    def size(self):
        sorting_key = lambda l: l[1][0]
        self.__files.sort(key=sorting_key)

    ## Printers
    def list(self):
        print("Total", len(self.__files))
        for file in self.__files:
            print(get_permissions(join(self.__folder, file[0])), file[1][1] + file[1][2],
                  get_creation_date(join(self.__folder, file[0])),
                  self.get_color(file[0]))

    ## Like default but sep=', '
    def commas(self):
        print(*[self.get_color(f[0]) for f in self.__files], sep=', ')

    # Default printing
    def default(self):
        print(*[self.get_color(f[0]) for f in self.__files])


## Pythonista default stash ls arguments

# add_argument('-1', '--one-line', action='store_true', help='List one file per line')
#
# add_argument('-a', '--all', action='store_true', help='do not ignore entries starting with .')
#
# add_argument('-l', '--long', action='store_true', help='use a long listing format')
#
# add_argument('files', nargs='*', help='files to be listed')
def main(args=None):
    ls = Ls()
    # ArgumentParses

    # Arguments of the programm
    # This let use the script as a module
    if not args:
        parser = ArgumentParser()
        # When the user wants to specify a folder
        parser.add_argument('folder', help='Folder to be listed', nargs='?', default=getcwd().replace('\\', '/'))
        # Listing arguments
        parser.add_argument('-a', '--all', help='List all files including hidden', dest='directory listing',
                            action='store_const', const='all', default='almostall', required=False)
        parser.add_argument('-A', '--almost-all', help='List all files exeption of hidden',
                            dest='directory listing', action='store_const', const='almostall', default='almostall',
                            required=False)
        parser.add_argument('-d', '--directory', help='Use current working direcoty only as list',
                            dest='directory listing', action='store_const', const='directory', default='almostall',
                            required=False)
        parser.add_argument('-R', '--recursive', help='Recursive folder listing', dest='directory listing',
                            action='store_const', const='recursive', default='almostall', required=False)
        # Processing arguments
        parser.add_argument('-F', '--classify', help='Classify between folders and files', dest='classify',
                            action='store_const', const=True, default=False, required=False)
        parser.add_argument('-S', help='Sort by size', dest='size', action='store_const', const=True,
                            default=False, required=False)
        parser.add_argument('-r', '--reverse', help='reverse the listed results Note that this always run at the end',
                            dest='reverse', action='store_const', const=True, default=False, required=False)
        # Printing arguments
        parser.add_argument('-l', help='Listing printer', dest='print', action='store_const', const='list',
                            default='default', required=False)
        parser.add_argument('-m', help='Comma separated values', dest='print', action='store_const', const='commas',
                            default='default', required=False)

        args = vars(parser.parse_args())

    # Set the folder to be processed
    ls.set_folder(args['folder'])
    # Set the file listing
    getattr(ls, args['directory listing'])()

    # deleting the alredy used variables help with processing
    del args['folder']
    del args['directory listing']

    # When it is recurisve it is hard to implement the listing function
    if ls.isProcessable():
        print_function = getattr(ls, args['print'])
        del args['print']

        for p_function in args.keys():
            if args[p_function]:
                getattr(ls, p_function)()
        print_function()


if __name__ == '__main__':
    main()
