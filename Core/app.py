import db_interactor
from functools import wraps
from flask import request, Response, jsonify, Flask
import json

app = Flask(__name__)

class PhesusException(Exception):
    """ class for exceptions
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

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
def handleHomepage():
    return render_template('landing.html')

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

@app.route("/createConnection")
def createConnection():
    pass

@app.route("/createNode")
def createNode():
    pass

def authenticate():
    pass
if __name__ == "__main__":
    app.run(debug=True)
