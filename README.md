# Orbital2015---NUS-Next-Bus-2
This aims to retrieve public bus arrival timings as well as NUS's internal shuttle bus arrival timings for NUS students 


Overview:
The NUS Next Bus 2 application aims to allow students to retrieve the arrival timing of the public buses at various bus stops around the NUS Campus. This is because several NUS Bus stops, especially the ones along the main road leading to the Central Library provides internal bus shuttle services and public bus services such as Bus 96.

However, only internal bus arrival timings are provided in the prevalent “NUS Next Bus application”. Information regarding public buses are unfortunately unavailable in the native application.

NUS Next Bus 2 aims to provide all-rounded travel information including arrival timings for public buses, for students to better plan their journey to and fro and around the school campus (if they heavily utilise bus services)

The basic idea is to collect the user’s input in the form of the Bus Stop Code, Bus Service number to access the LTA Datamall database. If the Bus Stop Code happens to be a bus stop located within NUS, additional bus arrival timings of NUS’s Shuttle Service will be provided. The mobile application shall be targeted for launch on the Android Lollipop platform.

Hopefully, NUS Office of Student Affairs (OSA)  will be able to provide us with some form of access to their Bus Arrival System. (A request will be sent to them)

 

1. Ideation:
Some NUS Students and Freshmen find it difficult to inquire about the shuttle bus service timings as ‘NUS Next Bus’ requires the user to search for the bus stop name before they can find out how longer they have to wait.

Other NUS Students that have multiple travel routes to Kent Ridge, Clementi or Jurong East find it cumbersome to additionally open the Transit Link Application to check out the timing for the public bus arrival timings.

NUS Next Bus 2 aims to merge the 2 applications together and features user preferences to save preferred bus stops to access the arrival timings quickly on the home screen.

 

Projected Time Line: https://onedrive.live.com/redir?resid=d0d952fc3907e36e!4088&authkey=!AC4KEnKf1Act7cA&v=3&ithint=photo%2cpng

 

2. Projected KPI
Milestone 1: 2 June 2015

Milestone 2: 27 June 2015

Milestone 3: 29 July 2015

Orbital Splashdown: 12 August 2015

 

2. Planned Features: https://onedrive.live.com/redir?resid=d0d952fc3907e36e!4090&authkey=!AB4d1ljyCJtZCdY&v=3&ithint=photo%2cPNG

3. Proposed level of achievement
Our team proposes that we should be granted Project Gemini (Intermediate) level of achievement. Firstly, NUS Next Bus 2 is an application that will feature the basic creation, retrieval and deletion of record, hopefully using FacebookID as a primary key in a 3rd form normalised mySQL table to save user preferences.

The launch of the app will be accompanied by a back-end process to query our user-developed mySQL DB for bus stop preferences saved previously.

Furthermore, the development of this Android Application aims to use Kivy as an alternative development platform. Besides, we aim to develop the application with a front-end settings screen, as well as a back-end administrative app to maintain a DB table with the buses available at the various bus stops within NUS.

 

Description

Feature

Back-end Requirements

For bus stops within NUS

Show all shuttle buses and public buses using <bus stop no>

Back-end DB for buses available at bus stops

For bus stops beyond NUS

Show arrival time of public buses using using <bus stop no> and <bus no>

N/A

Essentially, the application will feature a JSON GET request, Facebook openID user preferences page, an administrator bus stop DB table and will function as a mobile application in the Android operating environment. The DB will first be tested using a self-hosted mySQL DB. Subsequently, the DB will hopefully be transferred to a PaaS. This project will not at all involve a single bit of GAE.

 

4. References used
For Learning

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

