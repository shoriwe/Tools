from os.path import join, isdir, getsize, abspath
from os import walk, access, W_OK, R_OK, X_OK, stat, remove
from shutil import rmtree
from argparse import ArgumentParser, RawTextHelpFormatter
from logging import info, INFO, basicConfig
from re import fullmatch
from sys import platform

# This is for user check
if platform != 'win32':
    from pwd import getpwuid


class Find:
    def __init__(self):
        self.__start_point = None
        # Regex applicable to  iname or name
        self.__name = None
        # User name to search for
        self.__owner = None
        # Size and mode to search it
        self.__size = None
        # Type of the wanted file
        self.__type = None
        # Group of file
        self.__group = None
        # Filters to apply to the search
        self.__filters = []
        # Action to be exectud to results
        self.__action = None

    ## Setup
    # Setup the starting point for the search
    def startpoint(self, start_point):
        self.__start_point = start_point

    # Setup The iname filter
    # Seach for files with a unprocessed regex
    def setIname(self, iname):
        if iname:
            # Make it that can match  upper or lower cases4
            self.__name = iname
            self.__filters.append(self.__search_name)

    # Set the name filter to search files by its literal name regex changing "*" for (.*)
    def setName(self, name):
        if name:
            self.__name = name.replace('*', '(.*)')
            self.__filters.append(self.__search_name)

    # set user for search for files owned  by a specific user
    def setUser(self, username):
        if username:
            self.__owner = username
            self.__filters.append(self.__search_owner)

    # For the search of empty files
    def setEmpty(self, size):
        if type(size) in (int, float):
            self.setSize('=0c')

    # Se the size wanted for a  file
    def setSize(self, size):
        if size:
            if size[0] not in '<>=!~':
                size = '~' + size
            if size[-1] not in 'ckMG':
                size += 'c'

            self.__size = size
            self.__filters.append(self.__search_size)

    # Set the type is file or directory
    def setType(self, ftype):
        if ftype:
            self.__type = ftype
            self.__filters.append(self.__search_type)

    # Filter files that can be read by actual user
    def setRead(self, value):
        if value:
            self.__filters.append(self.__search_readable)

    # Filter files that can be executed by the actual user
    def setExe(self, value):
        if value:
            self.__filters.append(self.__search_executable)

    # Filter files that can be writed by this user
    def setWrite(self, value):
        if value:
            self.__filters.append(self.__search_writeable)

    # Filter files by it's group
    def setGroup(self, group):
        if group:
            self.__group = group
            self.__filters.append(self.__search_group)

    ## Set actions values
    # activate delete action
    def setDelete(self, value):
        if value:
            self.__action = self.__delete
        else:
            self.__action = self.__printf

    # Set verbose mode
    def setVerbose(self, value):
        if value:
            basicConfig(level=INFO, format='%(message)s')

    ## Filters (conditions)
    # Search by name using a python regex
    # -name pattern
    def __search_name(self, path, value):
        # We don't need to use  path because only  we are going to regex value
        if fullmatch(self.__name, value):
            return value

    # Search  by its owner
    # -user uname
    def __search_owner(self, path, value):
        # This filter work in any liux like os
        if platform != 'win32':
            # Check the user owner is the same of the wanted
            if getpwuid(stat(join(path, value)).st_uid).pw_name == self.__owner:
                return value
        else:
            # Windows do not support pwd
            return value

    # Search for empty file/folder
    # -empty
    def __search_empty(self, path, value):
        self.__search_size(path, value)

    # Search if file is executable or folder is searchable by current user
    # -executable
    def __search_executable(self, path, value):
        try:
            info(f"Checking if {join(path, value)} is executable")
            if access(join(path, value), X_OK):
                info(f"{join(path, value)} is executable")
                return value
        except Exception as e:
            info(str(e))

    # File correspond to a specific group
    # -group gname
    def __search_group(self, path, value):
        if platform != 'win32':
            if getpwuid(stat(join(path, value)).st_gid).pw_name == self.__group:
                return value
        else:
            info('This function is not implemented for windows')
            return value

    # Search if file is readable
    # -readable
    def __search_readable(self, path, value):
        try:
            info(f"Checking if {join(path, value)} is readable")
            if access(join(path, value), R_OK):
                info(f"{join(path, value)} is readable")
                return value
        except Exception as e:
            info(str(e))

    # Search for file size
    # -size n[cwbkMG]
    def __search_size(self, path, value):
        try:
            multipliers = {'c': 1, 'k': 1024, 'M': 1024 ** 2, 'G': 1024 ** 3}

            multiplier = multipliers.setdefault(self.__size[-1], 1)
            size_ = int(self.__size[1:-1])
            value_size = getsize(join(path, value))
            conditions = {'<': value_size / multiplier < size_,
                          '>': value_size / multiplier > size_,
                          '=': value_size / multiplier == size_,
                          '!': value_size / multiplier != size_,
                          '~': (size_ + (1024 / multiplier)) >= int(value_size / multiplier) and int(
                              value_size / multiplier) >= (size_ - (1024 / multiplier))}
            if conditions[self.__size[0]]:
                return value
        except Exception as e:
            info(str(e))

    # Search for type of file
    # -type [df]
    def __search_type(self, path, value):
        try:
            # Identify if wanted target is the same of this file (value)
            if {'d': True, 'f': False}[self.__type] == isdir(join(path, value)):
                return value
        except:
            pass

    # Seach for writeable for current user
    # -writable
    def __search_writeable(self, path, value):
        try:
            if access(join(path, value), W_OK):
                return value
        except Exception as e:
            info(str(e))

    ## Actions for results
    # Delete all results
    def __delete(self, path, value):
        try:
            if isdir(join(path, value)):
                rmtree(join(path, value))
            else:
                remove(join(path, value))
            print(f"Deleted -- {abspath(join(path, value))}")
        except Exception as e:
            info(str(e))

    def __printf(self, path, value):
        print(abspath(join(path, value)))

    ## Handlers
    # Handler for filter functions
    def __filter_function_handler(self, filter_, folder_group):
        path = folder_group[0]
        buffer = [path]
        # for group  in ([folders], [files])
        for group in folder_group[1:]:
            group_buffer = []
            for value in group:
                condition_result = filter_(path, value)
                if condition_result:
                    group_buffer.append(condition_result)
            buffer.append(group_buffer)
        return buffer

    # Handler for acitons functions
    def __action_function_handler(self, action_, folder_group):
        path = folder_group[0]
        # for group  in ([folders], [files])
        for group in folder_group[1:]:
            for value in group:
                action_(path, value)

    # action handler
    def __action_handler(self, folder_group):
        info(f"Action session for {str(folder_group)}")
        self.__action_function_handler(self.__action, folder_group)

    # filter handler
    def __filter_handler(self, folder_group):
        # Pass the folder group for all the filters that were selected
        for filter_ in self.__filters:
            info(f"Filtering session for {str(folder_group)}")
            folder_group = self.__filter_function_handler(filter_, folder_group)
        return folder_group

    # Start find function
    def start(self):
        info("Find process started")
        results = walk(self.__start_point)
        buffer = []
        # Filtering process
        for folder_group in results:
            buffer.append(self.__filter_handler(folder_group))
        if self.__action:
            for folder_group in buffer:
                self.__action_handler(folder_group)

        # Actions to results
        pass


