#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbStatistics python script to deleta all entries from 
# data base which are older than a configured number of days.
#
# Created by Oliver Albold 2019
#
# ################################################################

import MySQLdb
import sys
import requests
import json
import os
import csv
import dbtoolsconfig as config

jsonEntries = ["name", "label", "type", "state", "editable", "groupNames", "tags"]
dbEntries = ['table key', 'number of entries', 'first entry', 'last entry']

#get all items over REST API in json format
def getOpenHabItems():
	result = requests.get("http://localhost:8080/rest/items?recursive=false", timeout=2)
	if (result.status_code != 200):
		print("Error getting item list over Rest API: %d" % result.status_code)
		sys.exit()
	#return them sort them by name
	return sorted(result.json(), key=lambda k: k['name']) 

#get all items from the data base
def getDataBaseItems(db):
	# you must create a Cursor object. It will let you execute all the queries you need
	cur = db.cursor()

	# get all item tables
	cur.execute("SELECT * FROM items")
	myTableDict = {}
	for entry in cur.fetchall():
		myTableDict[entry[1]] = entry[0]
	return myTableDict

#get all entries of item table
def getItemTableEntries( tableIdx ):
	# you must create a Cursor object. It will let you execute all the queries you need
	cur = db.cursor()
	try:
		cur.execute("SELECT * FROM item%04d" % tableIdx)
	except:
		print( "Table problem with table item%04d" % tableIdx)
		return []
	return cur.fetchall()
	

	cur.execute("SELECT * FROM item%04d WHERE cast(time as date) < DATE_SUB(NOW(), INTERVAL 1 DAY)" % item[0])

#def open CSV file
def openCSV( path, name, columns ):
	if(not os.path.isdir(path)):
		try:
			os.makedirs( path )
		except:
			print ("Can not create: %s" % path)
			quit()
	try:
		file = open( os.path.join(path,name), "w+")
	except:
		print ("Can not create: %s" % filename)
		quit()
	cvsWriter = csv.writer( file, delimiter=str(config.delimiter) )
	cvsWriter.writerow(columns)
	return file, cvsWriter

def printProgress(str):
	sys.stdout.write(str)
	sys.stdout.flush()

def closeCVS(file):
	if file != None:
		file.close()

#		
#start processing
#
openHabItemsREST = getOpenHabItems() #read all items over REST API in json format
db = config.openDataBase() #open configured data base
openHabItemsDB = getDataBaseItems(db) # read all data base items

#create CSV file
file, csvWriter = openCSV(config.rootPath,'openHABdbStat.csv', ['No.']+jsonEntries+dbEntries)

#go over all REST items and put them in CSV file
index = 0
printProgress('[')
for elem in openHabItemsREST:
	#ignore groups
	if elem['type'] == 'Group': continue
	printProgress('.')
	index=index+1
	c =[str(index)]
	#go over the columns of the REST data
	for column in jsonEntries:
		try:
			value = elem[column]
		except:
			value = ""
		if isinstance(value, bytearray):
			#double check that unicode string does not contain characters which can not be used in csv files
			value=value.encode('utf-8',errors='replace')
		else:
			if isinstance(value,list):
				#for list values add a string with the listed values
				s = ""
				f = "%s"
				for subValue in value:
					s = s + f % str(subValue)
					f = ", %s"
				value = str(s)
			else:
				#all ather types change to string
				value = str(value)
		#add to row list
		c.append(value)
	#process data base entries for this item
	try:
		#get table index
		tableidx = openHabItemsDB[elem['name']]
		c.append(str(tableidx))
		#delete this item from data base list
		del openHabItemsDB[elem['name']]
		#read table data
		entries = getItemTableEntries(tableidx)
		c.append(str(len(entries)))
		printProgress("[%d]" % len(entries))
		d = (min(entries, key = lambda t: t[0]))[0]
		c.append("%04d-%02d-%02d %02d:%02d" % (d.year,d.month,d.day,d.hour,d.minute))
		d = (max(entries, key = lambda t: t[0]))[0]
		c.append("%04d-%02d-%02d %02d:%02d" % (d.year,d.month,d.day,d.hour,d.minute))
	except:
		c.append('not found')
	#finally write row to CVS
	csvWriter.writerow(c)

printProgress('.#not in configuration#')
#now go over all remaining entries in data base
for itemName,tableidx in sorted(openHabItemsDB.items(), key=lambda item: item[0]):
	index=index+1
	printProgress('.')
	c =[str(index), ]
	for column in jsonEntries:
		if column == 'name':
			c.append( str(itemName) )
		else:
			c.append("-.-")
	c.append(str(tableidx))
	#read table data
	entries = getItemTableEntries(tableidx)
	c.append(str(len(entries)))
	printProgress("[%d]" % len(entries))
	if len(entries) > 0:
		d = (min(entries, key = lambda t: t[0]))[0]
		c.append("%04d-%02d-%02d %02d:%02d" % (d.year,d.month,d.day,d.hour,d.minute))
		d = (max(entries, key = lambda t: t[0]))[0]
		c.append("%04d-%02d-%02d %02d:%02d" % (d.year,d.month,d.day,d.hour,d.minute))
	else:
		c.append("-.-")
		c.append("-.-")
		
	csvWriter.writerow(c)
printProgress(']\n')

#print number of unused tables
print("Number of unused tables in data base (tables without active item in openHAB) is %d" % len(openHabItemsDB))
	
#clean up
closeCVS(file)	
config.closeDataBase(db)
sys.exit()
