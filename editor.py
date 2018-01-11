#!/usr/bin/python
# -*- coding: utf-8 -*-

####
# Copyright (C) 2009-2015 Kim Gerdes
# kim AT gerdes. fr
# http://arborator.ilpga.fr/
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Affero General Public License (the "License")
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE
# See the GNU General Public License (www.gnu.org) for more details.
#
# You can retrieve a copy of of version 3 of the GNU Affero General Public License
# from http://www.gnu.org/licenses/agpl-3.0.html 
# For a copy via US Mail, write to the
#     Free Software Foundation, Inc.
#     59 Temple Place - Suite 330,
#     Boston, MA  02111-1307
#     USA
####

import os, cgitb, cgi, sys
sys.path.append('modules')
from lib import config, database
cgitb.enable()

##############################################
######################### functions

def printhtmlheader(projectEsc,textname,user,textid,userid,sql,todo,validator,addEmptyUser,validvalid,opensentence, projectconfig):
    """
    all strings in parameters are already in utf-8
    
    """
    
    txt = """<script type="text/javascript"> numbersent=1;"""
    txt += "project= '"+projectEsc.encode("utf-8")+"';"
    #txt += "uid= '"+"3"+"';" # TODO!
    txt += "textname= '"+textname.encode("utf-8")+"';"
    txt += "textid= '"+str(textid)+"';"
    txt += "userid= "+str(userid)+";"
    txt += "username= '"+user.username.encode("utf-8")+"';"
    if user.adminLevel or (sql.validatorsCanModifyTokens and validator) or sql.usersCanModifyTokens:
        tokenModifyable=1
    else: tokenModifyable=0
    txt += "tokenModifyable= "+str(tokenModifyable)+";"
    txt += "todo= '"+str(todo)+"';"
    txt += "validator= '"+str(validator)+"';"
    if addEmptyUser: txt += "addEmptyUser= '"+str(addEmptyUser)+"';"
    else: txt += "addEmptyUser= null;"
    txt += "validvalid= '"+str(validvalid)+"';"
    txt += "opensentence= '"+str(opensentence)+"';"
    txt += "editable= "+str(sql.editable)+";"
    txt += "filename = null;" # stuff for use in viewer not editor...
    txt += "nr = null;"
    txt += "filetype = null;"
    txt += "function settings() {"
    txt += projectconfig["look"]["look"]
    txt += """colored={"dependency":null}; //object of elements to be colored. the colors have to be defined in the configuration. just leave the object empty {} if you don't want colors
    attris[shownfeatures[categoryindex]]=attris["cat"]
    colored[shownfeatures[categoryindex]]=null;
    }
    
    </script>
    </head>"""
    return txt
    

def printheadline(project,textname,quantityInfo,user):
    
    if os.path.exists("projects/"+project.encode("utf-8")+"/"+project.encode("utf-8")+".png"):img="<img src='/projects/"+project.encode("utf-8")+"/"+project.encode("utf-8")+".png' align='top' height='18'>"
    else: img=""
    
    if user.adminLevel:openbutton= '<input type="button" id="openall" name="openall" value="open all" style="width:105px;z-index:33;" class="fg-button ui-state-default ui-corner-all " onClick="openAllTrees();">'
    else:openbutton=""
    
    txt =   """<body id="body">
            <div id="navigation" style="width:100%;margin:0px;border:0px;" class="arbortitle  ui-widget-header ui-helper-clearfix">
            <a href='.' style='position: fixed;left:1px;top:1px'><img src="images/arboratorNano.png" border="0"></a>
            <a href="/project/{project}/" style='position: fixed;left:120px;top:5px;color:white;' title="project overview">{img} {project} Annotation Project</a>
                <span style='margin:5 auto;position: relative;top:5px;' id='sentinfo'>{textname} &nbsp; {quantityInfo} </span>
            </div>
            <div id="center" class="center" style="width:100%;">
            <form method="post" action="" name="save" id="save" class="nav" style="top:0px;right:150px;">
                <input type="button" id="sav" name="sav" value="all trees are saved" style="width:155px;z-index:33;" class="fg-button ui-state-default ui-corner-all ui-state-disabled" onClick="saveAllTrees();">
                {openbutton}
            </form>
            <div id="loader" ><img src="images/ajax-loader.gif"/></div>
        """.format(textname=textname.encode("utf-8"), quantityInfo=quantityInfo,project=project.encode("utf-8"),img=img,openbutton=openbutton)
    if os.path.exists("sitemessage.html"):print open("sitemessage.html").read()

    return txt
    #ui-state-disabled


