# import db_interactor
import json
from functools import wraps
from flask import redirect, url_for, request, Response, jsonify, Flask, session
from exceptions import *

import httplib2
import flask
import json
from urllib.request import Request, urlopen, URLError
from oauth2client import client, crypt
from apiclient import discovery
import uuid

app = Flask(__name__)

@app.errorhandler(PhesusException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def checkTokenValidity():
    try:
        idinfo = client.verify_id_token(token, CLIENT_ID)
        # If multiple clients access the backend server:
        if idinfo['aud'] not in [ANDROID_CLIENT_ID, IOS_CLIENT_ID, WEB_CLIENT_ID]:
            raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
        if idinfo['hd'] != APPS_DOMAIN_NAME:
            raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError as error:
        # Invalid token
        return error
    userid = idinfo['sub']


def check_auth(username, password):
    return db_interactor.checkLogin(username, password)


def authenticate():
    return Response('Could not verify access level.')


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


# handle serving the gui
@app.route("/")
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        drive_service = discovery.build('drive', 'v2', http_auth)
        files = drive_service.files().list().execute()
        return json.dumps(files)


@app.route('/oauth2callback')
def oauth2callback():
      flow = client.flow_from_clientsecrets(
          'client_secrets.json',
          scope='https://www.googleapis.com/auth/drive.metadata.readonly',
          redirect_uri=flask.url_for('oauth2callback', _external=True),
          include_granted_scopes=True)
      if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
      else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))

@app.route(REDIRECT_URI)
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@app.route("/login")
def login():
    return "login"

@app.route("/getGraph")
@requires_auth
def getGraph():
    return "Success"


# create a user account
@app.route("/createuser/<userId>")
def createUser(userId=None):
    if (userId is not None):
        db_interactor.createUser(userId)
    else:
        raise PhesusException("Need to provide a valid userId", 400)
    return "Created a User"


@app.route("/createConnection")
@requires_auth
def createConnection():
    return "Created a connection"


@app.route("/editor")
def launchEditor():
    return "Launched an Editor"

@app.route("/createNode")
def createNode():
    x = request.args.get("x", '')
    y = request.args.get("y", '')
    type = request.args.get("type", '')
    content = request.args.get("content", '')
    pid = request.args.get("pid", '')
    db_interactor.createNode(x, y, type, content, pid)
    return "Created a Node"


"""Run the application"""
if __name__ == "__main__":
    app.secret_key = str(uuid.uuid4())
    app.run(debug=True)
