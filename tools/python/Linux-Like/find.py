from os.path import join, getctime, isdir, getsize
from os import walk, access, W_OK, R_OK, X_OK, stat, getcwd, listdir
from sys import platform
from datetime import datetime
from threading import Thread
from argparse import ArgumentParser
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
        # Filters to apply to the search
        self.__filters = []
        # Actions to be exectud to results
        self.__actions = []

    ## Setup
    # Setup the starting point for the search
    def startpoint(self, start_point):
        self.__start_point = start_point

    # Setup The name filter
    # Seach for files by ignoring it's lower or upper cases chars wirth regex
    def setName(self, name):
        if name:
            # Make it that can match  upper or lower cases4
            self.__name = r''.join(f'[{char.upper()}{char.lower()}]' if char != '*' else '(.*)' for char in name)
            self.__filters.append(self.__search_name)

    # Set the iname filter to search files by its literal name regex
    def setIname(self, iname):
        if iname:
            self.__name = r''.join(iname)
            self.__filters.append(self.__search_iname)

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

    ## Filters (conditions)
    # Search by name ignoring lower or upper
    # -name pattern
    def __search_name(self, path, value):
        # We don't need to use  path because only  we are going to regex value
        if fullmatch(self.__name, value):
            return value

    # Search by name using lower and upper
    # -iname pattern
    def __search_iname(self, path, value):
        # Is the same function as search_name only change the regex specified before
        self.__search_name(path, value)

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
        pass

    # Search for permissions if file/folder
    # -perm mode
    def __search_perm(self, path, value):
        pass

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

    # filter handler
    def __filter_handler(self, folder_group):
        # Pass the folder group for all the filters that were selected
        for filter_ in self.__filters:
            folder_group = self.__filter_function_handler(filter_, folder_group)
        return folder_group

    # Start find function
    def start(self):
        results = walk(self.__start_point)
        buffer = []
        # Filtering process
        print("------Searching with your conditions")
        for folder_group in results:
            buffer.append(self.__filter_handler(folder_group))
        print("------Printing results")
        for path, folder_group, file_group in buffer:
            for folder in folder_group:
                print(join(path, folder).replace('\\', '/'))
            for file in file_group:
                print(join(path, file).replace('\\', '/'))
        if len(self.__actions) > 0:
            print("------Doing programmed actions")

        # Actions to results
        pass


basicConfig(level=INFO, format='%(message)s')
f = Find()
f.startpoint('./../')
f.setSize('<1M')
f.setType('d')
f.setWrite(1)
f.setExe(1)
f.setRead(1)
f.start()
