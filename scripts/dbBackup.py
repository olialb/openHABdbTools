#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbBackup python script to backup all db data for existing items
#
# Created by Oliver Albold 2022
#
# ################################################################

import MySQLdb
from datetime import date, datetime
import sys
import requests
import json
import os
import shutil
import dbtoolsconfig as config

dataDir = "dbBackup"

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

def normalizeFilename(fn):
    """removes illegal filenmame characters from string"""
    validchars = "-_.() "
    out = ""
    for c in fn:
      if str.isalpha(c) or str.isdigit(c) or (c in validchars):
        out += c
      else:
        out += "_"
    return out  

#def open JSON file
def openJSON( path, name, type ):
	if(not os.path.isdir(path)):
		try:
			os.makedirs( path )
		except:
			print ("Can not create: %s" % path)
			quit()
	try:
		filename = normalizeFilename(name + "_" + type + ".json")
		file = open( os.path.join(path,filename), "w+")
		print ("Create: " + os.path.join(path,filename))
	except:
		print ("Can not create: %s" % filename)
		quit()
	return file

def jsonSerial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

#		
#start processing
#
openHabItemsREST = getOpenHabItems() #read all items over REST API in json format
db = config.openDataBase() #open configured data base
openHabItemsDB = getDataBaseItems(db) # read all data base items

#go over all REST items and put them in CSV file
index = 0
#printProgress('[')
for elem in openHabItemsREST:
	#ignore groups
	if elem['type'] == 'Group': continue

	#process data base entries for this item
	entries = []
	try:
		#get table index
		tableidx = openHabItemsDB[elem['name']]
		#delete this item from data base list
		del openHabItemsDB[elem['name']]
		#read table data
		entries = getItemTableEntries(tableidx)
	except:
		print ('"%s" not found' % elem['name'])

	if len(entries) > 0:
		#write data to json file
		outfile = openJSON(config.rootPath + dataDir, elem['name'], elem['type'])
		outfile.write( json.dumps(entries, default=jsonSerial ) )
		outfile.close()

#zip the directory
#print(config.rootPath + dataDir + "_" + datetime.now().isoformat())
shutil.make_archive(config.rootPath + dataDir + "_" + datetime.now().strftime("%Y%m%d-%H%M%S"), 'zip', config.rootPath + dataDir)
shutil.rmtree(config.rootPath + dataDir)

config.closeDataBase(db)
sys.exit()
