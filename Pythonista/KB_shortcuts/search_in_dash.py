from keyboard import get_selected_text
from webbrowser import open
from sys import argv
def main():
	seletected=get_selected_text()
	if seletected == '':
		return 
	url='dash://{}'.format(seletected)
	open(url)
main()
