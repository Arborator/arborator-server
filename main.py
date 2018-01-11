# -*- coding: utf-8 -*-
"""
This is a simple Flask app that uses Authomatic to log users in with Facebook Twitter and OpenID.
"""

import flask
from flask import Flask, render_template, request, make_response, url_for, redirect
from werkzeug.security import generate_password_hash, \
     check_password_hash
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic


import flask_login
from flask_login import login_required, current_user
from config import CONFIG
from project import printmyassignments, printalltexts, printuserassignments, printmenues, printmate

import cgitb, cgi, os, sys
sys.path.append('modules')
from logintools import isloggedin
from logintools import logout
from lib import config, database
thisfile = os.environ.get('SCRIPT_NAME',"index.cgi").split("/")[-1]
cgitb.enable()







app = Flask(__name__)
app.secret_key = 'sfdfewefwe@@$ASFSDF@#@#'

# Instantiate Authomatic.
authomatic = Authomatic(CONFIG, 'your secret string', report_errors=False)

# Instantiate login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    found = False
    def __init__(self):
        self.username = None
        self.pw_hash = ''
        self.first_name = ''
        self.last_name = ''
        self.email = ''
        self.image = ''
        self.last_login = ''
        self.adminLevel = 0
        self.admin_logout = 0
        self.password = ''
        self.project = ''

    def init_password(self, username, password):
        self.username = username
        self.set_password(password)
    def initByUsername(self, sql, username):
        user_details = sql.findUser(username)
        if user_details:
            self.found = True
            print user_details
            self.id = user_details[0]
            self.username = username
            self.pw_hash = user_details[6]
            self.first_name = user_details[2]
            self.last_name = user_details[3]
            self.email = user_details[4]
            self.image = user_details[5]
            self.last_login = user_details[7]
            self.adminLevel = user_details[8]
            self.admin_logout = user_details[9]
        else:
            self.found = False

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def set_project(self, project):
        self.project = project

    def createInDB(self,sql):
        if not self.found:
            if self.username:
                
                self.set_password(self.password)
                user_columns = ('user','first_name','last_name','email','image_path', 'password','admin_level', 'logout_by_admin',)
                values = (self.username,self.first_name, self.last_name, self.email,\
                    self.image, self.pw_hash, self.adminLevel, 0)
                user_id = sql.createUser(user_columns, values)
                self.found = True
                self.id = user_id
    def get_id(self):
        return u"%s=>%s"%(self.username, self.project)

# @login_manager.request_loader
# def request_loader(request):
#     email = request.form.get('email')
#     if email not in users:
#         return

#     user = User()
#     user.id = email

#     # DO NOT ever store passwords in plaintext and always compare password
#     # hashes using constant-time comparison!
#     user.is_authenticated = request.form['password'] == users[email]['password']

#     return user


@login_manager.user_loader
def load_user(user_id):
    user = None
    if '=>' in user_id:
        username = user_id.split('=>')[0]
        project = user_id.split('=>')[1]
        sql = database.SQL(project)
        user = User()
        user.initByUsername(sql, username)
        user.set_project(project)
        if not user.found:
            return None
    return user
@app.route('/', defaults={'project': ''})
@app.route('/index/<project>')
def index(project):
    """
    Home handler
    """
    thisfile = os.environ.get('SCRIPT_NAME',".")
    form = cgi.FieldStorage()

    userdir = 'users/'
    logintest = isloggedin(userdir)

    logint = form.getvalue("login",None)
    action = None

    if project: 
        try:    project=project.decode("utf-8")
        except: pass
    if len(config.projects)==1:project=config.projects[0]

    projectconfig=None
    try:    projectconfig = config.configProject(project) # read in the settings of the current project
    except: pass
    if logintest:
        userconfig = logintest[0]
    #action, userconfig = login(form, userdir, thisfile, action)
        adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"],userconfig["realname"]
    else:
        #adminLevel, username, realname = 0,"guest","guest"
        adminLevel, username, realname = 0,None,None

    if logintest and logint != "logout": buttonname="Enter"# enter
    else: buttonname="Login"
    
        
    return render_template('home.html', project=project, config=config, projectconfig=projectconfig, asset="/static")


