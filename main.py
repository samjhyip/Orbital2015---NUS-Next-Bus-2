#kivy.require("1.8.0")

#Kivy Library
from kivy.app import App 
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy import platform
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label

#Python Native
from functools import partial
from threading import Thread
import datetime
import re

#Imported Source Files
import datamall
import datadb
import netcheck
import toast
from facebook import Facebook #jnius Interpreter

#Default <Bus Service ended> text
BUS_SERVICE_ENDED = 'Not Available'
#Bus Timing Update Frequency (seconds)
UPDATE_FREQUENCY = 5
#Facebook APP ID
FACEBOOK_APP_ID = '904238149623014'


class BusInfo(FloatLayout):
	def __init__(self, **kwargs):
		super(BusInfo, self).__init__(**kwargs)

class DummyScrollEffect(ScrollEffect):
	#ScrollEffect: Does not allow scrolling beyond the ScrollView boundaries.
	#When scrolling would exceed the bounds of the ScrollView, it uses a ScrollEffect to handle the overscroll. These effects can perform actions like bouncing back, changing opacity, or simply preventing scrolling beyond the normal boundaries. Note that complex effects may perform many computations, which can be slow on weaker hardware.
	#You can also create your own scroll effect by subclassing one of these, then pass it as the effect_cls in the same way.
	pass

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


