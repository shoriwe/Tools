import ui
from os import getcwd, listdir, mkdir, rename
from os.path import isdir, join
from threading import Thread
from random import choice
from time import sleep


leidos = 0
cambiados = 0
finish = False


def map_dirs(directory=getcwd()):
	_map = []
	for file in listdir(directory):
		_map.append(join(directory, file))
		if isdir(join(directory, file)):
			_map += map_dirs(join(directory, file))
	return _map


def not_equal(parameters: list):
	file, new_file, location, file_name, import_name, new_import_name, old, new = parameters
	changes = False

	data = open(file, 'r').read()

	if 'import {}'.format(import_name) in data:
		if 'import {} as ' not in data:
			data = data.replace(import_name, new_import_name)
			changes = True
		
	if changes:
		f = open(file,'w')
		f.write(data)
		f.close()
		return 1
	return 0


def equal(parameters: list):
	file, new_file, location, file_name, import_name, new_import_name, old, new = parameters
	rename(file, new_file)
	return 1


def determine_equality(file, old, new):
	splited_file = file.split('/')

	location = '/'.join(splited_file[:-1])
	new_file = join(location, new)
	file_name = splited_file[-1]
	import_name = old.split('.')[0]
	new_import_name = new.split('.')[0]
	parameters = [
		file, new_file, location, file_name, import_name, new_import_name, old, new
	]

	if file_name == old:
		value = equal(parameters)
	else:
		if not isdir(file):
			value = not_equal(parameters)
		else:
			value = 0
	return value


def Tread_for_determine_equality(file, old, new):
	global cambiados
	cambiados += determine_equality(file, old, new)


def refractor(_map, old, new):
	global leidos
	for file in _map:
		leidos += 1
		Thread(target=Tread_for_determine_equality, args=(file, old, new)).start()
		sleep(0.2)

def update_labels(len_map):
	global leidos, cambiados, finish
	while not finish:
		v['label1'].text = str(leidos)
		v['label2'].text = str(cambiados)
		if leidos == len_map:
			finish = True


def start(sender):
	sender.enabled = False
	directory = join(getcwd(), v['textfield3'].text)
	old, new = v['textfield1'].text, v['textfield2'].text
	_map = map_dirs(directory)
	Thread(target=update_labels, args=(_map, )).start()
	Thread(target=refractor, args=(_map, old, new)).start()


try:
	v = ui.load_view('refactor.pyui')
	v.present()
except KeyboardInterrupt:
	print('bye')
	finish = True

