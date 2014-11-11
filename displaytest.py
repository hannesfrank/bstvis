import functools
import types

class Display(object):
	def __init__(self, t, display_after_functions):
		super().__init__()
		self.t = t
		t.d = self
		if not display_after_functions:
			display_after_functions = []

		for f in display_after_functions:
			wrapped_f = self.display_after(f)
			setattr(t, f.__name__, wrapped_f)

	def display(self, name):
		print("display:", name)

	def display_after(self, f):
		@functools.wraps(f)
		# we have to dismiss instance if we pass in bound methods like s.f1
		# def wrapper(instance, *args, **kwargs):
		# cleaner: Class methods (plain function)
		def wrapper(*args, **kwargs):
			res = f(*args, **kwargs)
			self.display(f.__name__)
			return res
		wrapper = types.MethodType(wrapper, self.t)
		return wrapper

class Displayable(object):
	def __init__(self):
		self.d = None

	def display(self, info):
		if self.d:
			d.display(info)

class SampleToDisplay(Displayable):
	"""docstring for SampleToDisplay"""
	def __init__(self):
		super(SampleToDisplay, self).__init__()

	def f1(self):
		print("in f1")
		self.f2()
		self.f2()

	def f2(self):
		self.display("extra")	# extra display
		print("in f2")

	def f3(self):
		print("in f3")

if __name__ == '__main__':
	s = SampleToDisplay()
	print(s.f1) 				# bound method
	print(SampleToDisplay.f1) 	# class method 

	s.f2() 	# no display just yet
	# d = Display(s, [s.f1, s.f2])  # bound method as argument
	d = Display(s, [
		SampleToDisplay.f1, 
		SampleToDisplay.f2])	# better plain functions

	# test display
	print("Test display")
	s.f1()
		