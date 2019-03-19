from re import search, findall
from numpy import arange
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from crunch import Crunch
from io import BytesIO
from ui import Image
from numpy import ma
from math import *


def create_ranges(ranges):
	add = {'[': 0, '(': 0.01, ']': 0.01, ')': 0}
	pattern = r'-?\d{1,}'
	ranges_ = {}
	for ran in ranges:
		x, y = (float(n) for n in findall(pattern, ran))
		x += add[ran[1]]
		y += add[ran[-1]]
		if ran[0] not in ranges_:
			ranges_[ran[0]] = [arange(x, y, 0.01)]
		else:
			ranges_[ran[0]].append(arange(x, y, 0.01))
	return ranges_


class Function:
	def __init__(self, function_str):
		self.func = function_str
		self.vars = findall(r'\w{1,}',
																						search(r'[\(](.*)[\)]',
																													function_str.split('=')[0]).group())

		self.plt3D = (len(self.vars) != 1)
		self.ranges = self.__get_ranges()
		self.raw_function = search(r'[\{](.*)[\}]', function_str).group().replace(
			'{', '').replace('}', '')
		for n, var in enumerate(self.vars):
			self.raw_function = self.raw_function.replace(var,
																																																	'{' + '{}'.format(n) + '}')

		if self.raw_function.split(',') != []:
			self.raw_function = self.raw_function.split(',')
		self.ys = self.generate_y()

	def generate_y(self):
		if self.plt3D:
			all_x = []
			all_z = []
			all_y = []

			vars = self.vars
			for n in range(len(self.ranges[vars[0]])):
				y = []
				xs, zs = self.ranges[vars[0]][n], self.ranges[vars[1]][n]
				for m in range(len(xs)):
					for l in range(len(zs)):

						x, z = xs[m], zs[l]
					try:
						evaluation = eval(self.raw_function[0].format(x, z))
						y.append(evaluation)
					except Exception as e:
						print(e, x, z)
				all_y.append(y)
				all_x.append(xs)
				all_z.append(zs)
			return all_x, all_z, all_y
		else:
			ys = []
			var_ = self.vars[0]
			for group in self.ranges[var_]:
				y = []
				for var in group:
					try:
						evaluation = eval(self.raw_function[0].format(var))
						y.append(evaluation)
					except Exception as e:
						pass
				ys.append(y)
			return ys

	def __get_ranges(self):
		pattern = r'\w?[\[\(]-?\d{1,},-?\d{1,}[\)\]]'
		ranges = findall(pattern, self.func)
		if ranges == []:
			ranges = ['{}[0,5]'.format(var) for var in self.vars]
		else:
			while len(self.vars) > len(ranges):
				data = ranges[-1]
				if data[0] in self.vars:
					ranges.append(ranges[-1][1:])
				else:
					ranges.append(ranges[-1])
			if len(ranges) > len(self.vars):
				for n, ran in enumerate(ranges):
					if ran[0] not in self.vars:
						ranges[n] = self.vars[-1] + ran
			if list(filter(lambda x: x[0] not in self.vars, ranges)) != []:
				available = [v for v in self.vars]
				for n, value in enumerate(ranges):
					if value[0] not in available:
						ranges[n] = available[0] + value
						available.remove(available[0])
					else:
						available.remove(value[0])
		return create_ranges(ranges)

	def plot(self):
		fig = BytesIO()
		if self.plt3D:
			figure = plt.figure()
			ax = figure.add_subplot(111, projection='3d')
			xs, ys, zs = self.ys
			for n in range(len(xs)):
				ax.plot_wireframe(xs[n], ys[n], zs[n])

			plt.savefig(fig)
			return Image.from_data(fig.getvalue())
		else:
			for n in range(len(self.ys)):
				plt.step(self.ranges[self.vars[0]][n], self.ys[n])
			plt.savefig(fig)
			return Image.from_data(fig.getvalue())

