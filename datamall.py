#native libraries
import urllib
import json
from urlparse import urlparse
import re

#External libraries
import httplib2 as http 


#References
#Request maker
#http://requestmaker.com/
#documentation
#http://www.mytransport.sg/content/dam/mytransport/DataMall_StaticData/LTA_DataMall_API_User_Guide.pdf

#LTA Datamall API key
#1DxxvzbHwydZ3uw6UKNA9w==
#GUID
#687ef57c-810a-414a-b0f8-df4b78bf9ef6


#BUS ARRIVAL API
#API URL: http://datamall2.mytransport.sg/ltaodataservice/BusArrival


class BusInfo(object):

    #def printbus(self, busNo):
    #    print busNo["Name"]                 #nextBus, subsequentBus
    #    print busNo["Load"]                 #Seating available? Standing available?
    #    dateandtime = re.split(r'T',busNo["EstimatedArrival"])
    #    date = dateandtime[0]
    #    time = re.split(r'\W',dateandtime[1])
    #    print date
    #    print time
    #    print busNo["Feature"] 

    def __init__(self,busstopid,serviceno):
        #authentication parameters
        headers = {'AccountKey' : '1DxxvzbHwydZ3uw6UKNA9w==',
                    'UniqueUserId' : '687ef57c-810a-414a-b0f8-df4b78bf9ef6',
                    'accept' : 'application/json' 
                    }
    
        #API parameters
        url = 'http://datamall2.mytransport.sg/ltaodataservice'
        path = '/BusArrival?'
        
        #Query parameters
        params = {'BusStopID' : str(busstopid), 
                    'ServiceNo' : str(serviceno)}
        self.params = params 
         
        #Build query string and specify type of API Call
        target = urlparse(url+path+urllib.urlencode(params) )#;print target.geturl()
        method = 'GET'
        body = ''
        
        #Get handle to handle http
        h = http.Http()
        
        #Sends GET Request
        response, content = h.request(target.geturl(), method, body, headers)
        
        #Parse JSON to print
        self.dumpout = json.loads(content)

    #SINGLE BUS TEST REPONSE
    def scrapeBusInfo(self):
        #Scraping information from hash table
        self.nextBus = self.dumpout["Services"][0]["NextBus"]
        self.subsequentBus = self.dumpout["Services"][0]["SubsequentBus"]

    def getNextTiming(self):
        return self.nextBus["EstimatedArrival"]
    
    def getSubsequentTiming(self):
        return self.subsequentBus["EstimatedArrival"]

    def getNextLoad(self):
        return self.nextBus["Load"]
    def getSubsequentLoad(self):
        return self.subsequentBus["Load"]

    def getNextFeature(self):
        return self.nextBus["Feature"]
    def getSubsequentFeature(self):
        return self.subsequentBus["Feature"]    

    #Gets the bus stop in request. Returns a string
    def getbusStopID(self):
        return self.params['BusStopID']

    #Gets the service number in request. Returns a string
    def getServiceNo(self):
        return self.params['ServiceNo']
    
    #Gets the list of services. Returns a list of nested dictionary
    def getallServices(self):
	return self.dumpout["Services"]

    #DEBUG::Gets Raw JSON Output
    def getJSONdump(self):
	return self.dumpout
