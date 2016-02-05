# import db_interactor
import json
import flask
from flask import redirect, url_for, request, Response, jsonify, Flask, session, render_template
from flask_oauthlib.client import OAuth

import httplib2
import json
from urllib.request import Request, urlopen, URLError
from oauth2client import client, crypt
from apiclient import discovery
import uuid

# Local classes
from exceptions import *

app = Flask(__name__)
secret = "thebirdisnine"
app.secret_key = secret

oauth = OAuth(app)

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          consumer_key="316576581621-m15up4ntog0qpgkdigvko683qbj667ua.apps.googleusercontent.com",
                          consumer_secret="ExDFLNcyKWbrrf8iEJRLqBm3")

@app.errorhandler(PhesusException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route('/')
def home():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    access_token = access_token[0]
    headers = {'Authorization', 'OAuth '+ access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo', None, headers)
    try:
        res = urlopen(req)
    except (URLError, e):
        if e.code == 401:
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    return res.read()
# handle serving the gui
#
@app.route("/login")
def login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route('/oauth2callback')
@google.authorized_handler
def authorized(resp):
    access_token=resp['access_token']
    session['access_token'] = access_token
    return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route("/getGraph/<graphId>")
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
def launchEditor():
    return render_template('editor.html')

"""Run the application"""
if __name__ == "__main__":
    app.secret_key = str(uuid.uuid4())
    app.run(debug=True)