class SearchBus(Screen):
	current_labels=[]
	loading_widget_collector=[]
	listview_widget_collector=[]
	isScreenDisabled = BooleanProperty(False)

	scrolleffect = DummyScrollEffect

	def on_isScreenDisabled(self, *args):
		if self.isScreenDisabled:
			self.ids['searchbusscreen_floatlayout'].disabled = True
		else:
			self.ids['searchbusscreen_floatlayout'].disabled = False

	def expand_menu(self):
		#Removes active header
		header_label = self.ids['searchbus1']
		header_placeholder = self.ids['header_placeholder']
		header_searchbutton = self.ids['search_button_grid']
		self.header_active = [header_label, header_placeholder, header_searchbutton]
		
		for each_header_widget in self.header_active:
			self.ids['header'].remove_widget(each_header_widget) 

		#Changes to active input menu
		self.header_back_button = Button(
			to_parent=True,
			size_hint=(0.1,1),
			background_normal='data/return.png',
			background_down='data/return_down.png'
			)
		self.header_back_button.bind(on_release=self.contract_menu)

		#Text Input Field Behaviour
		self.header_textinput = TextInput(
			to_parent=True,
			size_hint=(0.9,1),
			pos_hint={"top":1,"left":1},
			height='120dp', 
			multiline=False, 
			cursor_blink=True,
			cursor_color=(1,1,1,1),
			foreground_color=(1,1,1,1),
			hint_text_color=(1,1,1,0.7),
			hint_text='Search a bus stop number',
			font_size='24sp',
			background_active='data/text_input_focus.png',
			background_normal='data/text_input.png'
			)
		#on_text behaviour
		self.header_textinput.bind(text=self.on_text)
		#on validate key behaviour
		self.header_textinput.bind(on_text_validate=self.start_search)

		self.header_inactive = [self.header_back_button, self.header_textinput]

		for each_header_widget in self.header_inactive:
			self.ids['header'].add_widget(each_header_widget)

		#Sets focus to the text input (updates in the next frame, or it will not work. This is a getaround)
		Clock.schedule_once(self.focus_on_textinput,0)

	def contract_menu(self, *args):
		#removes inactive header
		for each_header_widget in self.header_inactive:
			self.ids['header'].remove_widget(each_header_widget)

		#removes the listview if exists
		if self.listview_widget_collector:
			for each_listview_widget in self.listview_widget_collector:
				self.ids['searchbusscreen_floatlayout'].remove_widget(self.listview_widget_collector.pop()) 
				
		#restores active header
		for each_header_widget in self.header_active:
			self.ids['header'].add_widget(each_header_widget)

	def focus_on_textinput(self, *args):
		self.header_textinput.focus = True

	#Suggested Bus stops
	def on_text(self, *args):
		#get text field text
		text_input_value = self.header_textinput.text
		#once user has type 3 letters and more, start substring search
		if len(text_input_value)>2:

			#if previous listview exists, remove it
			self.closeListView()

			#start search, put the response data in a list adapter
			suggestions = app.datamall_bus_stop.busnamesubstringSearch(text_input_value)
			
			#ListitemButton Behaviour
			args_converter = lambda row_index, rec: {
			'text':rec['text'],
			'size_hint':(None,None),
			'height': '50dp',
			'width': self.header_textinput.width
			}

			suggestion_listadapter = ListAdapter(
				data=suggestions,
				args_converter=args_converter,
				selection_mode='multiple',
				selection_limit=1,
				allow_empty_selection=True,
				cls=ListItemButton
				)
			#binds each listview button to the autofill function
			suggestion_listadapter.bind(on_selection_change=self.selection_change)
			
			#Logger.info("heightheight"+str(dp(60)))
			#Logger.info("heightheight"+str(float(dp(50)*len(suggestions)/self.height)))

			self.suggestion_listview = ListView(
				adapter=suggestion_listadapter,
				size_hint_y=(float(dp(50)*len(suggestions)/self.height)) if (float(dp(50)*len(suggestions)/self.height))<0.4 else 0.4,
				width=self.header_textinput.width,
				pos_hint={"top":(self.height-self.header_textinput.height*1.3)/self.height},
				x=self.header_textinput.x
				)

			#The container is a GridLayout widget held within a ScrollView widget.
			#So we are giving the ScrollViewParent a custom scroll effect
			#ListView >> ScrollView >> GridLayout
			#effect_cls is an ObjectProperty and defaults to DampedScrollEffect.
			self.suggestion_listview.container.parent.effect_cls = self.scrolleffect

			#Timeout allowed to trigger the scroll_distance, in milliseconds. If the user has not moved scroll_distance within the timeout, the scrolling will be disabled, and the touch event will go to the children.
			self.suggestion_listview.container.parent.scroll_distance = 10
			self.suggestion_listview.container.parent.scroll_timeout = 	1000

			self.listview_widget_collector.append(self.suggestion_listview)
			self.ids['searchbusscreen_floatlayout'].add_widget(self.suggestion_listview)

		else:
			#User is deleting his input, so naturally, we shall close the listview (if it exists)
			self.closeListView()

	#user touches a suggestion
	def selection_change(self, *args):
		selected_item = args[0].selection[0]
		#Logger.info("busstopselection"+str(selected_item.text))
		
		#On First Selection or when the textinput is not the same as the option selected
		#Auto fills the text input widget
		if selected_item.text != self.header_textinput.text:
			self.header_textinput.text = selected_item.text

		#On Second Selection + color change
		#If text field is the same as the text in the selection, close the listview and start the search
		else:
			self.start_search()


	def getBusStopNamefromCode(self, _busstopcode):
		return app.datamall_bus_stop.getBusStopName(_busstopcode)

	def closeListView(self):
		#close the suggestion listview (if any)
		if self.listview_widget_collector:
			for each_listview in self.listview_widget_collector:
				self.ids['searchbusscreen_floatlayout'].remove_widget(self.listview_widget_collector.pop())

	#search text input accepts strings and numbers
	def start_search(self, *args):
		#if listview is active, close it
		self.closeListView()
		self.getUserInput()
		self.contract_menu()
		self.searchUserInput()

	#Gets user input from the text fields busStopNoInput & busNoInput
	def getUserInput(self, *args):
		self._busnoinput = ''

		#If search value is a number
		if self.header_textinput.text.isdigit():
			self._busstopnoinput = self.header_textinput.text
		#if the string is not a digit
		else:
			response_busstopcode = app.datamall_bus_stop.searchBusStopCode(self.header_textinput.text)
			#if response is not None
			if response_busstopcode:
				self._busstopnoinput = response_busstopcode
			#not a valid bus stop. Are we gonna let it carry on first?
			else:
				self._busstopnoinput = self.header_textinput.text


	def searchUserInput(self, *args):
		#Instantiates a connection to datamall API
		#Bus 911 @ a working bus stop: 46429,911/83139
		app._toast('Searching for Bus Stop {}'.format(self._busstopnoinput))

		#Gets list of all bus services in operation	
		allbuses_instance = datamall.BusInfo(self._busstopnoinput, self._busnoinput)
		
		#Valid Bus Stop Check?
		if allbuses_instance.response.status == 200:
	
			self.busservices = allbuses_instance.getallServices()

			#Removes existing labels, (if any)
			if self.current_labels:
				for _eachbuswidget in self.current_labels:
					self.ids['searchbusscreen_gridlayout'].remove_widget(_eachbuswidget)

			#Displays Loading widget
			loading_widget = LoadingWidget()
			self.ids['searchscreen_main_body'].add_widget(loading_widget)
			self.loading_widget_collector.append(loading_widget)

			#Disables main body
			self.isScreenDisabled = True

			#Get user preferences (saved buses)>>UI remains responsive now. Widgets can only be created after records are retrieved
			#Retrieval of records allow for Checkboxes to be created with user's preference shown
			self.retrievePreferredStops()

		#invalid bus stop id or when all bus services have ceased operation
		else:
			app._toast('Invalid Bus Stop!')


	def create_bus_instance_widgets(self, *args):
		#Stop displaying loading widget
		if self.loading_widget_collector:
			for loading_widget in self.loading_widget_collector:
				self.ids['searchscreen_main_body'].remove_widget(self.loading_widget_collector.pop())

		#creates new labels and appends ref
		for (eachbus) in self.busservices:
			#Creates an EachBus instance for eachbus & Adds the Label instance to root. One bus service to one EachBus() instance
			self.each_bus_instance = EachBus(self._busstopnoinput, eachbus['ServiceNo'])			
			self.eachbuswidget = self.each_bus_instance.getEachBusGridLayoutWidget()

			#append to the current_labels list
			self.current_labels.append(self.eachbuswidget)

			#append to the Parent Layout
			self.ids['searchbusscreen_gridlayout'].add_widget(self.eachbuswidget)
		
			#Checkbox::Binds the Boolean Property 'active' to self.on_checkbox_active()		
			self.each_bus_instance.getLabels()[3].bind(active=partial(self.on_checkbox_active, self.each_bus_instance.getServiceNo(), self.each_bus_instance.getBusStopID(), self.each_bus_instance.getLabels()[3]))

		#Each bus's canvas instructions for loading texture
		for _eachbuswidget in self.current_labels:
			with _eachbuswidget.canvas.before:
				#Tints and opacity can be achieved!
				_eachbuswidget.canvas.opacity = 0.9
				thiscanvasrect = Rectangle(pos=_eachbuswidget.pos, size=_eachbuswidget.size, source='data/bg/each_label.png')

				#http://kivy.org/planet/2014/10/updating-canvas-instructions-declared-in%C2%A0python/
				#on pos or size change of the GridLayout, update the position of the canvas as well!
				_eachbuswidget.bind(pos=partial(self.update_label_canvas, _eachbuswidget, thiscanvasrect), size=partial(self.update_label_canvas, _eachbuswidget, thiscanvasrect))

		#enables main body again
		self.isScreenDisabled = False

		'''
		#show current bus stop name in search
		busstopnamelabel = Label(
			text=self.this_busstopname,
			size_hint=(1,None),
			height='60dp',
			font_size='16sp'
			)

		self.current_labels.append(busstopnamelabel)
		self.ids['searchbusscreen_gridlayout'].add_widget(busstopnamelabel)
		'''

	def update_label_canvas(self, thisbuswidget, thiscanvasrect, *args):
		thiscanvasrect.pos = thisbuswidget.pos
		thiscanvasrect.size = thisbuswidget.size

	def retrievePreferredStops(self, *args):
		#If records not retrieved
		if not app.isRecordRetrieved:
			#Get user preferences (saved buses). Will exit thread if user is not logged in
			thread1 = Thread(target=app.getUserSaveBusRecords,args=()).start()
		#thread2 starts even before thread 1 is done (if thread1 is executed)
		thread2 = Thread(target=self.check_UserSaveBusRecords_if_exists,args=()).start()


	def check_UserSaveBusRecords_if_exists(self,*args):
		#Still retrieving records (only if logged in)
		if app._facebookid:
			while not app.isRecordRetrieved:
				time.sleep(1)
		#Retrieval done
		Clock.schedule_once(self.create_bus_instance_widgets, 0)


	def on_checkbox_active(self, _serviceno, _busstopid, _labelref, *args):
		#If logged in and has checked this bus		
		if app._facebookid and _labelref.active == True:
			#show saving widget
			saving_widget = SavingWidget()
			self.ids['searchscreen_main_body'].add_widget(saving_widget)
			self.loading_widget_collector.append(saving_widget)
			self.isScreenDisabled = True

			#updates mySQL DB
			thread = Thread(target=self.createUserSaveBusRecords, args=(_serviceno, _busstopid, _labelref)).start()
			app.all_saved_busstopNo.append(_busstopid)
			app.all_saved_busno.append(_serviceno)
			#app._toast('Saving. Don\'t quit the app!')
		#If logged in and has unchecked this bus

		elif app._facebookid and not _labelref.active == True:
			#show deleting widget
			deleting_widget = DeletingWidget()
			self.ids['searchscreen_main_body'].add_widget(deleting_widget)
			self.loading_widget_collector.append(deleting_widget)
			self.isScreenDisabled = True

			#updates mySQL DB
			thread = Thread(target=self.deleteUserSaveBusRecords, args=(_serviceno, _busstopid, _labelref)).start()
			app.all_saved_busstopNo.remove(_busstopid)
			app.all_saved_busno.remove(_serviceno)
			#app._toast('Deleting. Don\'t quit the app!')

		elif not app._facebookid:
			if _labelref.active is True:
				_labelref.active = False
				app._toast('Please login into Facebook first')

	def createUserSaveBusRecords(self, _serviceno, _busstopid, _labelref, *args):
		#if the SaveBusRecords does not exist, response code of GET request is != 200
		#Create a new UserSaveBusRecords
		response = datadb.PostDBInfo().createUserSaveBusRecords(_serviceno, _busstopid, app._facebookid)
		#Logger.info('Saving the User\'s preference' + str(response))

	def deleteUserSaveBusRecords(self, _serviceno, _busstopid, _labelref, *args):
		#Deletes a UserSaveBusRecord
		response = datadb.DeleteDBInfo().deleteUserSavebusRecords(_serviceno, _busstopid, app._facebookid)
		#Logger.info('Deleting the User\'s preference' + str(response))

		#We have a response from the DELETE request
		delete_complete_status_code = response.status_code
		self.deleteCompleted(delete_complete_status_code)
	
	def saveCompleted(self, save_complete_status_code, *args):
		Clock.schedule_once(partial(self.showSaveCompletedToast, save_complete_status_code), 0)
	
	def showSaveCompletedToast(self, save_complete_status_code, *args):
		#Response for POST is 200
		if save_complete_status_code==200:
			#Remove Saving now widget
			if self.loading_widget_collector:
				for each_saving_widget in self.loading_widget_collector:
					self.ids['searchscreen_main_body'].remove_widget(self.loading_widget_collector.pop())
			app._toast('Saved!')
			self.isScreenDisabled = False
		else:
			app._toast('Can\'t save! Error Code: {}'.format(str(self.save_complete)))

	def deleteCompleted(self, delete_complete_status_code, *args):
		Clock.schedule_once(partial(self.showDeleteCompletedToast, delete_complete_status_code), 0)

	def showDeleteCompletedToast(self, delete_complete_status_code, *args):
		#Response for DELETE is 200
		if delete_complete_status_code==200:
			#Remove Deleting now widget
			if self.loading_widget_collector:
				#Updates widget Label
				for each_deleting_widget in self.loading_widget_collector:
					self.ids['searchscreen_main_body'].remove_widget(self.loading_widget_collector.pop())
			app._toast('Deleted!')
			self.isScreenDisabled = False
		else:
			app._toast('Can\'t delete! Error Code: {}'.format(str(self.delete_complete)))

	
