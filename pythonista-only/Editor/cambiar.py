from re import search
from editor import get_path


def count_spaces(line):
	patter = r' {1,6}'
	return search(patter, line).span()[1]


def replace():
	steps={1:'Extracting content',2:'Starting edition',3:'Getting cuantity'}
	actual=1
	try:
		file = get_path()
		print(steps[1])
		content = open(file).read()

		line = [x for x in content.split('\n') if ' ' in x[:1]][0]
		actual=2
		print(steps[2])
		actual=3
		print(steps[3])
		cuantity = count_spaces(line)
		with open(file, 'w') as file:
			file.write(content.replace(' ' * cuantity, '\t'))
			file.close()
		print('Done')
	except Exception as e:
		print('++{}++'.format(e))
		print('Error in step {}'.format(actual))
		print('({})'.format(steps[actual]))
replace()
