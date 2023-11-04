#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbTools python script to create a csv time sheet of
# items.
# Created by Oliver Albold 2023
#
# ################################################################

import MySQLdb
import sys
import os
import csv
import datetime

import dbtoolsconfig as config

def closeCvs(file):
	if file != None:
		file.close()
		
def convertDTtoHours( dt ):
	hours = dt.days * 24
	hours = hours + int(dt.seconds / 3600)
	minutes = int((dt.seconds % 3600) / 60)
	return float(hours) + float(minutes)/60

def createSheet ( name , delimiter, items, data ):
	#create colums
	columns = ["Date and Time"] + items
	columnIndex = 0

	#convert the data to a dictonary of date time entries
	dataDict = {} 
	for item in items:
		columnIndex += 1
		itemData = data[item]

		for itemState in itemData:
			#create date and time entry
			dateAndTimeStr = (str(itemState[0].date()) + " " + str(itemState[0].time()))
			if dateAndTimeStr not in dataDict:
				#create new dict entry
				dataDict[dateAndTimeStr] = [ dateAndTimeStr ] + len(items) * ['']

			#set the state for this item:
			dataDict[dateAndTimeStr][columnIndex] = itemState[1]
			#print (dataDict[dateAndTimeStr])
		
	with open(name, 'w') as csvfile:
		cvsWriter = csv.writer( csvfile, delimiter=delimiter )
		cvsWriter.writerow(columns)

		for row in sorted(dataDict):
			cvsWriter.writerow(dataDict[row])

	print("File '%s' sucessfully created" % name)

#open tha data base
db = config.openDataBase()
# you must create a Cursor object. It will let you execute all the queries you need
cur = db.cursor()

if len(sys.argv) < 3:
	print("Usage dbitemhistory filename.csv itemname1 itemname2 .... itemnameN")
	quit()

itemsList = sys.argv[2:]
sheetName = sys.argv[1]
itemsData = {}

#search the corresponding items for the tracks 
for item in itemsList:
	# get all item table name
	try:
		cur.execute("SELECT * FROM items WHERE itemname='%s'" % item)
	except:
		print( "Fatal problem with item table!" )
		quit()

	itemTables = cur.fetchall()

	if len(itemTables) == 0:
		print( "Table for item '%s' not found" % item)
		quit()

	#get all entries from track
	try:
		for itemTable in itemTables: #usually only one entry
			#select all data
			cur.execute("SELECT * FROM item%04d" % itemTable[0])
			break
	except:
		print( "Table problem with table item%04d" % itemTable[0])
		quit()

	#fetch all entries for this item
	itemsData[item] = cur.fetchall()

createSheet( sheetName, str(config.delimiter), itemsList, itemsData )

config.closeDataBase(db)
sys.exit(0)
