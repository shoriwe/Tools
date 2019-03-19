from sys import argv
from ui import TableView, View, get_screen_size, ListDataSource, Button, Label
from os import listdir, getcwd
from os.path import isdir, join
from shutil import copytree, copy


def map_sys(
	folder='/private/var/mobile/Containers/Shared/AppGroup/AD7A0AE4-6E50-4984-8814-0064F413FC33/Pythonista3/'
):
	f_map = {}
	for file in listdir(folder):
		f = join(folder, file)
		if isdir(f):
			f_map[file] = map_sys(f)

	return f_map


def _copy_(src, dst):
	if isdir(src):
		dst = join(dst, src.split('/')[-1])
		copytree(src, dst)
	else:
		copy(src, dst)


def Create_button(title, bg_color, t_color, corner_r, action, frame):
	button = Button()
	button.title = title
	button.bg_color = bg_color
	button.tint_color = t_color
	button.corner_radius = corner_r
	button.action = action
	button.frame = frame
	return button


class MyApp(View):
	def __init__(self, src):
		super().__init__(self)
		x, y = get_screen_size()
		self.src = src
		self.background_color = '#ffffff'
		self.map = map_sys()
		self.tableview = TableView()
		self.tableview.frame = (0, 0, *get_screen_size())
		self.datasource = ListDataSource(self.map.keys())
		self.datasource.action = self.Get_location
		self.label = Label()
		self.label.text = 'Done'
		self.copy_to = Create_button(
			'Copy here', '#6aff77', '#000000', 2, self.button_action,
			(x - 110, 50, 100, 30)
		)

		self.back = Create_button(
			'Back', '#ff4e4e', '#000000', 2, self.button_action, (x - 90, 10, 60, 30)
		)

		self.tableview.data_source = self.tableview.delegate = self.datasource
		self.location = []
		self.tableview.add_subview(self.back)
		self.tableview.add_subview(self.copy_to)
		self.add_subview(self.tableview)
		self.actual = self.map

		self.update_interval = 0.01

	def button_action(self, sender):
		if sender.title == 'Back':
			self.location = self.location[:-1]
			print(self.location)
			self.update_tv()
			self.Get_location(self.datasource, 1)
		else:
			route = '/'.join(self.location)
			base = '/private/var/mobile/Containers/Shared/AppGroup/AD7A0AE4-6E50-4984-8814-0064F413FC33/Pythonista3/'
			r = join(base, route)
			for src in self.src:
				_copy_(src, r)
			self.remove_subview(self.tableview)
			self.add_subview(self.label)

	def update(self):
		x, y = get_screen_size()
		self.back.frame = (x - 90, 10, 60, 30)
		self.copy_to.frame = (x - 110, 50, 100, 30)
		self.tableview.frame = (0, 0, x, y - 100)

	def update_tv(self):
		self.actual = self.map
		for value in self.location:
			self.actual = self.actual[value]

	def Get_location(self, sender, selected=None):
		if selected == None:
			selected = self.tableview.selected_row[1]
			selected = sender.items[selected]
			self.location.append(selected)
		self.update_tv()
		sender.items = self.actual.keys()


myapp = MyApp(argv[1:])
myapp.present()
my_sys_map = map_sys()

