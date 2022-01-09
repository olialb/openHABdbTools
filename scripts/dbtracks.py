#!/usr/bin/python
# ################################################################
# 
# OpenHAB dbTools python script to create daily tracks of 
# residents.
# Created by Oliver Albold 2019
#
# ################################################################

import MySQLdb
import sys
import os
from geopy import distance
import dbtoolsconfig as config

gpxHeader = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<gpx version="1.1" creator="OpenHAB user tracking (Author: Oliver Albold)"
 xmlns="http://www.topografix.com/GPX/1/1"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
 xmlns:gpx_style="http://www.topografix.com/GPX/gpx_style/0/2"
 xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
 xmlns:gpxtrkx="http://www.garmin.com/xmlschemas/TrackStatsExtension/v1"
 xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v2"
 xmlns:locus="http://www.locusmap.eu">
	<metadata>
		<desc>File with tracks created by openHAB user tracking (Author: Oliver Albold)</desc>
	</metadata>
<trk>
<name>openHAB track of %s, %04d-%02d-%02d</name>
	<extensions>
		<gpx_style:line>
			<gpx_style:color>#960000FF</gpx_style:color>
			<gpx_style:width>10.0</gpx_style:width>
		</gpx_style:line>
	</extensions>
<trkseg>
"""

gpxFooter= """</trkseg>
</trk>
</gpx>
"""

gpxPoint= """<trkpt lat="%s" lon="%s">
	<time>%s</time>
</trkpt>
"""

def closeTrack( file ):
	if file != None:
		#write footer
		file.write( gpxFooter )
		file.close()

def createTracks ( root, name ,cur ):
	year = 0
	month = 0
	day = 0
	file = None

	for entry in cur.fetchall():
		date = entry[0]
		location = entry[1]
		
		#check if we have a new day in the array of locations
		if date.year != year or date.month != month:
			year = date.year
			month = date. month
			day = 0
			oldlocation = None

			#create new directorey if necessary:
			path = os.path.join(root,"%04d/%02d/" % (year, month))
			if(not os.path.isdir(path)):
				try:
					os.makedirs( path )
				except:
					print ("Can not create: %s" % path)
					quit()
					
		#create new file if necessary
		if date.day != day:
			#first close exitiong file
			closeTrack(file)
			file = None
				
			#open new file
			day = date.day
			filename = path+"%04d-%02d-%02d-%s.gpx" % (year, month, day, name)
			#create only a new file if it does not exist already
			if not os.path.isfile( filename):
				try:
					file = open( filename, "w+")
				except:
					print ("Can not create: %s" % filename)
					quit()
				#write header
				file.write( gpxHeader % (name, year, month, day))
		if file != None:
			#write track point
			location = location.split(",")
			loctuple = (location[0], location[1])
			if oldlocation != None:
				d = distance.distance(loctuple, oldlocation)
				#if d > 1:
				#	print (date.strftime("%Y-%m-%dT%H:%M:%SZ"), d)
			oldlocation = loctuple
			file.write( gpxPoint % (location[0], location[1], date.strftime("%Y-%m-%dT%H:%M:%SZ")))
		#continue with next way point
	#finally close last track
	closeTrack(file)


#open tha data base
db = config.openDataBase()
# you must create a Cursor object. It will let you execute all the queries you need
cur = db.cursor()

#search the corresponding items for the tracks 
for track in config.tracks:
	# get all item table name
	try:
		cur.execute("SELECT * FROM items WHERE itemname='%s'" % track.item)
	except:
		print( "Table problem with table '%s`" % track.item)
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
	
	#print len(cur.fetchall())
	createTracks( track.path, track.name, cur )

config.closeDataBase(db)
sys.exit(0)

