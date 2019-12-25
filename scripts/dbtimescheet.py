#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbTools python script to create a csv time sheet of
# switch items.
# Created by Oliver Albold 2019
#
# ################################################################

import MySQLdb
import sys
import os
import csv
import datetime
import dbtoolsconfig as config

db = MySQLdb.connect (host = config.dbHost, 	# your host, usually localhost
                      user = config.dbUser,		# your username
                      passwd = config.dbPassWord,	# your password
                      db = config.dbTable)		# name of the data base
							  
# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

def closeCvs(file):
	if file != None:
		file.close()
		
def convertDTtoHours( dt ):
	hours = dt.days * 24
	hours = hours + int(dt.seconds / 3600)
	minutes = int((dt.seconds % 3600) / 60)
	return float(hours) + float(minutes)/60

def createTimeSheet ( root, name , delimiter, columns, cur ):
	year = 0
	month = 0
	day = 0
	file = None
	c = []
	totalTime = None

	for entry in cur.fetchall():
		date = entry[0]
		state = entry[1]
		
		#check if we have a new day in the array of locations
		if date.year != year:
			year = date.year
			month = 0
			#create new directorey if necessary:
			path = os.path.join(root,"%04d/" % (year))
			if(not os.path.isdir(path)):
				try:
					os.makedirs( path )
				except:
					print ("Can not create: %s" % path)
					quit()
					
		#create new file if necessary
		if date.month != month:
			#first close exitiong file
			closeCvs(file)
			file = None
			day=0
				
			#open new file
			month = date.month
			filename = path+"%04d-%02d-%s.csv" % (year, month, name)
			#create only a new file if it does not exist already
			try:
				file = open( filename, "w+")
			except:
				print ("Can not create: %s" % filename)
				quit()
			cvsWriter = csv.writer( file, delimiter=delimiter )
			cvsWriter.writerow(columns)
			numberOfEvents=(len(columns)-2)/2
		if cvsWriter != None:
			#check for new 
			if day != date.day:
				if len(c) > 0:
					#write last row first before you cantinue with new one
					while( len(c) < (numberOfEvents*2)+1):
						c.append("")
					c.append( "%.2f h" % convertDTtoHours( timeDelta ) )
					cvsWriter.writerow(c)
					if totalTime==None:
						totalTime=timeDelta
					else:
						totalTime=totalTime+timeDelta
				day = date.day
				#create datetime at 00:00 this day:
				lastTime = datetime.datetime.strptime('%04d%02d%02d' % (year,month,day), '%Y%m%d')
				timeDelta = datetime.timedelta(0)
				currentState=None
				c = ["%04d-%02d-%02d" % (year,month,day)]
				currentEvent=0
			if currentEvent < numberOfEvents:
				if currentState==None and state=='OFF':
					if((date.hour > 0) or (date.minute > 0)):
						c.append("00:00")
						c.append( "%02d:%02d" % (date.hour, date.minute))
						timeDelta = timeDelta + (date - lastTime)
						lastTime=date
						currentState=state
					else:
						#skip 00:00 OFF value
						continue
				if currentState != state:
					c.append( "%02d:%02d" % (date.hour, date.minute))
					if state=='OFF':
						timeDelta = timeDelta + (date - lastTime)
					lastTime = date
					currentState=state
				if currentState == 'OFF':
					currentEvent=currentEvent+1
				

		#continue with next way point
	#write last row
	if len(c) > 0:
		#write last row first before you cantinue with new one
		while( len(c) < (numberOfEvents*2)+1):
			c.append("")
		c.append( "%.2f h" % convertDTtoHours( timeDelta ) )
		cvsWriter.writerow(c)		
		#write total time row.
		if totalTime==None:
			totalTime=timeDelta
		else:
			totalTime=totalTime+timeDelta
		c = [ columns[-1] ]
		while( len(c) < (numberOfEvents*2)+1):
			c.append("")
		c.append( "%.2f h" % convertDTtoHours( totalTime ))
		cvsWriter.writerow(c)		
		
	#finally close last track
	closeCvs(file)

#search the corresponding items for the tracks 
for timeSheet in config.timeSheets:
	# get all item table name
	try:
		cur.execute("SELECT * FROM items WHERE itemname='%s'" % timeSheet.item)
	except:
		print( "Table problem with table '%s`" % timeSheet.item)
		quit()

	#get all entries from track
	try:
		for item in cur.fetchall(): #usually only one entry
			#select all data except from today
			cur.execute("SELECT * FROM item%04d WHERE cast(time as date) < DATE_SUB(NOW(), INTERVAL 1 DAY)" % item[0])
			break
	except:
		print( "Table problem with table item%04d" % item[0])
		quit()
	
	#create colums
	columns = [timeSheet.date]
	for event in range(0,timeSheet.events):
		columns.append(timeSheet.on)
		columns.append(timeSheet.off)
	columns.append(timeSheet.total)
	
	createTimeSheet( timeSheet.path, timeSheet.name, str(timeSheet.delimiter), columns, cur )

db.close()


