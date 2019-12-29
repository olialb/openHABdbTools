# openHAB Data Base Tools

## Purpose of this little project
This data base tools written in Python can be used  with [openHAB2](https://www.openhab.org) data bases.
The scritps support:

* **Data Base Maintenace**:
  * Deleteing of all entries from data base which are older than a configurable number of days
  * Calculating the data base size
  * Create data bases statistic sheet with all you items and how much data they have stored in the [openHAB2](https://www.openhab.org) data base

* **Creating Timesheets** of switch items. Together with GPS tracking this can be used to show entring and leaving of configured GPS areas but it can also for other use cases: (How long my Kitchen Light switched on every day?). 
  * Creating monthly CSV files from data base entries for [openHAB2](https://www.openhab.org) [switch items](https://www.openhab.org/docs/configuration/items.html)

* **GPS Tracking** of openHAB users
  * Creating a daily GPS track of the configured users of the oppenHAB instance ([gpx format](https://de.wikipedia.org/wiki/GPS_Exchange_Format))


## What you need to use this project
The following features must be supported by your [openHAB2](https://www.openhab.org) instance that the scripts are working.

* [openHAB2](https://www.openhab.org) installation (tested with 2.4 or newer)
* Instance must be connected to [myopenhab](https://myopenhab.org/) with [openHAB cloud connector](https://www.openhab.org/addons/integrations/openhabcloud/)
* Running [persistance](https://www.openhab.org/docs/configuration/persistence.html) with SQL data base (tested with [mariadb](https://mariadb.org/) over [jdbc data persistance](https://www.openhab.org/addons/persistence/jdbc/))
* Python installation on [openHAB2](https://www.openhab.org) server with the following additonal python packages
  * mysqldb (Install with `sudo apt-get install python-mysqldb` please)
* If you want to use the gps tracking scripts you need the [openHAB gps tracking addon](https://www.openhab.org/addons/bindings/gpstracker/) and for example [Owntracks mobile app](https://owntracks.org/) to send your location to your [openHAB2](https://www.openhab.org) instance.

## Installation
You must do the following steps to install this project on your [openHAB2](https://www.openhab.org) system.

### Copy files to your system
Download zip from this repository and copy all files to your openHAB config folder located at `/etc/openhab2`. Than:
* Make sure that the files are readable for your openHAB user
* Make sure that the python scripts in `/etc/openhab2/scripts` are executable

### Adapt GPS thinks and itmes to your needs
* If you want to use GPS tracks:
  * Adapt your GPS locations and naming to your needs in file `/etc/openhab2/things/gps.things.example` and rename it to `/etc/openhab2/things/gps.things`
  * Adapt the naming to your needs in files `/etc/openhab2/items/gps.items`
  * Adapt the naming and cron job timing to your needs in files `/etc/openhab2/rules/dbtools.rules.example` and rename it to `/etc/openhab2/rules/dbtools.rules`
  * Adapt the naming to your needs in files `/etc/openhab2/stitemaps/gps.sitemap`
  * Adapt your [persistance](https://www.openhab.org/docs/configuration/persistence.html) configuration, that item *locationOliverString* (example) is stored in your data base on every change!"
* If you **don't** want to use GPS Tracking just do:
  * delete or rename `/etc/openhab2/items/gps.items`
  * disable (comment) `[dailyTracks1]` section in `/etc/openhab2/scripts/dbtools.ini` (see also 

### Adapt configuration to your needs:
In `/etc/openhab2/scripts/dbtools.ini` you find the configuration of the python scripts. First you need to configure your data base. Adapt *host* if you do not have a local installation and adapt *user*, *password* and *table* which us used by your openHAB instance:

```ini
[dbconfig]
#host address of the db server:
host=localhost      	

#openHAB table:
table=openhab   

#openHAB data base user:
user=openhab	

#openHAB data base password
password=openhab	
```
Than you need to configure where the created file shall be stored and which delimiter you want to use for Excel CSV files.

```ini
[root]
#root path for all created files
path=/etc/openhab2/data/
#uncomment this when you have a german Excel Version. default is ','
delimiter=;
```
  ---
**Note:** 
Excel versions for different countries load CSV files different. if you use a English Excel version the default delimiter ',' works fine. For German Excel versions you use better ';'. this can be set with the *delimiter=* value.

```ini
#uncomment this when you have a german Excel Version
#delimiter=;
```
---

#### Data Base Maintenance feature
In the *[maintenance]* section you can update the value how much history your data base should keep. The value of *days=90* means that the dbmaintenance will delete every 1st day of the month all entries in the openHAB table which are older than *90* days.
```ini
[maintenance]
#number of days to keep in data base
days=90
```

#### Statistic sheet feature
With the script *dbStatistics.py* you can create a CSV table which contains the data of all your items and their data base index, how much entries they have in the data bases and the date and time of the oldest and newest entry in your DB. You can run this script from command line. All the configuration is read from *dbtools.ini*. The created file is called *openHABdbStat.csv* and can be found in the configured root path (as standard is `/etc/openhab2/data/`). 
The script does the following:

* Request all items over the REST API from the localhost openHAB installation
* Read all entries from the openHAB data base
* Add all active items seen on REST API to the table and check how many data is in the data base for each item
* Finally add also the items from the database to the table which are not active in openHAB any more (old deleted or renamed items)

#### GPS Track creating feature
You can create up to 9 different gps tracks of different users every day. This files are stored in [gpx format](https://de.wikipedia.org/wiki/GPS_Exchange_Format) and configured over the *[dailyTrack**X**]* sections where **X** can be a number from 1-9.

```ini
[dailyTrack1]
#path where the tracks are stored
path=Tracks/
#item to create daily track (must be of type string)
item=locationOliverString
#name for this tracks. Used only in GPX filenames.
name=Oliver	
```

This creates for every day a GPX file with the current date. Creation starts by default at 6am but can be changed in cron job configuration of rule *dbtools every day job* in file `/etc/openhab2/rules/dbtools.rules`. Tis config creates for example files like: `2019-12-24-Oliver.gpx` in directory `/etc/openhab2/data/Tracks/2019/12`

---
**Note:** OpenHAB does not store GPS locations (item type *Location*) in the data base. You need to convert them to string and store this string over your persistance. This is done with the rule `store location` in file `/etc/openhab2/rules/dbtools.rules`. This rule is triggered by any location change. If you want to adapt that accuracy of the way points in your tracks. Please adapt *AccuracyTheshhold* value (in meters). Only locations with an accuracy lower than this value are stored in the data base.

```javascript
val Number AccuracyTheshhold = 100
```
---
#### Monthly CSV files with Switch status
You can create up to 9 different time sheets of different switches every month. This files are stored in [csv format](https://en.wikipedia.org/wiki/Comma-separated_values) and configured over the *[timeSheet**X**]* sections where **X** can be a number from 1-9. This is useful to create your personal time sheet when you enter and leave work.

```ini
[timeSheet1]
#path where the time sheet ist strored
path=TimeSheet/
#item to create time sheet (must be of type switch)
item=OliverAtWork
#name of the timesheet. Used in CSV filenames.
name=AtWork
#column names for switch states (default: "on"/"off")
on=Enter
off=Leave
#column name with Total value (default: "total")
total=Working hours
#column name with date value (default: "date")
date=Date
#number of events in table (default=2)
events=2
```

This example creates for every month CSV files like this: `/etc/openhab2/data/TimeSheet/2019/2019-12-AtWork.csv` for the switch item `OliverAtWork`
The sheet containe a row for every day with a number of ON<->OFF events (here *events=2*) and a total time where the switch was in state ON.
With on=,off=,total= and date= the naming of the colums can be adapted. This example configuration will look like this:

| Date     | Enter | Leave | Enter | Leave | Working hours |
|----------|:-------:|------:|------:|------:|------:|
| 2019-12-01 | 08:50 | 18:43 |       |       | 8.45 h |
| 2019-12-01 | 08:49 | 12:18 | 12:38 | 18:25 | 9.25 h |
| ... |  |  |       |       |... |
| Working hours |  |  |       |       | 17.70h |

## More detailed descriptions can be found here:

* [Data Base Maintenance](http://albold-home.de/openhab2-database-maintenance/)
* [Data Base Statistics Sheet](http://albold-home.de/openhab2-database-overview-sheet-creation/)
* [OpenHAB2 presence tracking with GPS](http://albold-home.de/owner-presence-tracking-with-openhab/)

