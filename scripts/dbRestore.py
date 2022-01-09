#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbRestore python script to restore all db data for existing items
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
		print ("No data %s" % path)
		quit()

	jdata = None
	filename = normalizeFilename(name + "_" + type + ".json")
	try:
		file = open( os.path.join(path,filename), "r+")
		#print ("Found: " + os.path.join(path,filename))
		jdata = json.load(file)
		file.close()
	except:
		...
		#print ("No data for %s of type %s" % (name,type))

	return jdata

def jsonSerial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

#		
#start processing
#

#unzip data
if len(sys.argv) != 2:
	print("Usage: dbRestore zipfilename")
	sys.exit()	

shutil.unpack_archive(config.rootPath + sys.argv[1], config.rootPath + dataDir)

openHabItemsREST = getOpenHabItems() #read all items over REST API in json format
db = config.openDataBase() #open configured data base
openHabItemsDB = getDataBaseItems(db) # read all data base items

#go over all REST items and put them in CSV file
index = 0
#printProgress('[')
for elem in openHabItemsREST:
	#ignore groups
	if elem['type'] == 'Group': continue

	#Count all tables which are updated
	tableCount = 0
	entryCountTotal = 0

	#open JSON file
	jdata = openJSON(config.rootPath + dataDir, elem['name'], elem['type'])
	if jdata != None and elem['name'] in openHabItemsDB:
		tableidx = openHabItemsDB[elem['name']]
		print("Data found '%s' for table item%04d. Add data..." % (elem['name'],tableidx))
		tableCount = tableCount + 1
		
		#Add data to table
		cur = db.cursor()
		entryCount = 0
		failCount = 0
		for entry in jdata:
			table = "item%04d" % tableidx
			sql = "INSERT INTO " + table +" VALUES(%s, %s)"
			if elem['type'] == "DateTime":
				val = (datetime.fromisoformat(entry[0]), datetime.fromisoformat(entry[1]))
			else:
				val = (datetime.fromisoformat(entry[0]), entry[1])	
			try:
				cur.execute(sql,val)
				entryCount = entryCount + 1
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				failCount = failCount + 1
#				print (e)
		db.commit()
		print ("%d entries added to table item%04d. %d failed." % (entryCount, tableidx, failCount))

#zip the directory
#print(config.rootPath + dataDir + "_" + datetime.now().isoformat())
shutil.rmtree(config.rootPath + dataDir)

config.closeDataBase(db)
sys.exit()