@app.route('/login/<project>/', methods=['GET', 'POST'])
def ulogin(project):
    error = ""
    success = False
    if request.method == 'POST':
        sql = database.SQL(project)
        user = User()
        user.initByUsername(sql, request.form['username'])

        login_user = User()
        login_user.init_password(request.form['username'], request.form['pass'])

        if user.found and login_user.pw_hash == user.pw_hash:
            success = True
            user.set_project(project)
            flask_login.login_user(user)
            next = request.args.get('next')
            return redirect(next or flask.url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'


    return render_template('login_page.html', project=project, asset="/static", error=error, success=success)

@app.route('/newlogin/<project>/', methods=['GET', 'POST'])
def new_login(project):
    
    return render_template('new_login.html', project=project, asset="/static")


@app.route('/slogin/<project>/<provider>/', methods=['GET', 'POST'])
def slogin(project, provider):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider)
    
    # If there is no LoginResult object, the login procedure is still pending.
    next = request.args.get('next')
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
            sql = database.SQL(project)
            user = User()
            if provider == "tw":
                user.initByUsername(sql, "%s@twitter"%(result.user.username))
                if user.found:
                    #login
                    print 'login'
                    user.set_project(project)
                    flask_login.login_user(user)
                else: #create user
                    user.username = "%s@twitter"%(result.user.username)
                    user.first_name = result.user.name
                    user.createInDB(sql)
                    print 'created'
                    user.set_project(project)
                    flask_login.login_user(user)
            return flask.redirect(next or flask.url_for('index'))

        # The rest happens inside the template.
        return render_template('login.html', result=result)
    
    # Don't forget to return the response.
    return response
@app.route('/project/<project>/', methods=['GET', 'POST'])
def project(project):
    if current_user.is_authenticated and current_user.project == project:
        print 'yes'
        sql = database.SQL(project)
        projectconfig = config.configProject(project)
        myassignments = printmyassignments(project,sql,projectconfig,current_user.id)
        alltext = printalltexts(project,sql, current_user.adminLevel,projectconfig)
        userassignments = printuserassignments(project,projectconfig,sql,current_user.adminLevel)
        menus = printmenues(project,sql, projectconfig)
        mate = printmate(project,projectconfig, sql, current_user.adminLevel)
        return render_template('project.html', project=project, \
            myassignments=myassignments,userassignments=userassignments, alltext=alltext,mate=mate, menus=menus, asset="/static")
    else:
        return flask.redirect(flask.url_for('ulogin', project=project))

