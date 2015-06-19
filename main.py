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
import datadb
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
	current_labels=[]
	
	#Gets user input from the text fields busStopNoInput & busNoInput
	def getUserInput(self):
		self._busstopnoinput = self.ids['busStopNoInput'].text
		self._busnoinput = ''

	def searchUserInput(self):
		#Instantiates a connection to datamall API
		#Bus 911 @ a working bus stop: 46429,911/83139
		app._toast('Searching for {}'.format(self._busstopnoinput))
		#Gets list of all bus services in operation		
		busservices = datamall.BusInfo(self._busstopnoinput,self._busnoinput).getallServices()

		#Removes existing labels, (if any) using label ref
		if self.current_labels:
			for _label in self.current_labels:
				self.remove_widget(_label)

		#Get user preferences (saved buses)
		app.getUserSaveBusRecords()

		#creates new labels and appends ref
		for (eachbus,row) in zip(busservices,range(len(busservices))):
			#Creates an EachBus instance for eachbus & Adds the Label instance to root. One bus service to one EachBus() instance
			each_bus_instance = EachBus(self._busstopnoinput, eachbus['ServiceNo'], row)			
			alllabels = each_bus_instance.getLabels()

			#Append each label and checkbox to current screen
			for eachlabel in alllabels:
				self.current_labels.append(eachlabel)
				self.add_widget(eachlabel)
			
			#Checkbox::Binds the Boolean Property 'active' to self.on_checkbox_active()		
			alllabels[5].bind(active=partial(self.on_checkbox_active, each_bus_instance.getServiceNo(), each_bus_instance.getBusStopID(), alllabels[5]))

	def on_checkbox_active(self, _serviceno, _busstopid, _labelref, *args):
		#If logged in and has checked this bus		
		if app._facebookid and _labelref.active == True:
			#updates mySQL DB
			thread = Thread(target=self.createUserSaveBusRecords, args=(_serviceno, _busstopid, _labelref))
			thread.start()
			app.all_saved_busstopNo.append(_busstopid)
			app.all_saved_busno.append(_serviceno)
			app._toast('Saved!')
		#If logged in and has unchecked this bus
		elif app._facebookid and not _labelref.active == True:
			#updates mySQL DB
			app.all_saved_busstopNo.remove(_busstopid)
			app.all_saved_busno.remove(_serviceno)
			app._toast('Deleted!')
		elif not app._facebookid:
			_labelref.active = False
			app._toast('Please login into Facebook first')

	def createUserSaveBusRecords(self, _serviceno, _busstopid, _labelref):
		#if the SaveBusRecords does not exist, response code of GET request is != 200
		#Create a new UserSaveBusRecords
		response = datadb.PostDBInfo().createUserSaveBusRecords(_serviceno, _busstopid, app._facebookid)
		Logger.info('Saving the User\'s preference' + str(response))


	
#Contains the instance for Each bus
class EachBus():
	#Creates all the labels upon initialization
	def __init__(self, _busstopid, _serviceno, row):
		self._busstopid = _busstopid
		self._serviceno = _serviceno
		#creates the nextbustime instance
		self.nextbustimelabel = Label(font_size=22, text=self.getNextBusTime(), size_hint=(0.3,0.05), pos_hint={"x":0.2, "y":(0.75-row*0.1)})
		self.nextbusloadlabel = Label(font_size=22, text=self.getNextBusLoad(), size_hint=(0.3,0.05), pos_hint={"x":0.2, "y":(0.70-row*0.1)})
		#creates the subsequentbustime instance
		self.subsequentbustimelabel = Label(font_size=22, text=self.getSubsequentBusTime(), size_hint=(0.3,0.05), pos_hint={"x":0.5, "y":(0.75-row*0.1)})
		self.subsequentbusloadlabel = Label(font_size=22, text=self.getSubsequentBusLoad(), size_hint=(0.3,0.05), pos_hint={"x":0.5, "y":(0.70-row*0.1)})
		#Creates the service number instance
		self.servicenolabel = Label(font_size=22, text=self.getServiceNo(), size_hint=(0.2,0.05), pos_hint={"x":0, "y":(0.75-row*0.1)})
		#Creates the save bus checkbox
		saved_status = False
		#checks if the user has saved this bus 
		if app.all_saved_busstopNo and app.all_saved_busno:
			if (self._busstopid,self._serviceno) in zip(app.all_saved_busstopNo, app.all_saved_busno):
				saved_status=True
		self.savebuscheckbox = CheckBox(size_hint=(0.1,0.1), pos_hint={"x":0.85, "y":(0.725-row*0.1)}, active=saved_status)


	def getNextBusTime(self):
		try:
			#Creates a GET request instance
			self.busInstance = datamall.BusInfo(self._busstopid,self._serviceno)
			self.busInstance.scrapeBusInfo()
			dateTime = self.busInstance.getNextTiming()
			grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+',dateTime)
			#grabTime[0]==date #grabTime[1]==time(UTC)
			timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
			timeLeft = re.split(r'\D',str(timedelta))
			if dateTime:	
				#timeLeft[0] can return null at times
				if not (timeLeft[0]):
					timeLeft[0]=0	
				return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
		except TypeError:
			return busServiceEnded

	def getSubsequentBusTime(self):
		try:
			#Creates a GET request instance
			self.busInstance = datamall.BusInfo(self._busstopid,self._serviceno)
			self.busInstance.scrapeBusInfo()
			dateTime = self.busInstance.getSubsequentTiming()
			grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+',dateTime)
			#grabTime[0]==date #grabTime[1]==time(UTC)
			timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
			timeLeft = re.split(r'\D',str(timedelta))
			if dateTime:
				#timeLeft[0] can return null at times
				if not (timeLeft[0]):
					timeLeft[0]=0	
				return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
		except TypeError:	
			return busServiceEnded

	#Gets Bus Stop ID and Service number that is in request
	def getBusStopID(self):
		return self.busInstance.getbusStopID()
	def getServiceNo(self):
		return self.busInstance.getServiceNo()

	def getNextBusLoad(self):
		return self.busInstance.getNextLoad()
	def getSubsequentBusLoad(self):
		return self.busInstance.getSubsequentLoad()
	
	#Gets the Label object
	def getLabels(self):
		self.alllabels=[self.servicenolabel,
				self.nextbustimelabel,
				self.nextbusloadlabel,
				self.subsequentbustimelabel,
				self.subsequentbusloadlabel,
				self.savebuscheckbox]
		return self.alllabels



