#kivy.require("1.8.0")

#Kivy Library
from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.logger import Logger
from kivy.uix.popup import Popup

#Python Native Libraries
import datetime
import re

#Imported Source Files
import datamall
import netcheck
from facebook import Facebook #jnius Interpreter

#Default <Bus Service ended> text
busServiceEnded = 'Not Available'
#Bus Timing Update Frequency (seconds)
_updateFrequency = 10
#Facebook APP ID
FACEBOOK_APP_ID = '904238149623014'

#Global Variables
facebook_status_global = ''

class BusInfo(FloatLayout):
	def __init__(self, **kwargs):
		super(BusInfo, self).__init__(**kwargs)

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


	def updateNextBusTime(self, *args):
		self.ids["nextBusTime"].text = self.getNextBusTime()
	def updateSubsequentBusTime(self, *args):
		self.ids["subsequentBusTime"].text = self.getSubsequentBusTime()


	def getDateTimeNowLabel(self):
		Clock.schedule_once(self.updateDateTimeLabel,1)
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	def updateDateTimeLabel(self, *args):
		self.ids["dateTimeNowLabel"].text = self.getDateTimeNowLabel()



class AskUser(RelativeLayout):
    ''' Callback(bool) if user wants to do something'''
    action_name = StringProperty()
    cancel_name = StringProperty()
    text = StringProperty()
    
    def __init__(self, 
                 action_name='Okay', 
                 cancel_name='Cancel', 
                 text='Are you Sure?',
                 callback=None, # Why would you do this?
                 *args, **kwargs):
        self.action_name = action_name
        self.cancel_name = cancel_name
        self._callback = callback
        self.text = text
        modal_ctl.modal = self
        super(AskUser, self).__init__(*args, **kwargs)

    def answer(self, yesno):
        ''' Callbacks in prompts that open prompts lead to errant clicks'''
        modal_ctl.modal.dismiss()
        if self._callback:
            def delay_me(*args):
                self._callback(yesno)
            Clock.schedule_once(delay_me, 0.1)

class FacebookUI(Screen):
    ''' Seems like there was a bug in the kv that wouldn't bind on 
    app.facebook.status, but only on post_status '''

    status_text = StringProperty()
    def __init__(self, **kwargs):
        super(FacebookUI, self).__init__(**kwargs)
        app.bind(facebook=self.hook_fb)
        
    
    def hook_fb(self, app, fb):
        fb.bind(status=self.on_status)
        app.bind(post_status=self.on_status)
        
        #If login is done correctly, self.status will take upon this message
    def on_status(self, instance, status):
        self.status_text = \
        'Facebook Status: [b]{}[/b]\nMessage: [b]{}[/b]'.format(
            app.facebook.status, 
            app.post_status)
        facebook_status_global = self.status_text


class ModalCtl:
    ''' just a container for keeping track of modals and implementing
    user prompts.'''

    def ask_connect(self, tried_connect_callback):
        Logger.info('Opening net connect prompt')
        text = ('You need internet access to do that.  Do you '
                'want to go to settings to try connecting?')
        content = AskUser(text=text,
                          action_name='Settings',
                          callback=tried_connect_callback,
                          auto_dismiss=False)

        #The Popup widget is used to create modal popups. By default, the popup will cover the whole parent window. When you are creating a popup, you must at least set a Popup.title and Popup.content.
        p = Popup(title = 'Network Unavailable',
                  content = content,
                  size_hint=(0.8, 0.4),
                  pos_hint={'x':0.1, 'y': 0.35})
        modal_ctl.modal = p
        #open popup p
        p.open()

    def ask_retry_facebook(self, retry_purchase_callback):
        Logger.info('Facebook Failed')
        text = ('Zuckerberg is on vacation in Monaco.  Would'
                ' you like to retry?')
        content = AskUser(text=text,
                          action_name='Retry',
                          callback=retry_purchase_callback,
                          auto_dismiss=False)

         #The Popup widget is used to create modal popups. By default, the popup will cover the whole parent window. When you are creating a popup, you must at least set a Popup.title and Popup.content.
        p = Popup(title = 'Facebook Error',
                  content = content,
                  size_hint=(0.8, 0.4),
                  pos_hint={'x':0.1, 'y': 0.35})
        modal_ctl.modal = p
        p.open() 


class ScreenManagement(ScreenManager):
	pass


class ScreenManager(App):

	post_status = StringProperty('-')
	user_infos = StringProperty('-')
	facebook = ObjectProperty()

	def build(self):
		global app
		app = self
		#Creating presentation retains an instance that we can reference to
		presentation = Builder.load_file("screenmanager12.kv")
		return presentation
	
	def on_start(self):

		self.facebook = Facebook(FACEBOOK_APP_ID,permissions=['publish_actions', 'basic_info'])
		#Sets up the AskUser() and PopUp() to ask for connection
		global modal_ctl
		modal_ctl = ModalCtl()
		#Define callback as modal_ctl.ask_connect()
		netcheck.set_prompt(modal_ctl.ask_connect)
		self.facebook.set_retry_prompt(modal_ctl.ask_retry_facebook)


if __name__=="__main__":
	ScreenManager().run()