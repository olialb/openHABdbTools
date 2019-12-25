#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbTools python script to calculate db size
# Created by Oliver Albold 2019
#
# ################################################################

import MySQLdb
import sys
import dbtoolsconfig as config

db = MySQLdb.connect (host = config.dbHost, 	# your host, usually localhost
                      user = config.dbUser,		# your username
                      passwd = config.dbPassWord,	# your password
                      db = config.dbTable)		# name of the data base
							  
# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# get size of openhab
cur.execute('SELECT table_schema "Database Name" , SUM( data_length + index_length)/1024/1024 "Database Size (MB)"  FROM information_schema.TABLES where table_schema = "openhab";')

# go over all entries of 'items' table
for item in cur.fetchall():
	#select all old entries
	if item[0] == config.dbTable: 
		print("OpenHAB database size %.2fMB" % (item[1]))
		size = item[1]

db.close()

sys.exit(size)

