from flask import Flask
import db_interactor
app = Flask(__name__)

#handle serving the gui
@app.route("/")
def handleHomepage():
    pass

#handle data requests
@app.route("/data")
    pass

if __name__ == "__main__":
    app.run(debug=True)
