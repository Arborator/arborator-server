#!/usr/bin/python
from flask import Flask,  render_template, request, make_response
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
app = Flask(__name__)
app.config['SERVER_NAME'] = '127.0.0.1:8080'
from config import CONFIG
authomatic = Authomatic(config=CONFIG, secret='srgeargdafgdfag')
@app.route("/abc")
def hello():
    return "Hello World!"
@app.route("/login/<provider_name>/", methods=['GET', 'POST'])
def login(provider_name):
    response = make_response()
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
    if result:
        if result.user:
            result.user.update()
        return render_template('login.html', result=result)
    return response
    
