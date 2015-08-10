from kivy.logger import Logger
from urlparse import urlparse
import urllib
import requests
import json


#References
#Request maker
#http://requestmaker.com/
#documentation
#http://www.mytransport.sg/content/dam/mytransport/DataMall_StaticData/LTA_DataMall_API_User_Guide.pdf

#LTA Datamall API key
#1DxxvzbHwydZ3uw6UKNA9w==
#GUID
#687ef57c-810a-414a-b0f8-df4b78bf9ef6

#Fb id example:884587561622028

#BUS ARRIVAL API
#API URL: http://datamall2.mytransport.sg/ltaodataservice/BusArrival


_user='DREAMFACTORY USERNAME HERE'
_pass='DREAMFACTORY PASSWORD HERE'


class GetDBInfo(object):

    def requestInfo(self,tables):
        headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
        response = requests.get('https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2/{}'.format(str(tables)),
                                 auth=(_user, _pass),headers=headers, verify=False)
        data = response.json()
        return response

    #Request record using single identifier 
    #getRecord(). Only when identifier is a unique key
    def requestRecordByIdentifier(self,tables,identifier):
        headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
        response = requests.get('https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2/{}/{}'.format(str(tables),str(identifier)),
                                 auth=(_user, _pass),headers=headers, verify=False)
        data = response.json()
        #print data
        Logger.info('requestRecordByIdentifier: {}'.format(response))
        return response

    #Request list (one or more records) using identifier
    #Works when identifier is not unique
    def requestSavedBusRecord(self, _id_field):
        headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
	
	url = 'https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2'
	path = '/SavedBuses?'
	params = {'filter': str(_id_field)}
	target = urlparse(url+path+urllib.urlencode(params))

        response = requests.get(target.geturl(),
                              auth=(_user, _pass),headers=headers, verify=False)
	
        #print data
        Logger.info('requestRecordByIdentifier: {}'.format(response))
	data = response.json()		
	return data



class PostDBInfo(object):

    def createBusTableRecords(self, bus_no):
        headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
        payload = {"record": [
                        {"bus_no": '{}'.format(bus_no)}
                      ]
                    }
        response = requests.post('https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2/buses',
                                 auth=(_user, _pass),headers=headers, data=json.dumps(payload),verify=False)
        print response.text
        return response

    def createUserTableRecords(self, facebook_ID, username, firstname, lastname):
        headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
        payload = {"record": [
                        {"facebook_ID": str(facebook_ID),
                        "username": str(username),
                        "firstname": str(firstname),
                        "lastname": str(lastname)
			}
                      ]
                    }
        response = requests.post('https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2/users',
                                 auth=(_user, _pass),headers=headers, data=json.dumps(payload),verify=False)
        print response.text
        return response

    def createUserSaveBusRecords(self, busno, busstopNo, Users_facebook_ID):
	headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
        payload = {"record": [
                {"busno": str(busno),
                "busstopNo": str(busstopNo),
                "Users_facebook_ID": str(Users_facebook_ID)
		}
              ]
            }
        response = requests.post('https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2/SavedBuses',
                                 auth=(_user, _pass),headers=headers, data=json.dumps(payload),verify=False)
        print response.text
        return response


class DeleteDBInfo(object):

    def deleteTableRecords(self):
        headers = {'X-DreamFactory-Application-Name' : 'nextbus2'}
        payload = {"record": [
                        {"bus_no": '999'}
                      ]
                    }
        response = requests.delete('https://dsp-samjhyip.cloud.dreamfactory.com/rest/nextbus2/'+str(tables),
                                 auth=(_user, _pass),headers=headers, data=json.dumps(payload),verify=False)
        print response.text
        return response


#ob1 = GetDBInfo().requestInfo('buses')
#ob1 = PostDBInfo().createBusTableRecords('999e')
#ob1 = DeleteDBInfo().deleteTableRecords()
#print GetDBInfo().requestRecordByIdentifier('Users',96)