#Contains the instance for Each bus
class EachBus():
	#Creates all the labels upon initialization
	def __init__(self, _busstopid, _serviceno, row):
		self._busstopid = _busstopid
		self._serviceno = _serviceno
		#creates the nextbustime instance
		self.nextbustimelabel = Label(
			font_size='16sp',
			text=self.getBusTime(0), 
			size_hint=(0.35,None), 
			height=60
			)
		self.nextbusloadlabel = Label(
			font_size='12sp', 
			text=self.getNextBusLoad(), 
			size_hint=(0.35,None), 
			height=90, 
			halign='center'
			)
		#to wrap text size according to the label size
		self.nextbusloadlabel.text_size = self.nextbusloadlabel.size

		#creates the subsequentbustime instance
		self.subsequentbustimelabel = Label(
			font_size='16sp', 
			text=self.getBusTime(1), 
			size_hint=(0.35,None), 
			height=60
			)
		self.subsequentbusloadlabel = Label(
			font_size='12sp', 
			text=self.getSubsequentBusLoad(), 
			size_hint=(0.35,None), 
			height=90, 
			halign='center'
			)
		#to wrap text size according to the label size
		self.subsequentbusloadlabel.text_size = self.subsequentbusloadlabel.size
		
		#Creates the service number instance
		self.servicenolabel = Label(
			font_size='35sp', 
			text=self.getServiceNo(), 
			size_hint=(0.15,None), 
			height=60,
			padding_y='18dp'
			)

		#Creates the save bus checkbox
		saved_status = False
		#checks if the user has saved this bus 
		if app.all_saved_busstopNo and app.all_saved_busno:
			if (self._busstopid,self._serviceno) in zip(app.all_saved_busstopNo, app.all_saved_busno):
				saved_status=True
		self.savebuscheckbox = CheckBox(size_hint=(0.1,0.1), pos_hint={"x":0.85, "y":(0.725-row*0.1)}, active=saved_status)

		self.savebuscheckbox = CheckBox(
			size_hint=(0.15,None), 
			active=saved_status, 
			height='30dp',
			background_checkbox_normal='data/checkbox_disabled_down.png',
			background_checkbox_down='data/checkbox_down.png',
			background_checkbox_disabled_normal='data/checkbox_disabled_normal.png',
			background_checkbox_disabled_down='data/checkbox_normal.png'
			)
		#dummy labels to fill up GridLayout's column 1 and 4
		self.dummylabel1 = Label(
			size_hint=(0.15,None), 
			height=90
			)
		self.dummylabel2 = Label(
			size_hint=(0.15,None), 
			height=90
			)

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
			#Gets Data
			self.busInstance.scrapeBusInfo()
			dateTime = getattr(self.busInstance, which_bus_timing[which_bus])()
			#Finds the time	
			grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+', dateTime)
			#grabTime[0]==date #grabTime[1]==time(UTC)
			timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
			timeLeft = re.split(r'\D',str(timedelta))
			if dateTime:	 
				#timeLeft[0] can return null at times
				if not (timeLeft[0]):
					timeLeft[0]=0
				#return minutes and seconds
				#return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
				#return minutes only
				return '%s mins' %(str(int(timeLeft[0])*60+int(timeLeft[1])))
		except TypeError as e:
			return BUS_SERVICE_ENDED

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
				self.subsequentbustimelabel,
				self.savebuscheckbox,
				self.dummylabel1,
				self.nextbusloadlabel,	
				self.subsequentbusloadlabel,
				self.dummylabel2]
		return self.alllabels

	def getEachBusGridLayoutWidget(self):
		return self.gridlayout


