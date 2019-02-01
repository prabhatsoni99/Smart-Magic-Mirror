"""
Magic/Smart Mirror: A mirror where you can see yourself + some text/images
Coders - Anshul, Prabhat

All ouptput is black & white
Black -> What is to be reflected (area where you see yourself)
White -> What is to be absorbed (area where you see the text/images)

Designed to not require any inputs from user
Only physical connection to the Raspberry pi is the monitor screen

Dimensions of fullscreen are approx 1200 X 700 (x,y)

xyz_module calls other functions, if needed.
Just call the respective xyz_module and you're sorted

after() method format -> window.after(2 * 1000, func)
Here 2 is the number of seconds after which to execute the function again

Terminology: L1 -> 1st label, L2 -> 2nd label, .......

Contains:-
date_module()
time_module()
weather_module()
news_module()
events_module()
gmail_module()  this needs email and passwd
"""

from __future__ import print_function #for events
from tkinter import *
import datetime
import urllib.request
import geocoder #latitude,longitude - weather
import requests #news
#for events:-
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth.transport.requests
#for gmail:-
import smtplib
import time
import imaplib
import email



#time - Bell MT





def time_module():
	"""
	Manages all the time related stuff
	Outputs time in HH:MM format (final version) & HH:MM:SS format (testing version)
	Time error depends on window.after() associated with time_module()
	Eg. If process is repeated every 10 secs, error = +- 10 secs which is ok
	"""
	time = datetime.datetime.now().time()	
	time = str(time)
	pos = time.find(".")
	time = time[:pos] #This is the time we want in format HH:MM:SS
	time = time[:pos-3]#To do in final display. format HH:MM

	L1 = Label(window,text = time, fg = "white", bg = "black",font = "BellMT 50")
	L1.place(x = 500,y = 50)
	window.after(8353, time_module) #updates after 7 secs




def date_module():
	"""
	Manages all the date related stuff
	"""
	curr_date = datetime.datetime.now().date()
	a = curr_date.strftime("%A") #day of week like thursday, friday
	b = curr_date.strftime("%b") #3 letter month like jan,feb
	c = curr_date.strftime("%d") #day number in month like 06,23

	L1 = Label(window, text = a + ", " +  b + " " + c, fg = "white", bg = "black", font = "Helvetica 18")
	L1.place(x = 500,y = 140)
	window.after(13751, date_module) #updates after 5 mins




def get_weather():
	"""
	https://api.darksky.net/forecast/[key]/[latitude],[longitude]
	returns summary_useful, temp_useful
	temp -> temperature
	"""

	g = geocoder.ip('me') #An object of that uses the computer's IP address
	#Using this means no hardcoding the location
	latitude = str(g.latlng[0])
	longitude = str(g.latlng[1])

	weather_api_token = "98947546ad9ca9997c5d4e9577b84f3d" #I created this & the user doesn't need to change this
	URL = "https://api.darksky.net/forecast/" + weather_api_token + "/" + latitude + "," + longitude
	req = urllib.request.Request(URL)
	webpage = urllib.request.urlopen(req).read()
	webpage = str(webpage) #We have our JSON-type webpage in str datatype now

	#Operations for summary:-
	summary_start = webpage.find("\"summary\":")
	summary_end = webpage.find("," , summary_start)
	summary_useful = webpage[summary_start+11:summary_end-1]

	#operations for temperature:-
	temp_start = webpage.find("\"temperature\":")
	temp_end = webpage.find("," , temp_start)
	fahr_str_temp = webpage[temp_start+14:temp_end]
	#below is conversion from fahr_float_temp to celsius_int_temp
	#fahr -> fahrenheit
	fahr_float_temp = float(fahr_str_temp)
	celsius_int_temp = (fahr_float_temp - 32) * (5/9)
	celsius_int_temp = int(celsius_int_temp)
	temp_useful = str(celsius_int_temp) + "°C"

	return summary_useful, temp_useful




def weather_module():
	"""Manages all the weather(temperature,summary) related stuff
	"""
	summary,temp = get_weather()
	L1 = Label(window,text = summary, fg = "white", bg = "black",font = "Helvetica 16 bold") #The summary in English
	L1.place(x = 500,y = 150)
	L2 = Label(window,text = temp, fg = "white", bg = "black",font = "Helvetica 30 bold") #The temperature in celsius
	L2.place(x = 500,y = 200)
	window.after(21139, weather_module) #updates after 2 mins




def news_module():
	"""
	Displays top 3 news
	API taken from BBC
	Our API is 04ff9e73215d4a86890ad6a1a2c12ded
	"""

	main_url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=04ff9e73215d4a86890ad6a1a2c12ded"
  
	# fetching data in json format
	open_bbc_page = requests.get(main_url).json()

	# getting all articles in a string article
	article = open_bbc_page["articles"]

	results = [] #This list will contain all the news

	for ar in article:
		results.append(ar["title"])

	results = results[:3] #Only leaving the top 5 news headlines

	for i in range(3):
		#Here Li actually means L1,L2,L3,L4,L5
		#Same label name (variable) can be used to create many labels
		#That's why this works
		Li = Label(window, text = results[i], fg = "white", bg = "black", wraplength = 450, justify = LEFT, font = "Courier 16")
		Li.place(x = 300,y = 1050 + i*100)
		#Values of y coordinate are 100,150,200,250,300
		
	window.after(24481, news_module) #updates after 5 mins




