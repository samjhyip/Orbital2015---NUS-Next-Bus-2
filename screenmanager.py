from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
import datamall
#kivy.require("1.8.0")


#Main Screen
class MainScreen(Screen):
	def do_someaction(self):
		return 'Button Press is detected!'

#Bus Timing Screen
class BusTimingScreen(Screen):
	def getTime(self):
		datamall.GetBusInfo().getSubsequentTiming()

class ScreenManagement(ScreenManager):
	pass



class ScreenManager(App):
	def build(self):
		presentation = Builder.load_file("screenmanager12.kv")
		return presentation

if __name__=="__main__":
	ScreenManager().run()
