import requests 
from bs4 import BeautifulSoup
import re
import time
import cookielib
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

#######################################################CONFIG
urlBase = 'http://www.registrar.ucla.edu/schedule/'

#Input class info that you want to GET ENROLLED in

#Ex. 14F for Fall 2014 or 15W for Winter 2015
term = '15W'

#The department Ex. 'COM+SCI'
subjectarea = 'SCAND'

#The actual course number/ID
courseid = '0050'

#does this class have pre-reqs? restrictions? impacted? transaction fee? set to # of checks needed if true or 0(false) 
haveReqs = 0
haveRestrictions = 0
isImpacted = 0
misc = 1

#input how many different time conflicts you have for wanted class
hasConflicts = 0

#Class filter list, LIST ALL CLASSES YOU ARE 'OK' WITH 
#Ex. '1A' or '2B'
sectionFilter = ['1']

#myUCLAlogininfo
url = "http://my.ucla.edu"
username = "USER"
pw = "PASSWORD"

#sleep time interval between attempts (in seconds)
sleepInterval = 20

####################################################### XPATH INFO
xpaths = { 'signInBox' : "/html/body/form/div[3]/div[3]/div/div[2]/div[1]/div[1]/div/div[2]/div[2]/a[1]",
			'usernameField' : "/html/body/div[1]/div[2]/div[1]/form/div[1]/input",
			'pwField' : "/html/body/div[1]/div[2]/div[1]/form/div[2]/input",
			'signInBox2' : "/html/body/div[1]/div[2]/div[1]/form/div[3]/input",
			'advancedSearch' : "/html/body/div[1]/div[3]/div/div[2]/div[1]/div/form/div[3]/a/div/div[2]/h3",
			'searchByCriteria' : "/html/body/div[1]/div[3]/div/div[2]/div[1]/div/form/div[4]/div[1]/div[2]/div[2]/select",
			'classIDoption' : "/html/body/div[1]/div[3]/div/div[2]/div[1]/div/form/div[4]/div[1]/div[2]/div[2]/select/option[2]",
			'classIDfield' : "/html/body/div[1]/div[3]/div/div[2]/div[1]/div/form/div[4]/div[1]/div[3]/div[2]/div/input",
			'searchButton' : "/html/body/div[1]/div[3]/div/div[2]/div[1]/div/form/div[4]/div[4]/button[1]",
			'checkboxDisc' : "/html/body/div[1]/div[3]/div/div[2]/div[2]/div/div/div[3]/div/div[2]/div/div/div[2]/div/div[1]/input",
			'enrollButton' : "/html/body/div[1]/div[3]/div/div[2]/div[2]/div/div/div[3]/div/div[2]/div/div/div[2]/div/div[10]/div[2]/div/div[10]/div/div/div/div[2]/ul/li[1]/button",							 
			'preReqWarning' : "/html/body/div[1]/div[3]/div/div[2]/div[2]/div/div/div[3]/div/div[2]/div/div/div[2]/div/div[10]/div[2]/div/div[10]/div/div/div/div[2]/div[4]/label/input",
			'checkBUtton' : "/html/body/div[1]/div[3]/div/div[2]/div[2]/div/div/div[3]/div/div[2]/div/div/div[2]/div/div[10]/div[2]/div/div[10]/div/div[1]/div/div[2]/div[4]/label/input",
                        'enrollButton' : "/html/body/div[1]/div[3]/div/div[2]/div[2]/div/div/div[3]/div/div[2]/div/div/div[2]/div/div[10]/div/div[2]/div/div[2]/ul/li[1]/button"
}
########################################################
/html/body/

def getURL(term, subject, id):
	return urlBase + 'detselect.aspx?termsel=%s&subareasel=%s&idxcrs=%s' % (term, subject, id)

def getCell(cell):
	return ' '.join(cell.stripped_strings)

def parse_table(parse_table):
	data = []
	for row in table.findall('tr'):
		row_data=map(cell_text, row.find_all(re.compile('t[dh]')))[::2]	

def getTally(isWaitlisted,haveReqs,haveRestrictions,isImpacted,numConflicts,misc):
	return isWaitlisted + haveReqs + haveRestrictions + isImpacted + numConflicts + misc

