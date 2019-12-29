#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbTools python scripts 
# some helper scripts for import
#
# Created by Oliver Albold 2019
#
# ################################################################

# read configuartion from dbtools config file


import configparser
import MySQLdb
import os
from StringIO import StringIO

#change here the location of the config file:
configFile = '/etc/openhab2/scripts/dbtools.ini'

parser = configparser.ConfigParser()
parser.read(configFile)

#section root
try:
	rootPath = parser['root']
	try:
		rootPath = parser['root']['path']
	except:
		print ("Error w	ith 'path=' not defined in dbtools.cfg [root] section" )
		quit()
	try:
		delimiter = parser['root']['delimiter']
	except:
		delimiter = ','
except:
	rootPath = '/etc/openhab2/data'
	delimiter = ','

#section dbconfig	
try:
	dbHost = parser['dbconfig']['host']
except:
	print ("Error with 'host=' not defined in dbtools.cfg [dbconfig] section" )
	quit()
	
try:
	dbUser = parser['dbconfig']['user']
except:
	print ("Error with 'user=' not defined in dbtools.cfg [dbconfig] section" )
	quit()
	
try:
	dbPassWord = parser['dbconfig']['password']
except:
	print ("Error with 'password=' not defined in dbtools.cfg [dbconfig] section" )
	quit()

try:
	dbTable = parser['dbconfig']['table']
except:
	print ("Error with 'table=' not defined in dbtools.cfg [dbconfig] section" )
	quit()
	
#dection maintenance

try:
	dbDays = int(parser['maintenance']['days'])
except:
	#not defined!
	dbDays = -1



#section timesheet1-9
class cTimeSheet:
	def __init__(self):
		self.name = ""
		self.path = ""
		self.item = ""
		
timeSheets = []
	
for ts in range(1,10):
	tsName = 'timeSheet%d' % ts
	if tsName in parser:
		timeSheets.append( cTimeSheet() )
		try:
			timeSheets[-1].name = parser[tsName]['name']
		except:
			print ("Error with 'name=' not defined in dbtools.cfg [%s] section" % tsName )
			quit()
		try:
			timeSheets[-1].item = parser[tsName]['item']
		except:
			print ("Error with 'item=' not defined in dbtools.cfg [%s] section" % tsName )
			quit()
		try:
			timeSheets[-1].path = os.path.join(rootPath,parser[tsName]['path'])
		except:
			print ("Error with 'name=' not defined in dbtools.cfg [%s] section" % tsName )
			quit()
		try:
			timeSheets[-1].on = parser[tsName]['on']
		except:
			timeSheets[-1].on = 'on'
		try:
			timeSheets[-1].off = parser[tsName]['off']
		except:
			timeSheets[-1].off = 'off'
		try:
			timeSheets[-1].total = parser[tsName]['total']
		except:
			timeSheets[-1].total = 'total'
		try:
			timeSheets[-1].date = parser[tsName]['date']
		except:
			timeSheets[-1].date = 'date'
		timeSheets[-1].events = int(parser[tsName]['events'])
		try:
			timeSheets[-1].events = int(parser[tsName]['events'])
		except:
			timeSheets[-1].events = 2
	
#section timesheet1-9
class cTracks:
	def __init__(self):
		self.name = ""
		self.path = ""
		self.item = ""
		
tracks = []
	
for t in range(1,10):
	tName = 'dailyTrack%d' % t
	if tName in parser:
		tracks.append( cTracks() )
		try:
			tracks[-1].name = parser[tName]['name']
		except:
			print ("Error with 'name=' not defined in dbtools.cfg [%s] section" % tName )
			quit()
		try:
			tracks[-1].item = parser[tName]['item']
		except:
			print ("Error with 'item=' not defined in dbtools.cfg [%s] section" % tName )
			quit()
		try:
			tracks[-1].path = os.path.join(rootPath,parser[tName]['path'])
		except:
			print ("Error with 'name=' not defined in dbtools.cfg [%s] section" % tName )
			quit()
	
#open the configure data base
def openDataBase():
	db = MySQLdb.connect (host = dbHost, 	# your host, usually localhost
						user = dbUser,		# your username
						passwd = dbPassWord,	# your password
						db = dbTable)		# name of the data base
	return db								

#close the configured data base
def closeDataBase(db):
	db.close()


