from sys import argv
from shutil import make_archive,copy2,copytree,move
from os import mkdir,rmdir,chdir,listdir,getcwd,remove
from os.path import isdir,join

def erase(file):
	if isdir(file):
		for f in listdir(file):
			erase(join(file,f))
		rmdir(file)
	else:
		remove(file)
def copy(file):
	if isdir(file):
		dst=join('Backup',file.split('/')[-1])
		copytree(file,dst)
	else:
		copy2(file,'Backup')

def to_folder():
	try:
		erase('Backup')
	except Exception as e:
		pass
	mkdir('Backup')
	for file in argv[1:]:
		copy(file)

def zip_file():
		zip_location=getcwd()
		to_folder()
		make_archive('Backup','zip','Backup')
		erase('Backup')

zip_file()