class PreferredStops(Screen):

	#For widget 'garbage collection'
	widget_garbage_collector = []
	loading_widget_collector = []

	#Show 'PULL DOWN TO REFRESH?' Boolean
	showInstruction = BooleanProperty(False)
	is_reloading = False
	is_firstload = True

	isScreenDisabled = BooleanProperty(False)

	def on_pre_enter(self, *args):
		#Update Footer Buttons on enter
		self.ids['footer'].ids['footer_saved_button'].ids['footer_saved_button_image'].source = 'data/Save_inactive.png'
		#auto load on open
		if self.is_firstload:
			self.startFirstSearch()
			self.is_firstload = False

	def on_isScreenDisabled(self, *args):
		if self.isScreenDisabled:
			self.ids['preferredstops_mainbody'].disabled = True
		else:
			self.ids['preferredstops_mainbody'].disabled = False


	#Defines the behaviour of the Search Button 
	def startFirstSearch(self, *args):
		loadingwidget = LoadingWidget()
		#On first run, display the loading widget while we retrieve data
		self.ids['preferredstops_mainbody'].add_widget(loadingwidget)
		self.loading_widget_collector.append(loadingwidget)
		#Disable 
		self.isScreenDisabled=True
		#Starts the widget creation process
		self.createPreferredStops()

	#Because the GET requests are significantly slow, we use threads to prevent the UI from being unresponsive
	#We use these threads to schedule the widgets to be displayed once all the GET retrievals are completed
	#Event Dispatcher will subsequently run the callback functions to display the widgets
	def createPreferredStops(self, *args):
		#If records have not been retrieved or if user has no saved buses
		if not app.all_saved_busstopNo and not app.all_saved_busno:
			#Get user preferences (saved buses)
			self.isthread1_done = False
			thread1 = Thread(target=self.getUserSaveBusRecords,args=()).start()
		#If records have already been retrieved and saved locally
		if app.all_saved_busstopNo and app.all_saved_busno:
			self.isthread1_done = True
		#Checks if thread 1 is done. If done, create the preference instances
		thread2 = Thread(target=self.checkUserSaveBusRecords_if_exist,args=()).start()

	#Displays all the saved widgets				
	def showPreferredStops(self, *args):
		#If existing records exist
		if app.all_saved_busstopNo and app.all_saved_busno:
			for each_saved_busstopNo,each_saved_busno in zip(app.all_saved_busstopNo, app.all_saved_busno):
				eachSavedPreference_instance = EachSavedPreference(each_saved_busstopNo, each_saved_busno)
				#Add the GridLayout to the ScrollView				
				self.ids['preferredstops_body'].add_widget(eachSavedPreference_instance.getGridLayout())
				#Saves the reference of each GridLayout so that we can remove later
				self.widget_garbage_collector.append(eachSavedPreference_instance.getGridLayout())

			#Another loop to create the canvas for each entry
			for _each_saved_widget in self.widget_garbage_collector:
				with _each_saved_widget.canvas.before:
					_each_saved_widget.canvas.opacity = 0.9
					thiscanvasrect = Rectangle(
						pos=_each_saved_widget.pos, 
						size=_each_saved_widget.size, 
						source='data/bg/each_label.png'
						) 
					_each_saved_widget.bind(
						pos=partial(self.update_canvas, _each_saved_widget, thiscanvasrect),
						size=partial(self.update_canvas, _each_saved_widget, thiscanvasrect)
						)

		#if no records exists, do something

	def update_canvas(self, thiswidget, thiscanvasrect, *args):
		thiscanvasrect.pos = thiswidget.pos
		thiscanvasrect.size = thiswidget.size

	#'Garbage' Collection of all displayed widgets, if any
	def removePreferredStops(self, *args):
		#If loading widget is active, remove it.
		if self.loading_widget_collector:
			for each_loading_widget in self.loading_widget_collector:
				self.ids['preferredstops_mainbody'].remove_widget(self.loading_widget_collector.pop())

		#Removes previous instances (IF ANY)
		if self.widget_garbage_collector:
			for each_Grid in self.widget_garbage_collector:
				self.ids['preferredstops_body'].remove_widget(self.widget_garbage_collector.pop())

	#GET Request from RESTful API: DreamFactory
	def getUserSaveBusRecords(self):
		userSaveBusRecords = app.getUserSaveBusRecords()
		self.isthread1_done = True
		#return userSaveBusRecords

	def checkUserSaveBusRecords_if_exist(self, *args):
		#still waiting for thread 1
		while not self.isthread1_done:
			time.sleep(1)
		#Removes scroll lock if reloading
		if self.is_reloading:
			self.ids['preferred_scroll_view'].do_scroll_y = True
		#Enable the screen again
		self.isScreenDisabled = False
		#check is done, remove old widgets
		Clock.schedule_once(self.removePreferredStops,0)
		#displays new widgets
		Clock.schedule_once(self.showPreferredStops, 0)

	#Pull to refresh Behaviour
	def pullToRefresh(self, scr_val):

		#Large overscroll. The gap between slight scroll and this must be significant. Else, the user could have missed slight scroll activity
		if scr_val>1.05:
			self.is_reloading = True

		#Slight overscroll activity
		elif (scr_val>1.02):
			#shows 'pull down to refresh' instructions
			if not self.showInstruction and not self.is_reloading:
				self.showInstruction = True
			#User Release after refreshing
			if self.showInstruction and self.is_reloading:
				#Lock Scroll
				self.ids['preferred_scroll_view'].do_scroll_y = False
				self.start_refresh()
		
		#No overscroll activity
		else:
			self.is_reloading = False
			if self.showInstruction:
				self.showInstruction = False

	def start_refresh(self):
		#Show Loading widget
		loadingwidget = LoadingWidget()
		self.ids['preferredstops_mainbody'].add_widget(loadingwidget)
		self.loading_widget_collector.append(loadingwidget)

		#Disable the mainbody
		self.isScreenDisabled = True

		#Call for widget update. Once the widgets are ready, the scroll lock is removed by self.createPreferredStops()
		self.createPreferredStops()
		#Label will be auto removed

	def on_showInstruction(self, *args):
		#if user is pulling down
		if self.showInstruction:
			hiddenwidgets = self.ids['preferredstops_body']
			self.ids['main_body'].remove_widget(self.ids['preferredstops_body'])
			#show instructions
			self.instructions_label = Label(text='[b]PULL DOWN TO REFRESH[/b]', markup=True)
			self.ids['main_body'].add_widget(self.instructions_label)
			self.ids['main_body'].add_widget(hiddenwidgets)

		#if user is not pulling down anymore
		elif not self.showInstruction:
			#hide instructions
			self.ids['main_body'].remove_widget(self.instructions_label)

