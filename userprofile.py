import csv
import shutil
import os
from kivy.logger import Logger




#Runs on APP start (Bind a callback here)
#Runs on Login (use Callback)

class UserProfile():

	isExistingUser = False
	_user_profile = {}
	USER_PROFILE_CSV_PATH = ''
	USER_PROFILE_DIR_PATH = ''

	info_required = ['facebook_id','firstname','lastname']

	def __init__(self, user_data_dir, facebook_app_id=None, firstname=None, lastname=None):

		Logger.info("userprofile: {}".format(user_data_dir))#/sdcard/screenmanager
		self.USER_PROFILE_CSV_PATH = user_data_dir+'/User/profile.csv'
		self.USER_PROFILE_DIR_PATH = os.path.dirname(self.USER_PROFILE_CSV_PATH)

		#DIR CHECK
		if not os.path.exists(self.USER_PROFILE_DIR_PATH):
			try:
				os.mkdir(self.USER_PROFILE_DIR_PATH)
				Logger.info('Making DIR')
			except:
				Logger.info('Unable to create DIR')


		if not os.path.exists(self.USER_PROFILE_CSV_PATH):
			Logger.info('userprofile: CSV does not exist')
			#We have the details
			#If logged in write, else do not create the CSV
			if facebook_app_id:
				Logger.info('userprofile: User is logged in!')

				try:
					with open(self.USER_PROFILE_CSV_PATH, 'wb') as user_profile:
						Logger.info('userprofile: Creating CSV')
						csv_writer = csv.writer(user_profile)

						csv_writer.writerow([facebook_app_id, firstname, lastname])

						_user_profile['facebook_id'] = str(facebook_app_id)
						_user_profile['firstname'] = str(firstname)
						_user_profile['lastname'] = str(lastname)

						#Now an existing user
						self.isExistingUser = True

						
				except IOError as e:
					#Most likely no read permissions
					Logger.info("userprofile: Unable to open file {}".format(e)) 

		#isExisting User, 
		#Pass DIR and FILE Check
		else:
			self.isExistingUser = True

			#Read the CSV, load the details
			with open(self.USER_PROFILE_CSV_PATH, 'rb') as user_profile:
				Logger.info('Reading existing CSV')
				USER_PROFILE = csv.reader(user_profile)

				for each_line in USER_PROFILE:

					#0=Facebook APP ID, #1=First Name, #2=Last Name
					self._user_profile = {}

					try:
						for (each_key, col) in zip(self.info_required, range(len(self.info_required))):
							self._user_profile[each_key] = each_line[col]

					except:
						#The file exists but something is wrong
						Logger.info('userprofile: Something is wrong with the USERFILE')

			if not len(self._user_profile.keys()) is len(self.info_required):
				self.removeUSER()
				UserProfile(facebook_app_id, firstname, lastname)


	def removeUSER(self):
		try:
			#Remove the DIR
			Logger.info("userprofile: Deleting the DIR {}".format(str(self.USER_PROFILE_DIR_PATH)))
			shutil.rmtree(self.USER_PROFILE_DIR_PATH)

		except OSError as e:
			Logger.info("userprofile: {}".format(e))
		
