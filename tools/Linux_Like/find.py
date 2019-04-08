from os.path import join, getctime, isdir
from os import walk, access, W_OK, R_OK, X_OK, stat, getcwd
from sys import platform
from datetime import datetime
from threading import Thread
from argparse import ArgumentParser


def comparare_dates(date1, date2):
    if not sum(date1) or not sum(date2):
        return False
    else:
        for number in range(3):
            if date1[number] != date2[number]:
                if date1[number] != 0 and date2[number] != 0:
                    return False
        return True


def get_file_type(file_path):
    if isdir(file_path):
        return 1
    return 2


def pattern_in_file(file_path, pattern):
    in_file = False
    try:
        file = open(file_path, 'rb')
        if pattern.encode('utf-8') in file.read():
            in_file = True
        file.close()
    except:
        pass
    return in_file


def get_file_creation_date(file_path):
    try:
        if platform == 'win32':
            return tuple(map(int, datetime.fromtimestamp(getctime(file_path)).strftime('%Y,%m,%d').split(',')))
        else:
            s = stat(file_path)
            try:
                return tuple(map(int, datetime.fromtimestamp(s.st_ctime).strftime('%Y,%m,%d').split(',')))
            except:
                return tuple(map(int, datetime.fromtimestamp(s.st_mtime).strftime('%Y,%m,%d').split(',')))
    except:
        return 0, 0, 0


class Find:
    def __init__(self, starting_point, target, name_can_contein, in_content, date, permissions, file_type, any_):
        self.__starting_point = starting_point
        self.__target = target
        self.__can_contein = name_can_contein
        self.__in_content = in_content
        self.__date = date
        self.__permissions = permissions
        self.__type = file_type
        self.__any = any_

    def __get_condition_function(self):
        permissions = {'r': R_OK, 'w': W_OK, 'x': X_OK}
        file_types = {'d': 1, 'f': 2}
        functions = []
        if self.__target:
            functions.append(lambda root, file: file == self.__target or join(root, file) == self.__target)
        if self.__can_contein:
            functions.append(lambda root, file: self.__can_contein in file)
        if self.__in_content:
            functions.append(lambda root, file: pattern_in_file(join(root, file), self.__in_content))
        if self.__date:
            functions.append(lambda root, file: comparare_dates(get_file_creation_date(join(root, file)), self.__date))
        if self.__permissions:
            for permission in self.__permissions:
                func = lambda root, file: access(join(root, file), permissions[permission])
                if func not in functions:
                    functions.append(func)
        if self.__type:
            functions.append(lambda root, file: get_file_type(join(root, file)) == file_types[self.__type])
        if self.__any:
            return lambda root, file: any([f(root, file) for f in functions])
        return lambda root, file: all([f(root, file) for f in functions] + [True])

    def __search_handler(self, root, directories, files, condition_function):
        for file in directories + files:
            if condition_function(root, file):
                print(join(root, file) + '\n', end='')

    def search(self):
        condition_function = self.__get_condition_function()
        for root, directories, files in walk(self.__starting_point):
            Thread(target=self.__search_handler, args=(root, directories, files, condition_function)).start()


def main(args=None):
    if not args:
        parser = ArgumentParser()
        parser.add_argument('-starting-point',
                            help='Folder to start the search any file inside it will going to be processed',
                            dest='starting_point', default=getcwd())
        parser.add_argument('-target', help='Match if the file name is equal to this', dest='target', default=None)
        parser.add_argument('-name-can-contein', help='The name can contein *something', dest='name_can_contein',
                            default=None)
        parser.add_argument('-in-content', help='The file can contein in its CONTENT', dest='in_content', default=None)
        parser.add_argument('-year', help='If file was created in a specific year', type=int, dest='year', default=0)
        parser.add_argument('-month', help='If file was created in a specific month', type=int, dest='month', default=0)
        parser.add_argument('-day', help='If file was created in a specific day', type=int, dest='day', default=0)
        parser.add_argument('-permissions',
                            help='r w and/or x if the actual user using find have any of this privileges',
                            dest='permissions', default=None)
        parser.add_argument('-type',
                            help='Type of  the file to find; d for directories; f for files; any other char count as f',
                            dest='type', default=None)
        parser.add_argument('-any', help='If any statement is True yield the file', dest='any', default=None)
        args = vars(parser.parse_args())
    date = (args['year'], args['month'], args['day'])
    if date == (0, 0, 0):
        date = None
    f = Find(args['starting_point'], args['target'], args['name_can_contein'], args['in_content'], date,
             args['permissions'], args['type'], args['any'])
    f.search()


if __name__ == '__main__':
    main()
