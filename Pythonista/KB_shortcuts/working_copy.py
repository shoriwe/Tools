from keyboard import get_selected_text
from webbrowser import open


def main():
	text = get_selected_text()
	if text != '':
		url = 'working-copy://clone?remote={}'.format(text)
		open(url)

main()
