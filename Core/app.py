# import db_interactor
import json
from functools import wraps
from flask import redirect, url_for, request, Response, jsonify, Flask, session, render_template
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

def check_auth(username=username, password=password):
    return db_interactor.checkLogin(username, password)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return flask.redirect(flask.url_for('login'))
        return f(*args, **kwargs)
    return decorated


# handle serving the gui
@app.route("/login")
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        return render_template('index.html')


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/drive.metadata.readonly',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))

@app.route("/getGraph/<graphId>")
@requires_auth
def getGraph(graphId):
    uid = request.args.get('userId')
    pid = request.args.get('projectId')

    if uid is None:
        raise PhesusException("User Id cannot be null.")
    if pid is None:
        raise PhesusException("Need to specify a project to load.")

    return db_interactor.getProject(uid=uid, pid=pid)

# create a user account
@app.route("/createuser")
def createUser():
    email = request.args.get('email', '')
    name = request.args.get('name', '')

    if email is not None and name is not None:
        return db_interactor.createUser(email, "id", name)
    else:
        raise PhesusException("Required fields for user cannot be blank.")

@app.route("/editor")
@requires_auth
def launchEditor():
    return "Launched an Editor"

"""Run the application"""
if __name__ == "__main__":
    app.secret_key = str(uuid.uuid4())
    app.run(debug=True)
