#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2016 Kim Gerdes
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

#import depedit

#import traceback,
import cgi,cgitb, codecs,time, subprocess, sys, os



cgitb.enable()
form = cgi.FieldStorage()

parser_type = form.getvalue('parser_type','').decode("utf-8")
whosetrees = form.getvalue('whosetrees','').decode("utf-8")
evaluateionpercent = form.getvalue('evaluateionpercent','').decode("utf-8")
additionallexicon = form.getvalue('additionallexicon','').decode("utf-8")
resultannotator = form.getvalue('resultannotator','').decode("utf-8")


print 'Content-type: text/plain\n\n',
info = u"Here are my parameters: {parser_type}, {whosetrees}, {evaluateionpercent}, {additionallexicon}, {resultannotator}".format(parser_type=parser_type,whosetrees=whosetrees,evaluateionpercent=evaluateionpercent,additionallexicon=additionallexicon,resultannotator=resultannotator,)
#print u"Mate started\n"+info
#with codecs.open("mate/parse.log","w","utf-8") as log:
	#log.write(u"I've started.\n"+info)
#time.sleep(5) 
#with codecs.open("mate/parse.log","w","utf-8") as log:
	#log.write(u"now i'm here.\n"+info)
#os.chmod("mate/parse.log", 0666)
#p = subprocess.Popen([sys.executable, 'python newmate.py'], shell=True, 
                     #stdout=subprocess.PIPE, 
                     #stderr=subprocess.STDOUT)
p = subprocess.Popen('python newmate.py', shell=True)
