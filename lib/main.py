# -*- coding: utf-8 -*-
"""
This is a simple Flask app that uses Authomatic to log users in with Facebook Twitter and OpenID.
"""

from flask import Flask, render_template, request, make_response
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic


import flask_login
from flaskconfig import CONFIG


import cgitb, cgi, os, sys
sys.path.append('modules')
from logintools import isloggedin
from logintools import logout
from lib import config
thisfile = os.environ.get('SCRIPT_NAME',"index.cgi").split("/")[-1]
cgitb.enable()







app = Flask(__name__)

# Instantiate Authomatic.
authomatic = Authomatic(CONFIG, 'your secret string', report_errors=False)

# Instantiate login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/index')
def index():
    """
    Home handler
    """
    thisfile = os.environ.get('SCRIPT_NAME',".")
    form = cgi.FieldStorage()

    userdir = 'users/'

    logint = form.getvalue("login",None)

    project = form.getvalue("project",None)
    if project: 
        try:    project=project.decode("utf-8")
        except: pass
    if len(config.projects)==1:project=config.projects[0]

    projectconfig=None
    try:    projectconfig = config.configProject(project) # read in the settings of the current project
    except: pass

    if logintest and logint != "logout": buttonname="Enter"# enter
    else: buttonname="Login"
    action, userconfig = login(form, userdir, thisfile+'?project='+project, action)
    adminLevel, username, realname = int(userconfig["admin"]),userconfig["username"],userconfig["realname"]
        
    return render_template('index.html', project=project, logint=logint, 
        config=config, projectconfig=projectconfig, buttonname=buttonname, username=username,
        realname=realname, adminLevel)


@app.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    
    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
        
        # The rest happens inside the template.
        return render_template('login.html', result=result)
    
    # Don't forget to return the response.
    return response

@app.route('/logout')
def logout():
    flask_login.logout_user()

# Run the app.
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=2830) 