def events_module():
	"""We are using google calender
	"""
	"""Shows basic usage of the Google Calendar API.
	Prints the start and name of the next 10 events on the user's calendar.
	"""

	# If modifying these scopes, delete the file token.pickle.
	SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		lol = open('token.pickle', 'rb')
		#print(lol)
		creds = pickle.load(lol)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(google.auth.transport.requests.Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			creds = flow.run_local_server()
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API
	now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
	#print('Getting the upcoming 10 events')
	events_result = service.events().list(calendarId='primary', timeMin=now,
										maxResults=3, singleEvents=True,
										orderBy='startTime').execute()
	events = events_result.get('items', [])

	if not events:
		L0 = Label(window, text = "No upcoming events", fg = "white", bg = "black", font = "Verdana 18 italic")
		L0.place(x = 50,y = 50)
	ctr = 0
	for event in events:
		#will break when ctr=3 anyways as we have set maxresults = 3
		event_datetime_str = event['start'].get('dateTime', event['start'].get('date'))
		description = str(event['summary'])

		#sorting datetime related stuff, converting to datetime.timedelta, and outputting as str
		pos = event_datetime_str.find("+")
		event_datetime_str = event_datetime_str[:pos]
		datetime_event_object = datetime.datetime.strptime(event_datetime_str, '%Y-%m-%dT%X')
		difference_object = datetime_event_object - datetime.datetime.now()
		difference_datetime_str = str(difference_object)
		pos_cool = difference_datetime_str.find(":")
		difference_datetime_str = difference_datetime_str[:pos_cool] + " hrs later "
		#print(difference_datetime_str)


		L1 = Label(window, text = description, fg = "white", bg = "black", font = "ErasDemi 18", wraplength = 400)
		L2 = Label(window,text = difference_datetime_str,fg = "white", bg = "black", font = "Architext 12", wraplength = 400)
		L1.place(x = 50,y = 30 + 80*ctr)
		L2.place(x=50,y=65 + 80*ctr)
		ctr +=1

	window.after(16519, events_module) #updates after 16 secs (testing)




def gmail_module():
	FROM_EMAIL  = "kapsmirror@gmail.com"
	FROM_PWD    = "magicmirror"
	SMTP_SERVER = "imap.gmail.com"
	SMTP_PORT   = 993
	try:
		mail = imaplib.IMAP4_SSL(SMTP_SERVER)
		mail.login(FROM_EMAIL,FROM_PWD)
		mail.select('inbox')	
		counter=0

		type, data = mail.search(None, 'ALL')
		mail_ids = data[0]

		id_list = mail_ids.split()

		for i in reversed(id_list):
			typ, data = mail.fetch(i, '(RFC822)' )
			if(counter==3):
				break    #displays only first 3 mails
			for response_part in data:
				if isinstance(response_part, tuple):
					msg = email.message_from_string(response_part[1].decode('utf-8'))
					email_subject = msg['subject']
					email_from = msg['from']
					email_from = email_from.split('<')[0]
					if(email_from[0]=='"'):
						email_from=email_from[1:len(email_from)-2]
					#print(email_from)

					height = 1100 + counter*80
					L1 = Label(window, text = email_from + ": " + email_subject, fg = "white", bg = "black", wraplength = 220, justify = LEFT, font = "Times 16")
					L1.place(x = 50,y = height)
					counter = counter+1
					
	
	except Exception as e:
		print(str(e))
	window.after(9829, gmail_module) #updates after 9 secs (testing)





"""
Landscape -> 1300 x 700
Vertical -> 700 x 1300
how to set font,fontsize -> label.config(font=("Courier", 44))
"""



window = Tk() #Creating the object i.e. the window
window.configure(background='black')
window.attributes("-fullscreen", True)


date_module()
time_module()
weather_module()
news_module()
events_module()
gmail_module()


def exitprogram(): #comment this out in final product
	window.destroy()
	exit()
#We use this button as we are in fullscreen and there's no way for us to exit
B1 = Button(window, text = "Exit", fg="red", command = exitprogram)
B1.place(x = 300, y = 300)


#The following functions occur infinitely after the given time period
window.after(8353, time_module) #updates after 8 secs max
window.after(13751, date_module) #updates after 13 secs (testing)
window.after(21139, weather_module) #updates after 21 secs (testing)
window.after(24481, news_module) #updates after 24 secs (testing)
window.after(16519, events_module) #updates after 16 secs (testing)
window.after(9829, gmail_module) #updates after 9 secs (testing)

window.mainloop()
