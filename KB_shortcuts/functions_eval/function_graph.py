from keyboard import set_view, get_selected_text, get_input_context
from ui import View, Image, ImageView, get_screen_size, Label

from function import Function


class Plot_View(View):
	def __init__(self, image):
		super().__init__(self)

		x, y = get_screen_size()
		if x > y:
			img_view = Label()
			img_view.text = 'Only in vertical position'
			img_view.frame = (0, 0, x, 15)
		else:
			y /= 4.4
			img_view = ImageView()
			img_view.image = image
			img_view.frame = (0, 0, x, y)
		self.add_subview(img_view)
		self.frame = (0, 0, x, y)


def main():
	content = get_selected_text()
	if content == '':
		content = get_input_context()[0]
		if content == '':
			return
	img = Function(content).plot()
	v = Plot_View(img)
	set_view(v)


main()

