# Orbital2015---NUS-Next-Bus-2

LATEST DEBUG APK (v1.2.3): https://copy.com/K3KEnPmpTzhtLib9

This aims to retrieve public bus arrival timings as well as NUS's internal shuttle bus arrival timings for NUS students 


Overview:
The NUS Next Bus 2 application aims to allow students to retrieve the arrival timing of the public buses at various bus stops around the NUS Campus. This is because several NUS Bus stops, especially the ones along the main road leading to the Central Library provides internal bus shuttle services and public bus services such as Bus 96.
However, only internal bus arrival timings are provided in the prevalent “NUS Next Bus application”. Information regarding public buses are unfortunately unavailable in the native application.
NUS Next Bus 2 aims to provide all-rounded travel information including arrival timings for public buses, for students to better plan their journey to and fro and around the school campus (if they heavily utilise bus services)
The basic idea is to collect the user’s input in the form of the Bus Stop Code, Bus Service number to access the LTA Datamall database. If the Bus Stop Code happens to be a bus stop located within NUS, additional bus arrival timings of NUS’s Shuttle Service will be provided. The mobile application shall be targeted for launch on the Android Lollipop platform.
Hopefully, NUS Office of Student Affairs (OSA)  will be able to provide us with some form of access to their Bus Arrival System. (A request will be sent to them)

 
Ideation:
Some NUS Students and Freshmen find it difficult to inquire about the shuttle bus service timings as ‘NUS Next Bus’ requires the user to search for the bus stop name before they can find out how longer they have to wait.
Other NUS Students that have multiple travel routes to Kent Ridge, Clementi or Jurong East find it cumbersome to additionally open the Transit Link Application to check out the timing for the public bus arrival timings.
NUS Next Bus 2 aims to merge the 2 applications together and features user preferences to save preferred bus stops to access the arrival timings quickly on the home screen.
Projected Time Line: https://onedrive.live.com/redir?resid=d0d952fc3907e36e!4088&authkey=!AC4KEnKf1Act7cA&v=3&ithint=photo%2cpng

 
Achieved Features for:
1. Vostok - DB retrieval and Storage
2. Gemini - Used Kivy & Python-for-android
3. Gemini - JSON retrieval from LTA's datamall API and DreamFactory REST API
4. Gemini - Facebook Login
5. Gemini - Kivy application runs on different platforms (Tested on Android Lollipop and Jellybean and Windows)

 

Failed to achieve:
We did not manage to get the approval to access the NUS BUS API. In the request to OCA, they had replied that there are making changes to the bus contracts and are unable to share more about the API. The API listed in https://wiki.nus.edu.sg/display/nllapi/NUS+Living+Lab+API+Overview is now deprecated and thus unable to be used.
 

4. References used:
Kv Language documentation (http://kivy.org/docs/guide/lang.html)
MyTransport.SG:DataMall(http://www.mytransport.sg/content/mytransport/home/dataMall.html)
JSON Encoder/Decoder (https://docs.python.org/2/library/json.html)
Kivy-Android Package Builder, Buildozer documentation (http://kivy.org/docs/guide/packaging-android.html)
Kivy Basics (http://kivy.org/docs/guide/basic.html)
Kivy language syntax definition for Sublime Text (https://packagecontrol.io/packages/Kivy%20Language)
MySQL Connector for Python (https://pypi.python.org/pypi/MySQL-python)

For the documentation of NUS Next Bus 2

Google Sheets (https://drive.google.com/?pli=1&authuser=0#my-drive) for creating our project log (cut and pasted in here)
Trello (https://trello.com/) for feature making and card sorting.  Considered using Github Issues but decided to go for the card look.

