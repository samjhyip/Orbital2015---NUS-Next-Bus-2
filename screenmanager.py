from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Line, Color
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
import datamall
#kivy.require("1.8.0")


class Painter(Widget):
	def on_touch_down(self,touch):
		with self.canvas:
			Color(1,0,0,1)
			touch.ud["line"] = Line(points=(touch.x,touch.y))
	def on_touch_move(self,touch):
		touch.ud["line"].points += [touch.x,touch.y]

	#clear the paint instance
	def clear_canvas(self):
		self.canvas.clear()

#Main Screen
class MainScreen(Screen):
	def do_someaction(self):
		return 'Button Press is detected!'
class AnotherScreen(Screen):
	pass

class AnotherScreen1(Screen):
	pass

#Bus Timing Screen
class BusTimingScreen(Screen):
	def getTime(self):
		datamall.GetBusInfo().getSubsequentTiming()

class ScreenManagement(ScreenManager):
	pass



class ScreenManager(App):
	def build(self):
		presentation = Builder.load_file("screenmanager1.kv")
		return presentation




if __name__=="__main__":
	ScreenManager().run()