class EachSavedPreference():

	def __init__(self, _busstopid, _serviceno, *args):
		#Local variables
		self._busstopid = _busstopid
		self._serviceno = _serviceno
		
		#All the required Labels
		self.bus_stop_name = Label(
			text='[b]{}[/b]'.format(str(self.getBusStopName(str(_busstopid)))), 
			size_hint=(1,None), 
			height='30dp',
			markup=True,
			font_size='15sp'
			)
		self.bus_stop_text = Label(
			text='BUS STOP', 
			size_hint=(1,None), 
			height='20dp'
			)
		self.bus_stop_label = Label(
			text=_busstopid, 
			size_hint=(1,None), 
			height='20sp'
			)
		self.service_no_label = Label(
			text='[b]{}[/b]'.format(_serviceno), 
			font_size='35sp', 
			size_hint=(1,None), 
			height='60dp', 
			markup=True
			)
		self.next_bus_text = Label(
			text='NEXT BUS', 
			size_hint=(1,None), 
			height='60dp'
			)
		self.subsequent_bus_text = Label(
			text='SUBSEQUENT BUS', 
			size_hint=(1,None), 
			height='60dp'
			)
		self.next_arrival_label = Label(
			text=self.getBusTime(0), 
			size_hint=(1,None), 
			height='25dp',
			font_size='20sp',
			valign='top'
			)
		self.subsequent_arrival_label = Label(
			text=self.getBusTime(1), 
			size_hint=(1,None), 
			height='25dp',
			font_size='20sp',
			valign='top'
			)
		self.next_load_label = Label(
			text=self.getNextBusLoad(), 
			size_hint=(1,None), 
			height='50dp'
			)
		self.subsequent_load_label = Label(
			text=self.getSubsequentBusLoad(), 
			size_hint=(1,None), 
			height='50dp'
			)

		#Grouping in Grid 0
		self.grid0_labels = [self.bus_stop_name]	
		
		#Grouping in Grid 1
		self.grid1_labels = [self.bus_stop_text, self.bus_stop_label]

		#Grouping in Grid 2
		self.grid2_labels = [self.service_no_label]
	

		#Grouping in Grid 3 follows the arrangement as shown below
		self.grid3_labels = [self.next_bus_text, self.subsequent_bus_text, 
				self.next_arrival_label, self.subsequent_arrival_label, 
				self.next_load_label, self.subsequent_load_label]

		#Creating the Layout (Made up of 3 GridLayouts)
		self.grid0 = GridLayout(cols=1, size_hint=(1,None),height=self.bus_stop_name.height)
		self.grid1 = GridLayout(cols=2, size_hint=(1,None),height=self.bus_stop_text.height)
		self.grid2 = GridLayout(cols=1, size_hint=(1,None), height=self.service_no_label.height)
		self.grid3 = GridLayout(cols=2, rows=3, size_hint=(1,None), height=(self.next_bus_text.height+self.next_arrival_label.height+self.next_load_label.height)*1.2)

		#Adding the Labels to each GridLayout
		for each_grid0_label in self.grid0_labels:
			self.grid0.add_widget(each_grid0_label)

		for each_grid1_label in self.grid1_labels:
			self.grid1.add_widget(each_grid1_label)

		for each_grid2_label in self.grid2_labels:
			self.grid2.add_widget(each_grid2_label)

		for each_grid3_label in self.grid3_labels:
			self.grid3.add_widget(each_grid3_label)

		self.mainGrid = GridLayout(
			cols=1, 
			size_hint=(1,None), 
			height=(self.grid0.height+self.grid1.height+self.grid2.height+self.grid3.height), 
			padding=('15dp','15dp','15dp','15dp')
			)
		self.mainGrid.add_widget(self.grid0)
		self.mainGrid.add_widget(self.grid1)
		self.mainGrid.add_widget(self.grid2)
		self.mainGrid.add_widget(self.grid3)

	def getBusTime(self, which_bus):
		#which_bus can be either getNextTiming or getSubsequentTiming
		which_bus_timing = ['getNextTiming', 'getSubsequentTiming']

		try:
			#Creates a GET request instance
			self.busInstance = datamall.BusInfo(self._busstopid, self._serviceno)
			#Gets Data
			self.busInstance.scrapeBusInfo()
			dateTime = getattr(self.busInstance, which_bus_timing[which_bus])()
			#Finds the time	
			grabTime = re.findall('[0-9]+\D[0-9]+\D[0-9]+', dateTime)
			#grabTime[0]==date #grabTime[1]==time(UTC)
			timedelta = datetime.datetime.strptime(grabTime[1],"%H:%M:%S") - datetime.datetime.strptime(DateTimeInfo().getUTCTime(),"%H:%M:%S")
			timeLeft = re.split(r'\D',str(timedelta))
			if dateTime:	 
				#timeLeft[0] can return null at times
				if not (timeLeft[0]):
					timeLeft[0]=0
				#return minutes and seconds
				#return '%s MINUTES %s SECONDS' %(str(int(timeLeft[0])*60+int(timeLeft[1])),timeLeft[2])
				#return minutes only
				return '%s mins' %(str(int(timeLeft[0])*60+int(timeLeft[1])))
		except TypeError as e:
			return BUS_SERVICE_ENDED
		except KeyError as e:
			return BUS_SERVICE_ENDED

	def getNextBusLoad(self):
		return self.busInstance.getNextLoad()
	def getSubsequentBusLoad(self):
		return self.busInstance.getSubsequentLoad()

	def getBusStopName(self, _busstop_id):
		return app.datamall_bus_stop.getBusStopName(str(_busstop_id))

	def getGridLayout(self):
		return self.mainGrid

