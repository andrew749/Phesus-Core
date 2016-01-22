# import db_interactor
from functools import wraps
from flask import redirect, url_for, request, Response, jsonify, Flask, session
import json
from flask_oauthlib.client import OAuth
from exceptions import *
app = Flask(__name__)

CLIENT_ID = "316576581621-m15up4ntog0qpgkdigvko683qbj667ua.apps.googleusercontent.com"
CLIENT_SECRET = "ExDFLNcyKWbrrf8iEJRLqBm3"
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console
secret_key = "ayylmao"
app.secret_key = secret_key
oauth = OAuth(app)

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=CLIENT_ID,
                          consumer_secret=CLIENT_SECRET)
@app.errorhandler(PhesusException)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

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


#handle serving the gui
@app.route("/")
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]

    from urllib.request import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except (URLError, e):
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()

    return res.read()

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

@app.route("/login")
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@google.tokengetter
def get_access_token():
    return session.get('access_token')

@app.route("/getGraph")
@requires_auth
def getGraph():
    return "Success"

#create a user account
@app.route("/createuser/<userId>")
def createUser(userId=None):
    if(userId is not None):
        db_interactor.createUser(userId)
    else:
        raise PhesusException("Need to provide a valid userId", 400)

@app.route("/authenticated/")
def authenticated():
    pass

@app.route("/createConnection")
def createConnection():
    pass

@app.route("/createNode")
def createNode():
    x = request.args.get("x",'')
    y = request.args.get("y",'')
    type = request.args.get("type",'')
    content = request.args.get("content",'')
    pid = request.args.get("pid",'')
    db_interactor.createNode(x, y, type, content, pid)

def authenticate(func):
    pass

"""Run the application"""
if __name__ == "__main__":
    app.run(debug=True)
