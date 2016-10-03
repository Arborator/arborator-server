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


#import traceback,
import cgi,cgitb, codecs,time, subprocess, sys, os


cgitb.enable()

form = cgi.FieldStorage()

project = form.getvalue('project','').decode("utf-8") # graph / transition
parserType = form.getvalue('parserType','').decode("utf-8") # graph / transition
whoseTrees = form.getvalue('whoseTrees','').decode("utf-8") # all / validators only
evaluationPercent = form.getvalue('evaluationPercent','').decode("utf-8") # from 1 to 100
additionnalLexicon = form.getvalue('additionnalLexicon','').decode("utf-8") # infile / None
resultAnnotator = form.getvalue('resultAnnotator','').decode("utf-8") # parser / mate / enterName

#parserType= u"graph"
#whoseTrees = u"all"
#evaluationPercent = u"10"
#additionnalLexicon = u"None"
#resultAnnotator = u"parser"

command = u'python mate.py {project} {parserType} {whoseTrees} {evaluationPercent} {additionnalLexicon} {resultAnnotator} '.format(project=project, parserType=u"--parserType "+parserType if parserType else "", whoseTrees=u"--whoseTrees "+whoseTrees if whoseTrees else "", evaluationPercent=u"--evaluationPercent "+evaluationPercent if evaluationPercent else "", additionnalLexicon=u"--additionnalLexicon "+additionnalLexicon if additionnalLexicon else "", resultAnnotator=u"--resultAnnotator "+resultAnnotator if resultAnnotator else "")
print 'Content-type: text/plain\n\n',
print command
#-testRun
p = subprocess.Popen(command, shell=True)

#de=newmate.doIt(project=u"OrfeoGold2016", lang="graph", evaluationPercent=10, additionnalLexicon=None, resultAnnotator="mate")
#output_trees=de.run_depedit(infile)

#print output_trees.encode("utf-8")

