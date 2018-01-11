#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2011 Kim Gerdes
# kim AT gerdes. fr
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of the GNU General Public License
# from http://www.gnu.org/.  For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####

import os
from sqlite3 import connect, OperationalError
from optparse import OptionParser

	
def makeDataBase(dbpath):
	db = connect(dbpath)
	cursor = db.cursor()
	
	cursor.execute('''create table IF NOT EXISTS texts
	(textname TEXT UNIQUE, nrtokens INTEGER)''')
	cursor.execute('''create table IF NOT EXISTS users
	(user TEXT UNIQUE, realname TEXT)''')
	cursor.execute('''create table IF NOT EXISTS ausers
	(user VARCHAR(100) UNIQUE, first_name VARCHAR(100), last_name VARCHAR(100), 
	email VARCHAR(255), last_login VARCHAR(100),image_path VARCHAR(450), password VARCHAR(200), 
	admin_level INTEGER, logout_by_admin TINYINT)''')
	
	cursor.execute('''create table IF NOT EXISTS sentences
	(nr INTEGER, sentence TEXT, textid INTEGER)''')
	try:
		cursor.execute('''create VIRTUAL table IF NOT EXISTS sentencesearch USING fts4
		(nr INTEGER, sentence TEXT, textid INTEGER)''')
	except OperationalError: # Compatibility for sqlite without fts4
		cursor.execute('''create table IF NOT EXISTS sentencesearch
		(nr INTEGER, sentence TEXT, textid INTEGER)''')

	#annotype: 0=annoatator, 1=validator
	cursor.execute('''create table IF NOT EXISTS trees
	(sentenceid INTEGER, userid INTEGER, annotype INTEGER, status TEXT, comment TEXT, timestamp FLOAT, primary key (sentenceid, userid, annotype) )''') 
	cursor.execute('''create table IF NOT EXISTS features
	(treeid INTEGER, nr INTEGER, attr TEXT, value TEXT, primary key (treeid,nr,attr) )''')
	
	cursor.execute('''create table IF NOT EXISTS sentencefeatures
	(sentenceid INTEGER, attr TEXT, value TEXT )''')
	
	cursor.execute('''create table IF NOT EXISTS links
	(treeid INTEGER, depid INTEGER, govid INTEGER, function TEXT )''') 
	
	#todos has the following structure: userid INTEGER, textid INTEGER, type TEXT, status TEXT, comment TEXT
	#type means: 0=simple annotator, 1=validator
	#status means: 0:todo, 1: ok, ... fixed in the parameters of the project
	cursor.execute('''create table IF NOT EXISTS todos
	(userid INTEGER, textid INTEGER, type TEXT, status TEXT, comment TEXT, primary key (userid, textid) )''') 
	cursor.execute('''create table IF NOT EXISTS exos
	(textid INTEGER NOT NULL PRIMARY KEY, type INTEGER, exotoknum INTEGER, status TEXT, comment TEXT, FOREIGN KEY (textid) REFERENCES texts(rowid))''')
	cursor.execute('''create table IF NOT EXISTS exousersentence
	(textid INTEGER NOT NULL, userid INTEGER NOT NULL, sentenceid INTEGER NOT NULL, 
	UNIQUE (textid, userid, sentenceid),
	FOREIGN KEY (textid) REFERENCES texts(rowid),
	FOREIGN KEY (userid) REFERENCES users(rowid),
	FOREIGN KEY (sentenceid) REFERENCES sentences(rowid)
	)''')
	db.commit()
	db.close()
	
if __name__ == "__main__":

	usage = "usage: %prog [options] newProjectName\n important: make all folders world readable!"
	parser = OptionParser(usage)
	parser.add_option("-v", "--verbose",default=False,
			help="print status messages to stdout",
			action="store_true", dest="verbose")
			
	(options, args) = parser.parse_args()
	verbose = options.verbose
	if verbose: 
		print "options:",options,args
	if len(args)<1:	
		options.test=True
		print "please indicate a name for the new project"
	else:
		project=args[0]
		
		if os.path.exists ("../projects/"+project):
			print "ok"
			print "creating the database for the project",project
			dbpath="../projects/"+project+"/arborator.db.sqlite"
			makeDataBase(dbpath)
			os.chmod(dbpath,0777)
			
		else:
			print "please create the", project,"folder in the 'projects' folder."