class FacebookUI_Existing_User(Screen):

	def on_pre_enter(self, *args):
		#updates footer button on enter
		self.ids['footer'].ids['footer_accountsettings_button'].ids['footer_accountsettings_button_image'].source = 'data/User Accounts inactive.png'
		self.ids.labelAccountID.text = app._facebookid

	def launchPopup(self, title):
		popupContent = askConfirmation()
		popupContent.setText(title, popupContent)	
		popup = Popup(title=title, content=popupContent, size_hint=(0.8,0.3), auto_dismiss=False)
		
		self.btnYesBehaviour(title, popupContent, popup)
		#Binds cancel button to dismiss activity
		popupContent.ids.btnDismiss.bind(on_press=popup.dismiss)
		popup.open()

	def btnYesBehaviour(self, title, popupContent, popup):
		if (title=="Logout"):
			#Binds the yes button to the LOGOUT activity
			popupContent.ids.btnYes.bind(on_press=partial(self.logoutUser, popup))
		
		elif (title=="Reset"):
			#Bind the yes button to the RESET activity
			popupContent.ids.btnYes.bind(on_press=partial(self.resetUser, popup))

	def logoutUser(self, popup, *args):
		app._toast('You are now logged out')
		popup.dismiss()
		#Deletes the save file
		app.fb_userprofile.removeUSER()
		#Transfer to the main screen
		app.root_widget.current = 'accountsettings'

	def resetUser(self, popup, *args):
		app._toast('Deleting your records')
		popup.dismiss()
		#Deletes all the user saved buses using FB ID as a filter
		response = datadb.DeleteDBInfo().deleteAllUserRecords(app._facebookid)
		if (response.status_code == 200):
			app._toast('Your account has been reset')
			app.all_saved_busstopNo = []
			app.all_saved_busno = []
		else:
			app._toast('Something went wrong. Cannot reset your account')



