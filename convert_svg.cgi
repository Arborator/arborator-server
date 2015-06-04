#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
convert_svg.py  0.1

See <http://svgkit.sourceforge.net/> for documentation, downloads, license, etc.

(c) 2006-2007 Jason Gallicchio.  All rights Reserved.
"""

# Outline of code:
# Read the SVG
# Read the type to convert to
# Read the options (width, height, dpi, quality)  (TODO)
# Generate a hash for caching and check to see if we've already done this (TODO)
# Convert with scripts off
# Check the output file size.
# Send the result back
# needs: apt-get install librsvg2-bin !!!!!!!!!!!! new in 2014!!!


import cgi
import cgitb; cgitb.enable() # Show errors to browser.
import sys
import os, urlparse
from subprocess import *
import time
import re
import hashlib

import config
#,xmlsqlite

#from config import *



form = cgi.FieldStorage()
time.sleep(0.1) # Throttle requests
project = form.getvalue("project",None).decode("utf-8")

if project != "quickie":
	

	projectconfig=None
	try:
		projectconfig = config.configProject(project) # read in the settings of the current project
	except:
		pass
	if not projectconfig:
		print "Content-Type: text/html\n" # blank line: end of headers
		print "something went seriously wrong: can't read the configuration of the project",project.encode("utf-8")
		#print "Content-Type: text/html\n" # blank line: end of headers
		#print '<script type="text/javascript">window.location.href=".";</script>'
		sys.exit("something's wrong")

	
#java = '/opt/jdk1.7.0/bin/java'
java = "java"
#batik = '/var/www/cgi-bin/arborator/batik-1.7/batik-rasterizer.jar'
batik = 'export/batik-1.7/batik-rasterizer.jar'

#svg2office = '/var/www/cgi-bin/arborator/svg2office-1.2.2.jar'
svg2office = 'export/svg2office-1.2.2.jar'

#cache='/var/www/html/cache/'
cache= 'export/cache/'

#cacheShow='http://localhost/cache/'
#cacheShow= projectconfig["configuration"]["url"]+'export/cache/'

#url = os.environ["QUERY_STRING"] 
#parsed = urlparse.urlparse(url) 

cacheShow= 'export/cache/'

sys.stderr = sys.stdout
cgi.maxlen = 1024*1024



mediatypes={
  'pdf':'application/pdf',
  'ps':'application/pdf',  # Gets converted after
  'odg':'application/odg',
  'jpg':'image/jpeg',
  'png':'image/png',
  'tif': 'image/tiff',
  'svg':'image/svg+xml'
}

#debug = True
debug = False
redirect = True
#redirect = False

if debug:   print 'Content-type: text/plain\n\n'


if debug:
    print 'Debug mode of convert_svg.py\n'
    print 'form.keys(): ' + form.keys().__str__()+'\n'
    for key in form.keys():
        print 'form['+key+'] = '+form[key].value+'\n'

source = form.getvalue('source',None)
if source == None: source = open("images/arborator.svg","r").read()

#source = open("arborator.svg","r").read()

type = form.getvalue('type',"pdf")
#type = form['type'].value
mime = mediatypes[type]

md5hex = hashlib.md5(source).hexdigest()
svgname = cache+md5hex+'.svg'
outname = cache+md5hex+'.'+type
showname = cacheShow+md5hex+'.'+type

def execute_cmd(cmd):
    #(child_stdin, child_stdout, child_stderr) = os.popen3(cmd)
    
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    
	#(child_stdin,bufsize=bufsize,
	#child_stdout,
	#child_stderr) = (p.stdin, p.stdout, p.stderr)
    
    #print 1/0
    str_stdout = p.stdout.read() # Read until the process quits.
    str_stderr = p.stderr.read() # Read until the process quits.
    if debug:
        print cmd+'\n'
        print 'stdout:'+str_stdout+'\n'
        print 'stderr:'+str_stderr+'\n'
        
#execute_cmd('chown jason users files/*.*')  # Redhat disables chown
        
# If the result doesn't already exist in cached form, create it True or 
if not os.path.isfile(outname) or source!=open(svgname, 'r' ).read():
	
    # work around for the bug in rsvg-convert (failure to render non default fonts if they are not mentioned in "font-family")!
    pattern=re.compile(r"font:([^;]* ([^;]*));",re.I+re.U)
    source=pattern.sub(ur"font:\1; font-family:\2;",source.decode("utf-8")).encode("utf-8")
    
    
    svgfile = open(svgname, 'w')
    svgfile.write(source)
    svgfile.close()
    #if type == 'xml':
	#PrettyPrint(xmlsqlite.tree2xml(1))
    if type == 'svg':
        outname = svgname
    elif type == "odg":
	cmd = java+' -jar ' + svg2office +" "+svgname #+" "+ outname
	if debug: print cmd
	execute_cmd(cmd)
	#print "<br>",cmd
    elif type in ["png","pdf","ps"]:
	 cmd = "rsvg-convert --background-color white -z 3 -f {type} -o {outname} {svgname}".format(type=type,svgname=svgname,outname=outname)
	 execute_cmd(cmd)
    else:
        cmd = java+' -jar ' + batik + ' -d '+cache+' -m '+mime+' '+svgname # -dpi <resolution>  -q <quality>
        if debug: print cmd
        
        execute_cmd(cmd)
        
        if type=='ps':
            inname = cache+md5hex+'.pdf'
            cmd = 'pdftops '+inname+' '+outname
	    
            execute_cmd(cmd)
#time.sleep(1)

if redirect:
	#print 'Content-type: text/plain\n\n'
	print 'Location: '+showname+'\r\n\r\n'
else:
    outfile = open( outname, 'rb')
    image = outfile.read()
    if not debug:
        sys.stdout.write('Content-type: '+mime+'\r\n\r\n')
        sys.stdout.write(image)
    outfile.close()
