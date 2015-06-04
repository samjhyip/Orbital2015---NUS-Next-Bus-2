import urllib
import json
from urlparse import urlparse
import re
import httplib2 as http #External library


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


class GetBusInfo(object):

    #def printbus(self, busNo):
    #    print busNo["Name"]                 #nextBus, subsequentBus
    #    print busNo["Load"]                 #Seating available? Standing available?
    #    dateandtime = re.split(r'T',busNo["EstimatedArrival"])
    #    date = dateandtime[0]
    #    time = re.split(r'\W',dateandtime[1])
    #    print date
    #    print time
    #    print busNo["Feature"] 

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

    def getSubsequentLoad(self):
        return self.subsequentBus["Feature"]    

    def __init__(self):
        #authentication parameters
        headers = {'AccountKey' : '1DxxvzbHwydZ3uw6UKNA9w==',
                    'UniqueUserId' : '687ef57c-810a-414a-b0f8-df4b78bf9ef6',
                    'accept' : 'application/json' 
                    }
                    
        #API parameters
        url = 'http://datamall2.mytransport.sg/ltaodataservice'
        path = '/BusArrival?'
        
        #Query parameters
        params = {'BusStopID' : '46429', 
                    'ServiceNo' : '911'}
                    
        #Build query string and specify type of API Call
        target = urlparse(url+path+urllib.urlencode(params) )#;print target.geturl()
        method = 'GET'
        body = ''
        
        #Get handle to handle http
        h = http.Http()
        
        #Sends GET Request
        response, content = h.request(target.geturl(), method, body, headers)
        
        #Parse JSON to print
        dumpout = json.loads(content)
        self.nextBus = dumpout["Services"][0]["NextBus"]
        self.subsequentBus = dumpout["Services"][0]["SubsequentBus"]
    
    