def login (classid, numChecks):
	try:
		driver = webdriver.Firefox()
		driver.get(url)
		#driver.maximize_window()

		#Click signInBox
		driver.find_element_by_xpath(xpaths['signInBox']).click()

		#Clear and Enter username
		driver.find_element_by_xpath(xpaths['usernameField']).clear()
		driver.find_element_by_xpath(xpaths['usernameField']).send_keys(username)

		#Clear and Enter pw
		driver.find_element_by_xpath(xpaths['pwField']).clear()
		driver.find_element_by_xpath(xpaths['pwField']).send_keys(pw)

		#Click sign in
		driver.find_element_by_xpath(xpaths['signInBox2']).click()

		driver.implicitly_wait(5)
		driver.get('https://sa.ucla.edu/ro/classsearch/')

		#Set to classIDoption
		driver.find_element_by_xpath(xpaths['advancedSearch']).click()
		#driver.find_element_by_id('advSearch_header').click()
		#driver.implicitly_wait(1)
		driver.find_element_by_xpath(xpaths['classIDoption']).click()

		#Input classid and click search
		driver.find_element_by_xpath(xpaths['classIDfield']).clear()
		driver.find_element_by_xpath(xpaths['classIDfield']).send_keys(classid)
		driver.find_element_by_xpath(xpaths['searchButton']).click()

		#click checkboxes
		driver.find_element_by_xpath(xpaths['checkboxDisc']).click()

		#in case internet lags
		time.sleep(2)

		if (numChecks > 0):
			x = 0
			while (x < numChecks):
				k = 1 + (x*2)
				k = k + 48
				addon = chr(k)
				objectid = 'enroll_warning_flyout_warning_checkbox' + addon
				print 'Clicking checkbox: %s' % (objectid)
				x += 1
				driver.find_element_by_id(objectid).click()

		
		driver.find_element_by_xpath(xpaths['enrollButton']).click()
		print 'Successfully enrolled!'
		return 1

	except NoSuchElementException:
		driver.close();
		print 'Enrollment failed.. There was some error while enrolling.'
		return 0

#######################################################MAIN
response = requests.get( getURL(term, subjectarea, courseid) )

#print response.status_code
#print response.text.encode('utf8') - TO see the text extracted

flag = 0

while(flag == 0):
	soup = BeautifulSoup(response.text)
	print 'Checking for open/waitlist classes...'

	#Create a table 
	idnumbers = []
	enrolled = []
	enrolledcap = []
	waitlist = []
	waitlistcap = []
	statuses = []
	sectionnum = []

	#Extract ID number, enrolled, enrolled capacity, etc

	for row in soup.find_all('td', 'dgdClassDataColumnIDNumber'):
		idnumbers.append(getCell(row))

	for row in soup.find_all('td', 'dgdClassDataEnrollTotal'):
		enrolled.append(getCell(row))

	for row in soup.find_all('td', 'dgdClassDataEnrollCap'):
		enrolledcap.append(getCell(row))

	for row in soup.find_all('td', 'dgdClassDataWaitListTotal'):
		waitlist.append(getCell(row))

	for row in soup.find_all('td', 'dgdClassDataWaitListCap'):
		waitlistcap.append(getCell(row))

	for row in soup.find_all('td', 'dgdClassDataStatus'):
		statuses.append(getCell(row))

	for row in soup.find_all('td', 'dgdClassDataSectionNumber'):
		sectionnum.append(getCell(row))

	#create table and put everything in

	table = []
	for section in range(0, len(idnumbers) ):
		section = [ idnumbers[section],enrolled[section],enrolledcap[section], waitlist[section], waitlistcap[section] , statuses[section] , sectionnum[section] ]
		table.append(section)

	##Things are either "Open" or "W-List" or "Closed"
	for row in table:
		if(row[6] in sectionFilter):
			print 'Lecture: %s is %s' % (row[0],row[5])
			if (row[5] == 'W-List' or row[5] == 'Open'):
				foundID = row[0]
				foundSectionNum = row[6]
				print 'Found! %s' % (foundID)

				boxes = 0

				if (row[5] == 'W-List'):
					boxes = getTally(1, haveReqs, haveRestrictions, isImpacted, hasConflicts, misc)
				else:
					boxes = getTally(0, haveReqs, haveRestrictions, isImpacted, hasConflicts, misc)

				print 'Enrolling for %s with %s number of checks' % (foundID, boxes)

				if (login(foundID,boxes) == 1):
					flag = 1

				break

	if (flag == 0):
		print 'Attempting again in 20s...\n'
		#CONFIGURE INTERVAL TIME HERE
		time.sleep(sleepInterval)

	else:
		continue
