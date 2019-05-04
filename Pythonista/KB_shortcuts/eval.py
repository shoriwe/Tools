from ui import View,Label,delay
from keyboard import get_input_context,set_view,get_selected_text
from io import StringIO
from sys import stdout
from math import *


class Out_View(View):
	def __init__(self):
		super().__init__(self)
		self.label=Label(frame=self.bounds.inset(0, 4, 0, 36), flex='WH')
		self.label.font=('Charter',12)
		self.label.text_color ='#ffffff'
		self.background_color = '#319b9b'
		self.add_subview(self.label)
		delay(self.update,0.3)
	def kb_text_changed(self):
		'''This gets called automatically by the keyboard (for the active view) whenever the text/selection changes'''
		self.update()
		
	def update(self):
		conetxt = get_input_context()
		select = get_selected_text()
		if select == '':
			out = conetxt[0]
		else:
			out = select
		try:
			self.label.text= '{}'.format(eval(out))
		except Exception as e:
			self.label.text='{}'.format(e)
def main():
	set_view(Out_View())
main()