class PreferredStops(Screen):
	pass


class BusTimingScreen(Screen):

	def getNextBusTime(self):
		Clock.schedule_once(self.updateNextBusTime,_updateFrequency)
		try:
			dateTime = datamall.GetBusInfo().getNextTiming()
			grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+',dateTime)
			#grabTime[0]==date #grabTime[1]==time(UTC)
			timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
			timeLeft = re.split(r'\D',str(timedelta))
			if dateTime:
				return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
		except TypeError:
			return busServiceEnded

	def getSubsequentBusTime(self):
		Clock.schedule_once(self.updateSubsequentBusTime,_updateFrequency)
		try:
			dateTime = datamall.GetBusInfo().getSubsequentTiming()
			grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+',dateTime)
			#grabTime[0]==date #grabTime[1]==time(UTC)
			timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
			timeLeft = re.split(r'\D',str(timedelta))
			if dateTime:
				return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
		except TypeError:	
			return busServiceEnded


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
		
	#Allows for this app to be paused when Facebook app is opened
	def on_pause(self):
		Logger.info('Android: App paused, now wait for resume.')
		return True
	
	#Allows for this app to be resumed after Facebook authorisation is completed
	def on_resume(self):
		pass

	def fb_me(self):
		def callback(success, user=None, response=None, *args):
			if not success:
			    return
			'''since we're using the JNIus proxy's API here,
			we have to test if we're on Android to avoid implementing
			a mock user class with the verbose Java user interface'''
			if platform() == 'android' and response.getError():
				Logger.info(response.getError().getErrorMessage())
			    #If this platform is android & response type not error
			if platform() == 'android' and not response.getError():
				infos = []
				infos.append('Name: {}'.format(user.getName()))
				infos.append('FirstName: {}'.format(user.getFirstName()))
				infos.append('MiddleName: {}'.format(user.getMiddleName()))
				infos.append('LastName: {}'.format(user.getLastName()))
				infos.append('Link: {}'.format(user.getLink()))
				infos.append('Username: {}'.format(user.getUsername()))
				infos.append('Birthday: {}'.format(user.getBirthday()))
				location = user.getLocation()
				if location:
					infos.append('Country: {}'.format(location.getCountry()))
					infos.append('City: {}'.format(location.getCity()))
					infos.append('State: {}'.format(location.getState()))
					infos.append('Zip: {}'.format(location.getZip()))
					infos.append('Latitude: {}'.format(location.getLatitude()))
					infos.append('Longitude: {}'.format(location.getLongitude()))
				else:
					infos.append('No location available')
				#Get User Details for DB Storage
				#Do something to get the ID part of the Facebook Link. Returns the numerical part of the Link
				self._facebookid = re.findall(r'[0-9]+',user.getLink())[0]
				self._username = user.getUsername()
				self._firstname = user.getFirstName()
				self._lastname = user.getLastName()
				self.startnewSaveThread()
			#if this platform is not android
			else:
				infos = ['ha', 'ha', 'wish', 'this', 'was', 'real']
			self.user_infos = '\n'.join(infos)
		self.facebook.me(callback)

	#separate thread to save basic user information
	def startnewSaveThread(self):
		thread = Thread(target=self.savefacebookinfo,args=())
		thread.start()

	#callback for saving user information
	def savefacebookinfo(self):
		#Use Identifier of the record to retrieve response code from 'users' table
		response = datadb.GetDBInfo().requestRecordByIdentifier("users",self._facebookid)
		Logger.info('Finding user from DreamFactory RESTful API. Response Code: {}'.format(response))
		#If record does not exist, create new FacebookID
		if response.status_code != 200:
			response = datadb.PostDBInfo().createUserTableRecords(self._facebookid,self._firstname+self._lastname,self._firstname,self._lastname)
			Logger.info('Creating user from DreamFactory RESTful API. Response: {}'.format(response))
	
	def getFacebookID(self):
		return self._facebookid

	#non-nus buses = requires bus stop and bus information
	def savePreferredBus(self):
		pass

	def savePreferredNUSBusstop(self):
		pass

	def _toast(self, text, length_long=False):
		toast.toast(text, length_long)

	#GET Request. Returns list of saved busNo and list of saved busstopNo using app._facebookid
	def getUserSaveBusRecords(self):
		#Retrieves for the first time
		if app._facebookid and not (self.all_saved_busstopNo and self.all_saved_busno):
			#gets a list of all the saved buses using facebookid		
			response = datadb.GetDBInfo().requestSavedBusRecord(app._facebookid)
			for each_bus_saved in response['record']:
				self.all_saved_busstopNo.append(each_bus_saved['busstopNo'])
				self.all_saved_busno.append(each_bus_saved['busno'])

if __name__=="__main__":
	ScreenManager().run()
