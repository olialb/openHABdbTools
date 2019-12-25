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
interval = "where cast(time as date) < DATE_SUB(NOW(), INTERVAL %d DAY)" % keep

db = MySQLdb.connect (host = config.dbHost, 	# your host, usually localhost
                      user = config.dbUser,		# your username
                      passwd = config.dbPassWord,	# your password
                      db = config.dbTable)		# name of the data base
							  
# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# get all item tables
cur.execute("SELECT * FROM items")

#Count all deleted entries
totalDeleteCount = 0
problem_entries = []

# go over all entries of 'items' table
for item in cur.fetchall():
	#select all old entries
	try:
		cur.execute("SELECT * FROM item%04d %s" % (item[0],interval))

		#go over the tables with old entries
		mylist = cur.fetchall()
		n = len(mylist)
		if n > 0: #are there old entries?
			print ("[%s,item%04d] delete %d old entries" % (item[1], item[0], n))
			totalDeleteCount = totalDeleteCount + n;
			#finally delete old entries and otimize the table
			cur.execute("DELETE FROM item%04d %s" % (item[0],interval))
			cur.execute("OPTIMIZE TABLE item%04d" % item[0])
	except Exception as info:
		print( "Error %s: item%04d %s: %s" % (item[1],item[0],interval,info))
		problem_entries.append( item[1] )

#print total
print ("In total [%d] %d day old entries deleted." % (totalDeleteCount,keep))

print ("Problem entries:")
for itemName in problem_entries:
	print("itemname='%s';"%(itemName))

db.close()

sys.exit(totalDeleteCount)