class askConfirmation(RelativeLayout):

	def setText(self, title, popup):
		if (title=="Logout"):
			self.ids.labelText.text = "Do you really want to LOGOUT?"
		elif (title=="Reset"):
			self.ids.labelText.text = "Are you sure that you want to RESET your account?"




class BusTimingScreen(Screen):
	#TEST VARIABLES
	_busstopid = 46429
	_serviceno = 911
	
	def getNextBusTime(self):
		Clock.schedule_once(self.updateNextBusTime,UPDATE_FREQUENCY)
		try:
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
			return BUS_SERVICE_ENDED

	def getSubsequentBusTime(self):
		Clock.schedule_once(self.updateSubsequentBusTime,UPDATE_FREQUENCY)
		try:
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
			return BUS_SERVICE_ENDED


	def updateNextBusTime(self, *args):
		self.ids["nextBusTime"].text = self.getNextBusTime()
	def updateSubsequentBusTime(self, *args):
		self.ids["subsequentBusTime"].text = self.getSubsequentBusTime()


	def getDateTimeNowLabel(self):
		Clock.schedule_once(self.updateDateTimeLabel,1)
		return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	def updateDateTimeLabel(self, *args):
		self.ids["dateTimeNowLabel"].text = self.getDateTimeNowLabel()

	def getBusStopID(self):
		return self.busInstance.getbusStopID()
	def getServiceNo(self):
		return self.busInstance.getServiceNo()


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

class FacebookUI_New_User(Screen):
    ''' Seems like there was a bug in the kv that wouldn't bind on 
    app.facebook.status, but only on post_status '''

    status_text = StringProperty()
    def __init__(self, **kwargs):
        super(FacebookUI_New_User, self).__init__(**kwargs)
        app.bind(facebook=self.hook_fb)
        self.status_text = 'Facebook Status: [b]{}[/b]\nMessage: [b]{}[/b]'.format('Not Connected','-')
        
    
    def hook_fb(self, app, fb):
        fb.bind(status=self.on_status)
        app.bind(post_status=self.on_status)
        
        #If login is done correctly, self.status will take upon this message
    def on_status(self, instance, status):
        self.status_text = \
        'Facebook Status: [b]{}[/b]\nMessage: [b]{}[/b]'.format(
            app.facebook.status, 
            app.post_status)