def main(args=None):
    if not args:
        parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
        parser.add_argument('-name', dest='setName', help='Search for file/folder name using a python processed regedx (change "*" for "(.*)")',
                            default=False)
        parser.add_argument('-iname', dest='setIname',
                            help='Search for file/folder with a python unprocessed regex', default=False)
        parser.add_argument('startpoint', help='Folder to start the search')
        parser.add_argument('-uname', dest='setUser', help='Search by file owner', default=False)
        parser.add_argument('-empty', dest='setEmpty', help='Search for  empty files and folders (0 bytes size)',
                            default=False, action='store_const', const=True)
        parser.add_argument('-size', dest='setSize',
                            help="Search file by its size using  this sintax \n" \
                                 "[operator][size][metric] like '<10c'\n" \
                                 "this will search for files under 10 bytes.\n\n" \
                                 "Available operators are:\n" \
                                 "'~' --- files with near size to the specified\n" \
                                 "'<' --- files with lower size than the spesicied\n" \
                                 "'>' --- files with higher size than the specified\n" \
                                 "'=' --- files with the same size as the  specified\n\n" \
                                 "Available metrics are:\n" \
                                 "'c' --- size as bytes\n" \
                                 "'k' --- size as kilobytes\n" \
                                 "'M' --- size as megabytes\n" \
                                 "'G' --- size as Gigabytes", default=False)
        parser.add_argument('-type', dest='setType',
                            help="Available file types are:\n" \
                                 "d --- directory\n" \
                                 "f --- file (only a file with or not with extension)",
                            default=False)
        parser.add_argument('-readable', dest='setRead', help='Filter files that are readable by current user',
                            default=False, action='store_const', const=True)
        parser.add_argument('-writeable', dest='setWrite', help='Filter files that are writeable by current user',
                            default=False, action='store_const', const=True)
        parser.add_argument('-executable', dest='setExe', help='Filter files that are executable by current user',
                            default=False, action='store_const', const=True)
        parser.add_argument('-group', dest='setGroup', help='Filter by group', default=False)

        parser.add_argument('-delete', dest='setDelete',
                            help='Delete all results (use with precaution this will not ask you for every file)',
                            action='store_const', const=True, default=False)
        parser.add_argument('-verbose', dest='setVerbose', help='Verbose mode', action='store_const', const=True, default=False)
        args = vars(parser.parse_args())
    find = Find()
    for key in args.keys():
        getattr(find, key)(args[key])
    find.start()

if __name__ == '__main__':
    main()
