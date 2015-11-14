#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2015 Kim Gerdes
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


"""
called from configedit.cgi by javascript

checks whether the proposed modification of the configuration is syntactically acceptable

"""

import cgi
import sys,cgi,cgitb, codecs, config, os

sys.path.append('modules')
from logintools import isloggedin
#from os       import environ

#import traceback,



cgitb.enable()

form = cgi.FieldStorage()

ct = form.getvalue('config',None).decode("utf-8")
cats = form.getvalue('cats',None).decode("utf-8")
funcs = form.getvalue('funcs',None).decode("utf-8")
projectName = form.getvalue('project',None).decode("utf-8")

test = isloggedin("users/")
if not test:sys.exit()
admin = test[0]["admin"]
if not admin:sys.exit()

#print "Content-Type: text/html\n" # blank line: end of headers

def confToDisk(tmp):
	filename=unicode(os.path.join(unicode(os.getcwd()),u"projects",projectName,u"project.cfg"+tmp )).encode("utf-8")
	f=codecs.open(filename,"w","utf-8")
	f.write(ct)
	f.close()
	c=config.checkConfigProject(projectName, filename=u"project.cfg"+tmp,readin=False)	
	
	filename=os.path.join(os.getcwd(),"projects",projectName.encode("utf-8"),(c["configuration"]["categoriesfilename"]+tmp).encode("utf-8") )  
	f=codecs.open(filename,"w","utf-8")
	f.write(cats)
	f.close()

	filename=os.path.join(os.getcwd(),"projects",projectName.encode("utf-8"),(c["configuration"]["functionsfilename"]+tmp).encode("utf-8") )  
	f=codecs.open(filename,"w","utf-8")
	f.write(funcs)
	f.close()

	return config.checkConfigProject(projectName, filename=u"project.cfg"+tmp,readin=True)

def eraseConfig(tmp,c):
	os.remove(unicode(os.path.join(unicode(os.getcwd()),u"projects",projectName,u"project.cfg"+tmp )).encode("utf-8"))
	os.remove(os.path.join(os.getcwd(),"projects",projectName.encode("utf-8"),(c["configuration"]["categoriesfilename"]+tmp).encode("utf-8") )  )
	os.remove(os.path.join(os.getcwd(),"projects",projectName.encode("utf-8"),(c["configuration"]["functionsfilename"]+tmp).encode("utf-8") )  )
	
# first phase: testing with tmp files, without erasing the old files
c=confToDisk(".tmp")
#erase the tmp config files:
eraseConfig(".tmp",c)
# if here no error all is well. we can save normally
c=confToDisk("")
#and 



print "Content-Type: text/json\r\n\r\n"
print '{"answer":"Ok. Saved."}'