@app.route('/editor/<project>/<text_id>/<opensentence>/', methods=['GET', 'POST'])
def editor(project,text_id,opensentence):
    textid=int(text_id)
    from editor import printhtmlheader,printheadline,printmenues
    if current_user.is_authenticated and current_user.project == project:
        sql = database.SQL(project)
        projectconfig = config.configProject(project)
        txt = ""
        if not projectconfig:
        #print "Content-Type: text/html\n" # blank line: end of headers
            txt = "something went seriously wrong: can't read the configuration of the project",project.encode("utf-8")
        try:
            _,textname,_ = sql.getall(None, "texts",["rowid"],[text_id])[0]
        except:
            pass
            txt+= "something went seriously wrong: The text you are looking for does not seem to exist! project"
            textname="text not found!"
        todo = sql.gettodostatus(current_user.id,textid)
        validator=0
        if todo>0: validator=int(todo) # -1 and 0 => 0, 1 => 1
        projectEsc=project.replace("'","\\'").replace('"','\\"')
        validvalid=sql.validvalid(textid)
        
        exotype, exotoknum =sql.getExo(textid)
        addEmptyUser=None
        #print "uu",sql.exotypes[exotype],sql.exotypes[exotype]=="graphical feedback"
        if sql.exotypes[exotype] in ["teacher visible","graphical feedback", "percentage"] :
            addEmptyUser=current_user.username
        if sql.exotypes[exotype] in ["teacher visible"] :
            validvalid+=[sql.userid(sql.teacher)]
        if sql.exotypes[exotype]=="graphical feedback":
            graphical=1
        if exotoknum and not current_user.adminLevel:    quantityInfo = ">"+str(exotoknum)+" tokens"
        else:                   quantityInfo = str(sql.getnumber(None, "sentences",["textid"],[textid]))+" sentences"
        
        jsdef = config.jsDefPrinter(projectconfig)
        htmlheader = printhtmlheader(projectEsc,textname,current_user,textid,current_user.id,sql,todo,validator,addEmptyUser,validvalid,opensentence, projectconfig)
        headline  = printheadline(project,textname,quantityInfo,current_user)
        userid = current_user.id
        main = ""
        for snr,sid,s,tid in sql.getAllSentences(textid, current_user.username, current_user.id, current_user.adminLevel):
            #print adminLevel, validvalid, validator
            treelinks, firsttreeid, sentenceinfo=sql.links2AllTrees(sid,snr,current_user.username,current_user.adminLevel, todo, validvalid, validator,addEmptyUser=addEmptyUser)
            status=""
            if todo>=0:status=sql.gettreestatus(sid,userid)
            status="<span id='status{nr}' class='status' onClick='nexttreestatus({sid},{nr})'>{status}</span>".format(status=status,sid=sid, nr=snr)
            connectRight=""
            if current_user.adminLevel or (sql.validatorsCanConnect and validator):
                connectRight='''<img class="connectRight" src="/static/images/chain.png" border="0" align="bottom" id='connectRight{nr}' nr='{nr}' title="connect with next tree (+ctrl: split at selcted word)"> '''.format(nr=snr)
            exo=""
            if exotype>1: # 0: no exercise, 1: no feedback
                exo='''<img class="check" src="/static/images/check.png" border="0" align="bottom" id='check{nr}' nr='{nr}' title="check annotation" graphical={graphical}> '''.format(nr=snr, graphical=graphical)
            main += '''<div id='sentencediv{nr}' class='sentencediv' style="margin:10px;" sid={sid}  nr={nr}>
                    <a id='toggler{nr}' class="toggler" treeid="{firsttreeid}" nr="{nr}" >
                        {nr}: {sentence} &nbsp;
                    </a> 
                    <span id="othertrees{nr}" > {treelinks} </span>
                    <img class="saveimg" src="/static/images/save.png" border="0" align="bottom" id='save{nr}' title="save">
                    <img class="undoimg" src="/static/images/undo.png" border="0" align="bottom" id='undo{nr}'>
                    <img class="redoimg" src="/static/images/redo.png" border="0" align="bottom" id='redo{nr}'> 
                    {status}
                    <img class="exportimg" src="/static/images/export.png" border="0" align="bottom" id='export{nr}' nr='{nr}' title="export"> 
                    {connectRight}
                    {exo}
                </div><p><small>{sentenceinfo}</small></p>'''.format(sentence=s.encode("utf-8"),nr=snr, sid=sid, firsttreeid=firsttreeid, project=project.encode("utf-8"), userid=userid, treelinks=treelinks.encode("utf-8"), status=status,connectRight=connectRight,exo=exo,sentenceinfo=sentenceinfo.encode("utf-8"))
        menus = printmenues(projectconfig)
        return render_template('editor.html', project=project, \
            textname=textname,htmlheader=htmlheader,menus=menus, headline=headline,main=main.decode("utf-8"), jsdef=jsdef, asset="/static")
    else:
        return flask.redirect(flask.url_for('ulogin', project=project))


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('index'))

# Run the app.
if __name__ == '__main__':
    app.secret_key = 'sfdfewefwe@@$ASFSDF@#@#'
    app.run() 
