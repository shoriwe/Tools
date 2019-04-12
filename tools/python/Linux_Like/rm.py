from os import rmdir, remove, walk, listdir
from os.path import join, isdir
from logging import INFO, basicConfig, info
from argparse import ArgumentParser
from sys import platform
# Handler for the rm operation
class RM:
    def __init__(self):
        # Interactive function to use
        # By default always remove file without asking
        self.__interctive = lambda x:True
        # File to be removed
        self.__file = None
        # is the file a folder?
        self.__is_file_folder = None

        # For the interactive interval function
        self.__interval_limit = None
        # The reference for the intervals
        self.__interval_memory = 0

        # Function to remove the target
        self.__remove_function = None

        # Preservation vars
        self.__preserve = None
        self.__base = None
        self.__base_list = None
    # Set the file that is going to be erased
    def setFile(self, filename):
        self.__file = filename
    # Put intercative funtion intervals
    def setInterval(self, interval):
        self.__interval_limit = interval
        self.__interctive = self.interval
    # Put the intercative function as complete interactive
    def setInteractive(self, value):
        if value:
            self.__interctive = self.interactive
    # Set verbose mode
    def setVerbose(self, value):
        if value:
            basicConfig(level=INFO, format='%(message)s')
    # Set if the target is a directory
    def setIsDirectory(self, value):
        if value:
            self.__is_file_folder = True
    # Set the function to remove the file
    def setRecursive(self, value):
        if value:
            self.__remove_function = self.recursive
        else:
            self.__remove_function = self.normal_remove
    # Preserve the base "/" or "C:/"
    def setPreservation(self, value):
        if not value:
            try:
                if platform == 'win32':
                    self.__base = 'C:/'
                else:
                    self.__base = '/'
                    self.__base_list = listdir(self.__base)
                if value:
                    self.__preserve = False
            except:
                self.__preserve = True
        else:
            self.__preserve = True

    # Check if the given file is the root or not to preserve it
    def checkIfPreserve(self, file):
        if file == self.__base:
            return True and self.__preserve
        else:
            if listdir(file) == self.__base_list:
                return True and self.__preserve
            else:
                return False and self.__preserve
    ## Interactive functions
    def interactive(self, file):
        option = input(f'Remove {file} (Y/n)')
        if not len(option) or option[0] in 'yY':
            return True
        else:
            return False
    # Interactive but with a inteerval between files
    def interval(self, file):
        if self.__interval_memory == self.__interval_limit:
            self.__interval_memory = 0
            return self.interactive(file)
        self.__interval_memory += 1
        return True
    ## Removing functions
    # Normal removal of aa file
    def normal_remove(self):
        if not self.checkIfPreserve(self.__file.replace('\\', '/')):
            if self.__interctive(self.__file.replace('\\', '/')):
                if self.__is_file_folder:
                    try:
                        file = self.__file.replace('\\', '/')
                        rmdir(file)
                        info(f"Removed {file}")
                    except Exception as e:
                        info(str(e))
                else:
                    try:
                        file = self.__file.replace('\\', '/')
                        rmdir(file)
                        info(f"Removed {file}")
                    except Exception as e:
                        info(str(e))
    def start(self):
        self.__remove_function()

    # Recursive removal of a directory
    def recursive(self):
        if isdir(self.__file):
            # Map of the directiry we want to remove
            directory_map = list(walk(self.__file))
            # Reverse the directory for file erase at last `self.__file`
            directory_map.reverse()

            for path, directory_group, file_group in directory_map:
                # Erase all the directories in the path
                for directory in directory_group:
                    # Check if user wants to delete the directory
                    if self.__interctive(join(path, directory).replace('\\', '/')):
                        try:
                            directory = join(path, directory).replace('\\', '/')
                            rmdir(directory)
                            info(f"Removed {directory}")
                        except Exception as e:
                            info(str(e))
                # Erase all the file in the path
                for file in file_group:
                    # Check if user wants to delete the file
                    if self.__interctive(join(path, file).replace('\\', '/')):
                        try:

                            file =  join(path, file).replace('\\', '/')
                            remove(file)
                            info(f"Removed {file}")
                        except Exception as e:
                            info(str(e))
            # Erase base folder (self.__file)
            # We alredy know that self.__file is a folder
            self.__is_file_folder = True
            self.normal_remove()
        else:
            try:
                file = self.__file
                info(f"Removed {file}")
            except Exception as e:
                info(str(e))
# Main function to execute rm
def main(args=None):
    if not args:
        parser = ArgumentParser()
        parser.add_argument('setFile')
        parser.add_argument('-d', '--dir', help='Specify that the target is a empty directory', dest='setIsDirectory', action='store_const', const=True, default=False)
        parser.add_argument('-i', help='Always as for permission to delete a file', dest='setInteractive', action='store_const', const=True, default=False)
        parser.add_argument('-I', help='-I INTERVAL Ask for permission every n files deleted', dest='setInterval', type=int)
        parser.add_argument('-r', '-R', help='Recursive delete of a folder', dest='setRecursive', action='store_const', const=True, default=False)
        parser.add_argument('-v', '--verbose', help='Set mode to verbose show every action', dest='setVerbose', action='store_const', const=True, default=False)
        parser.add_argument('--no-preserve-root', help='Do not preserver the base; by default this is inactive', dest='setPreservation', action='store_const', const=False, default=True)
        args = vars(parser.parse_args())
    # Handler
    rm = RM()
    # Modular setup
    for key in args.keys():
        getattr(rm, key)(args[key])
    rm.start()
if __name__ == '__main__':
    main()