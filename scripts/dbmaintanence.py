#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbTools python script to deleta all entries from 
# data base which are older than a configured number of days.
#
# Created by Oliver Albold 2019
#
# ################################################################

import MySQLdb
import sys
import dbtoolsconfig as config

#define the month interval. Everything whats older will be deleted
keep =  config.dbDays #number of days to keep
if(keep < 0):
	print("Please configure days=X in [maintenance] section in dbTools.ini!")
	quit()

interval = "where cast(time as date) < DATE_SUB(NOW(), INTERVAL %d DAY)" % keep

#open tha data base
db = config.openDataBase()
# you must create a Cursor object. It will let you execute all the queries you need
cur = db.cursor()

# get all item tables
cur.execute("SELECT * FROM items")

#Count all deleted entries
totalDeleteCount = 0
problem_entries = []

#evaluate command line arguments
config.checkargs()

# go over all entries of 'items' table
for item in cur.fetchall():
	#select all old entries
	try:
		cur.execute("SELECT * FROM item%04d %s" % (item[0],interval))

		#go over the tables with old entries
		mylist = cur.fetchall()
		n = len(mylist)
		if n > 0: #are there old entries?
			if not config.silent:
				print ("[%s,item%04d] delete %d old entries" % (item[1], item[0], n))
			totalDeleteCount = totalDeleteCount + n;
			#finally delete old entries and otimize the table
			cur.execute("DELETE FROM item%04d %s" % (item[0],interval))
			cur.execute("OPTIMIZE TABLE item%04d" % item[0])
	except Exception as info:
		print( "Error %s: item%04d %s: %s" % (item[1],item[0],interval,info))
		problem_entries.append( item[1] )

#print total
print ("%d entries deleted witch are older than %d days." % (totalDeleteCount,keep))

print ("Problem entries: %d" % len(problem_entries))
if not config.silent:
	for itemName in problem_entries:
		print("itemname='%s';"%(itemName))

#cleanup
config.closeDataBase(db)
sys.exit(0)
