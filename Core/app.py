import db_interactor
import json
import flask
from functools import wraps
from flask import redirect, url_for, request, Response, jsonify, Flask, session, render_template
from flask_oauthlib.client import OAuth

import httplib2
import json
from urllib.request import Request, urlopen, URLError
from oauth2client import client, crypt
from apiclient import discovery
import uuid
import pdb
import time
import datetime

# Local classes
from exceptions import *

app = Flask(__name__)
secret = str(uuid.uuid4())
app.secret_key = secret

oauth = OAuth(app)

tokens={}

"""
Client to be used for all authentication.
Can use similar implementation to add twitter, facebook, etc.
"""
google = oauth.remote_app('google',
                          base_url='https://www.googleapis.com/oauth2/v1/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'email','access_type':'offline'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          consumer_key="316576581621-m15up4ntog0qpgkdigvko683qbj667ua.apps.googleusercontent.com",
                          consumer_secret="ExDFLNcyKWbrrf8iEJRLqBm3")

@app.errorhandler(PhesusException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

"""
Authentication wrapper
"""
def isAuthenticated(func):
    @wraps(func)
    def a(*args, **kwargs):
        access_token = session.get('access_token')
        if access_token is None:
            return redirect(url_for('login'))
        else:
            #FIXME:this is BAD, make sure to query google in the future, as it stands client can just modify cookie.
            if session.get('expiry_time') < time.time():
                return redirect(url_for('login'))
            return func(*args, **kwargs)
    return a

@app.route('/')
@isAuthenticated
def index():
    return ("Welcome {}".format(session['name']))

def getUserData():
    access_token = session['access_token']
    headers = {'Authorization': 'OAuth '+ access_token}
    req = Request('https://www.googleapis.com/oauth2/v2/userinfo', None, headers)
    try:
        res = urlopen(req)
    except (URLError, e):
        if e.code == 401:
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return json.load(res.read())
    return json.loads(res.read().decode('utf-8'))

# handle serving the gui
@app.route("/login")
def login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)

#remove session
@app.route("/logout")
def logout():
    session.pop('access_token', None)
    return redirect(url_for('index'))

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

#handle response from google
@app.route('/oauth2callback')
def authorized():
    resp = google.authorized_response()

    access_token=resp['access_token']
    refresh_token=resp['refresh_token']
    expiry_time=resp['expires_in']
    expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=expiry_time)
    #set session access token
    session['access_token'] = access_token
    session['expiry_time'] = time.mktime(expiry_time.timetuple())
    #FIXME:also bad, make our own ids instead of using google.

    data = getUserData()

    #TODO migrate to redis
    tokens['id']={'access_token':access_token, 'refresh_token':refresh_token, 'expiry_time':expiry_time}

    session['id']=data['id']
    session['name']=data['name']

    #FIXME: dont put all processing on database
    createUser(data['name'], data['email'], data['id'])

    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route("/createNode/<projectId>/<x>/<y>")
@isAuthenticated
def createNode(projectId, x, y):
 #TODO actaully take json
    if db_interactor.createNode(uid=session['id'], pid = projectId, x=x, y=y, type=db_interactor.NodeType.NORMAL, contentJson=json.dumps("")) is not None:
        return "success"
    raise PhesusException("Couldn't create node")

@app.route("/createConnection/<projectId>/<fromnode>/<tonode>")
@isAuthenticated
def createConnection(projectId, fromnode, tonode):
    if db_interactor.createConnection(uid=session['id'],pid=projectId, type=db_interactor.ConnectionType.NORMAL, fromnode=fromnode, tonode=tonode, metadata=json.dumps({})) is not None:
        return "success"
    raise PhesusException("Couldn't create connection")

"""
Return the project data
"""
@app.route("/getProject/<projectId>")
@isAuthenticated
def getProject(projectId):
    return db_interactor.getProject(uid=session['id'], pid=projectId)

"""
Get projects for a user id.
"""
@app.route("/getProjects")
@isAuthenticated
def getProjects():
    id = session['id']
    return db_interactor.getProjects(uid=id)

"""
Create a new project for the current logged in user.
"""
@app.route("/createProject")
@isAuthenticated
def createProject():
    data =  db_interactor.createProject(session['id'],[])
    return str(data)

"""
Helper method to create a new user after logging in.
"""
def createUser(name, email, id):
    if email is not None and name is not None and id is not None:
        return db_interactor.createUser(name, email, id)
    else:
        raise PhesusException("Required fields for user cannot be blank.")

"""
Run the application
"""
if __name__ == "__main__":
    app.run(debug=True)