#def printfooter(project,username,thisfile, now):
def printfooter():
    now=lastseens,now=sql.usersLastSeen()   
    print (u"""<div class="arborfoot fg-toolbar ui-widget-header ui-helper-clearfix">logged in as {username}&nbsp;&nbsp;&nbsp;
    <a href="{thisfile}?login=logout&project={project}">logout</a>""".format(username=username,project=projectEsc,thisfile=thisfile)).encode("utf-8")
    if username!="guest": print (u'&nbsp;&nbsp;&nbsp;<a href="{thisfile}?login=editaccount&project={project}">edit the account {username}</a>'.format(username=username,project=projectEsc,thisfile=thisfile)).encode("utf-8")
    if adminLevel > 1: print (u'&nbsp;&nbsp;&nbsp;<a href="{thisfile}?login=admin&project={project}">User Administration</a>'.format(project=projectEsc,thisfile=thisfile)).encode("utf-8")
    
    nowstring=u'<a  title="Ask questions or share your feelings with {r}..." href="mailto:{email}?subject=The%20Arborator%20is%20driving%20me%20crazy!">{r} ({u})</a>'
    now = [nowstring.format(u=u,r=r,email=email) for (u,r,email) in now if u!= username]
    if len(now)==1: print (u'&nbsp;&nbsp;&nbsp;You are not alone! This other user is online now: '+now[0]).encode("utf-8")
    elif len(now)>1: print( u'&nbsp;&nbsp;&nbsp;You are not alone! These other users are online now: '+u", ".join(now)).encode("utf-8")
    print "</div>"
    print '</body></html>'
    #&nbsp;&nbsp;&nbsp;<a href="admin.cgi?project={project}">Corpus Administration</a>
        
    
def printmenues(projectconfig):
    #print projectconfig.functions
    # form for functions and form for categories
    txt = """   
    <div id="funcform" style="display:none;position:absolute;">
        <form  method="post" id="func" name="func" >
            <select id="funchoice" class='funcmenu' onClick="changeFunc(event);"  size=""" +str( len(projectconfig.functions))+""" style="height:"""+str( len(projectconfig.functions)*13.5)+"""px; width:80px;"  >"""
    for f in projectconfig.functions:
        #print "___",f.encode("utf-8")
        txt += "<option style='color: "+projectconfig.funcDic[f]["stroke"].encode("utf-8")+";'>"+f.encode("utf-8")+"</option>"   
    txt += """
            </select>
        </form>
    </div>
    
    <div id="catform" style="display:none;position:absolute;">
        <form  method="post" id="cat" name="cat" >
            <select id="catchoice" class='funcmenu' onClick="changeCat();"  size=""" +str( len(projectconfig.categories))+""" style="height:"""+str( len(projectconfig.categories)*13.5)+"""px; " >"""

    for i,c in enumerate(projectconfig.categories): 
        txt += "<option style='color: "+projectconfig.catDic[c]["fill"].encode("utf-8")+";'>"+c.encode("utf-8")+"</option>"  
    
    txt += """
            </select>
        </form>
    </div>
    <div style="border-top:1px solid #EEE;">&nbsp;</div>    
    """
    
    # form for compare
    txt += """
        <div class="ui-widget ui-widget-content ui-corner-all" style="position: absolute; padding: 5px;z-index:20;display:none;" id="compbox">
            <form id="compform" name="compform" method="POST">
                <div id="complist">
                </div><br>
                <div align="center" id="compasubmit">
                    <img class="compare" src="/static/images/compare.png" border="0" align="bottom" onclick='compareSubmit()'>
                </div>
            </form>
        </div>
        """
    # form for check
    txt += """
        <div class="ui-widget ui-widget-content ui-corner-all" style="position: absolute; padding: 5px;z-index:20;display:none;" id="checkbox">
            
                <div id="checklist">
                </div><br>
                <div align="center">
                    <img src="/static/images/check.png" border="0" align="bottom">
                </div>
            
        </div>
        """
    return txt
    

    
    
    