class FacebookUI_PC_New_User(Screen):
	facebook_id = ""
	isvalidUser = False

	def btnLoginPress(self, facebook_id):
		self.facebook_id = facebook_id
		#saveFacebookInfothread = Thread(target=self.validate_id,args=()).start()
		self.validate_id()

	def validate_id(self, *args):
		response = datadb.GetDBInfo().getUser(self.facebook_id)
		if (response==200):
			self.login_success(response)
		else: 
			self.login_fail()

	def login_success(self, response):
		app._facebookid = facebook_id
		app._firstname = response['record']['firstname']
		app._lastname = response['record']['lastname']
		app.root_widget.current = 'searchscreen'
		Clock.schedule_once(app._toast('Welcome Back {} {}!'.format(app._firstname, app._lastname)),0)

	def login_fail(self):
		Clock.schedule_once(app._toast('This is an invalid account ID. Please sign up using the mobile app'),0)

class AboutScreen(Screen):
	def on_pre_enter(self, *args):
		#Update Footer Buttons on enter
		self.ids['footer'].ids['footer_aboutpage_button'].ids['footer_aboutpage_button_image'].source = 'data/Troubleshooting_inactive.png'



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



class NUSNextBus(App):
	#Callback properties
	post_status = StringProperty('-')
	user_infos = StringProperty('-')
	facebook = ObjectProperty()
	
	#Class variables
	_facebookid = StringProperty('')
	_username = ''
	_firstname = ''
	_lastname = ''
	all_saved_busstopNo = []
	all_saved_busno = []
	isRecordRetrieved = False
	fb_userprofile = ObjectProperty()

	def build(self):
		global app
		app = self

		#Creating presentation retains an instance that we can reference to
		root_widget = Builder.load_file("layout.kv")
		#Saves a Reference of the Screen Manager
		self.root_widget = root_widget
		return root_widget
	
	def on_start(self):

		'''
		Load Modules required for Facebook Login
		'''
		self.facebook = Facebook(FACEBOOK_APP_ID,permissions=['publish_actions', 'basic_info'])
		#Sets up the AskUser() and PopUp() to ask for connection
		global modal_ctlon_start
		modal_ctl = ModalCtl()
		#Define callback as modal_ctl.ask_connect()
		netcheck.set_prompt(modal_ctl.ask_connect)
		self.facebook.set_retry_prompt(modal_ctl.ask_retry_facebook)


		'''
		Load Bus Stop Directory
		'''
		#Retrieve Bus Stop Details from CSV
		self.datamall_bus_stop = datamall_bus_stop.BusStop()


		'''
		Load Facebook Profile
		'''
		#Check if this is the first login
		self.fb_userprofile = userprofile.UserProfile(self.user_data_dir)
		#If existing user, IS_EXISTINGUSER=True
		self.IS_EXISTINGUSER = self.fb_userprofile.isExistingUser
		#If existing user, USER_PROFILE will not be an empty dict
		self.USER_PROFILE = self.fb_userprofile._user_profile

		if platform == 'android':
			if self.IS_EXISTINGUSER:
				#Loads Screen for existing Users
				self.root_widget.current = 'searchscreen'
				self._facebookid = self.USER_PROFILE['facebook_id']
				self._firstname = self.USER_PROFILE['firstname']
				self._lastname = self.USER_PROFILE['lastname']
			else:
				#Loads Screen for new users
				self.root_widget.current = 'accountsettings'

		#Not on android
		else:
			self.root_widget.current = 'PCaccountsettings'

		'''
		Update Footer for Search Screen(the main screen)
		'''
		self.root_widget.ids['searchbusscreen'].ids['footer'].ids['footer_search_button'].ids['footer_search_button_image'].source = 'data/Searches Folder_inactive.png'


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
				self.saveFacebookInfoThread()
			#if this platform is not android
			else:
				infos = ['ha', 'ha', 'wish', 'this', 'was', 'real']
			self.user_infos = '\n'.join(infos)
		self.facebook.me(callback)

	#separate thread to save basic user information
	def saveFacebookInfoThread(self):
		saveFacebookInfothread = Thread(target=self.savefacebookinfo,args=()).start()

	#callback for saving user information
	def savefacebookinfo(self):
		#Create the FB USER CSV. Info is saved locally
		userprofile.UserProfile(self.user_data_dir, self._facebookid, self._firstname, self._lastname)

		#Use Identifier of the record to retrieve response code from 'users' table
		response = datadb.GetDBInfo().requestRecordByIdentifier("users",self._facebookid)
		Logger.info('Finding user from DreamFactory RESTful API. Response Code: {}'.format(response))
		#If record does not exist, create new FacebookID
		if response.status_code != 200:
			response = datadb.PostDBInfo().createUserTableRecords(self._facebookid,self._firstname+self._lastname,self._firstname,self._lastname)
			Logger.info('Creating user from DreamFactory RESTful API. Response: {}'.format(response))
			
	def awaitingUserChangeScreen(self):
		changeUserScreenThread = Thread(target=self.checkFacebookLoginDone,args=()).start()
	
	def checkFacebookLoginDone(self, *args):
		while not self._facebookid:
			time.sleep(1)
		#Login in Ok!
		Clock.schedule_once(self.newUserChangeScreen,0)

	def newUserChangeScreen(self, *args):
		#Login is okay, change screen!
		self._toast('Welcome {} {}'.format(self._firstname, self._lastname))
		self.root_widget.current = 'searchscreen'

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
	NUSNextBus().run()
