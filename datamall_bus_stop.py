import csv
#from kivy.logger import Logger

BUS_STOP_CSV_PATH = 'data/BusStop_Jan2015.csv'

class BusStop():
	#Instance is created when information is requested
	bus_stop_directory = {}

	def __init__(self):
		#open the CSV file
		with open(BUS_STOP_CSV_PATH) as BUS_DATA:
			bus_data_csv_read = csv.reader(BUS_DATA)

			#iterate through the CSV list and find a matching bus stop number in column 0
			#About 4600 bus stops in Singapore as of Jan 2015
			for each_entry in bus_data_csv_read:
				#0=bus stop number, #1 = ShortCode, #2=Bus Stop Name
				#Stores both code and name as a nested list in the dictionary
				#self.bus_stop_directory[str(each_entry[0])] = [each_entry[1], each_entry[2]]
				self.bus_stop_directory[str(each_entry[0])] = each_entry[2]

	def getBusStopName(self, _busstop_id):
		#0=Short Code, #1=Bus Stop Name
		try:
			return '{}'.format(self.bus_stop_directory[_busstop_id])
		
		except KeyError:
			return 'Cannot find Bus Stop ID {}'.format(_busstop_id)

	#Outputs list for listview suggestions
	def busnamesubstringSearch(self, _searchstring):
		response = []
		for each_key in self.bus_stop_directory:
			#0=the bus stop short code, #1=the bus stop name
			#searches the upper case
			if _searchstring.upper() in self.bus_stop_directory[each_key]:
				response.append({
					'text': str(self.bus_stop_directory[each_key]), 
					'is_selected':False
					})
		return response

	def searchBusStopCode(self, _searchstring):
		for each_key in self.bus_stop_directory:
			if _searchstring == self.bus_stop_directory[each_key]:
				return each_key
		return None	