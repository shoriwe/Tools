from ui import View,Label,delay
from keyboard import get_input_context,set_view,get_selected_text
from math import *

# Python accessible eval from pythonista's PyKeys
class Out_View(View):
	def __init__(self):
		# Grap all the methods of View
		super().__init__(self)
		# Label for outputs
		self.label=Label(frame=self.bounds.inset(0, 4, 0, 36), flex='WH')
		# Only some configuration for better look
		self.label.font=('Charter',12)
		self.label.text_color ='#ffffff'
		self.background_color = '#319b9b'
		self.add_subview(self.label)
		# This updates the view
		delay(self.update,0.3)
	# This is called every time the stop typing
	def kb_text_changed(self):
		# This gets called automatically by the keyboard (for the active view) whenever the text/selection changes
		self.update()
	# Update the result of the lable with the evalution of the text selected or the last typed by the iser
	def update(self):
		# Grap the last typed text by the user
		context = get_input_context()
		# Grap the selected text by the user
		select = get_selected_text()
		# If the user select some text
		if select != '':
			inp = select
		else:
			# If go here user didn't select text so the script is going to grap the last stuff he typed
			inp = context[0]
		# pass the input to the eval function
		try:
			self.label.text= '{}'.format(eval(inp))
		except Exception as e:
			self.label.text='{}'.format(e)
def main():
	# Se view add's the created view to the panel of PyKeys  keyboard
	set_view(Out_View())
main()
