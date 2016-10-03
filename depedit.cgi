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

from StringIO import StringIO
import depedit

import cgi,cgitb, sys



cgitb.enable()

form = cgi.FieldStorage()

conllin = form.getvalue('conllin','').decode("utf-8")
grammar = form.getvalue('grammar','').decode("utf-8")

config_file = StringIO(grammar)
infile = StringIO(conllin)

print 'Content-type: text/plain\n\n',

class writer(object):
	log = []
	def write(self, data):
		self.log.append(data)
sys.stderr
logger = writer()
sys.stderr = logger

try:
	de=depedit.DepEdit(config_file)
	output_trees=de.run_depedit(infile)
	print output_trees.encode("utf-8")
	
except:
	print u"uuuuuuuuu".join(logger.log)

