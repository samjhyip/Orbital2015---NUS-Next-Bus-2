#kivy.require("1.8.0")

#Kivy Library
from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

#Python Native Libraries
import datetime
import re

#Imported Source Files
import datamall

#Default <Bus Service ended> text
busServiceEnded = 'Not Available'
#Bus Timing Update Frequency (seconds)
_updateFrequency = 10



class DateTimeInfo():
	def getTimeNow(self):
		#Returns local time
		return datetime.datetime.now().strftime("%H:%M:%S")
	def getDateNow(self):
		#Returns local time
		return datetime.datetime.now().strftime("%Y-%m-%d") 
	def getUTCTime(self):
		#Returns UTC Time. To calculate difference between arrival and current timings
		return datetime.datetime.utcnow().strftime("%H:%M:%S")


class MainScreen(Screen):
	def do_someaction(self):
		return 'Button Press is detected!'

class SearchBus(Screen):
	pass

class PreferredStops(Screen):
	pass

class AccountSettings(Screen):
	pass

class BusTimingScreen(Screen):

	def getNextBusTime(self):
		Clock.schedule_once(self.updateNextBusTime,_updateFrequency)
		dateTime = datamall.GetBusInfo().getNextTiming()
		grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+',dateTime)
		#grabTime[0]==date #grabTime[1]==time(UTC)
		timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
		timeLeft = re.split(r'\D',str(timedelta))
		if dateTime:
			#To fix Hours=null
			if not timeLeft[0]:
				timeLeft[0]=0
			return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
		else: return busServiceEnded

	def getSubsequentBusTime(self):
		Clock.schedule_once(self.updateSubsequentBusTime,_updateFrequency)
		dateTime = datamall.GetBusInfo().getSubsequentTiming()
		grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+',dateTime)
		#grabTime[0]==date #grabTime[1]==time(UTC)
		timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
		timeLeft = re.split(r'\D',str(timedelta))
		if dateTime:
			#To fix Hours=null
			if not timeLeft[0]:
				timeLeft[0]=0
			return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
		else: return busServiceEnded


	def updateNextBusTime(self, *largs):
		self.ids["nextBusTime"].text = self.getNextBusTime()
	def updateSubsequentBusTime(self, *largs):
		self.ids["subsequentBusTime"].text = self.getSubsequentBusTime()


	def getDateTimeNowLabel(self):
		Clock.schedule_once(self.updateDateTimeLabel,1)
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	def updateDateTimeLabel(self, *largs):
		self.ids["dateTimeNowLabel"].text = self.getDateTimeNowLabel()


class ScreenManagement(ScreenManager):
	pass



class ScreenManager(App):
	def build(self):
		presentation = Builder.load_file("screenmanager12.kv")
		return presentation


if __name__=="__main__":
	ScreenManager().run()
