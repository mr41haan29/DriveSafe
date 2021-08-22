import os
from flask import Flask
from flask.helpers import url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from werkzeug.utils import redirect
from application.settings_secrets import *
from flask import render_template
from flask import request
import pymongo
from bson.json_util import dumps
from bson.json_util import loads
from opencage.geocoder import OpenCageGeocode


# Connect to Atlas
conn_str = "mongodb+srv://dbUser:dbUser@cluster0.xqerf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

try:
    client.server_info()
    print('\033[92m' + "Connected to Server!" + '\033[0m')
except Exception:
    print("Unable to connect to the server.")

db = client['roads_db']
col = db['ontario_info']

# Connect to geosomething

key = "b3fcc9d195b548ef9f4cdceb593fc22a"
geocoder = OpenCageGeocode(key)

# Initialize Flask and extensions, such as Flask_SQLAlchemy, Flask_Login, etc.
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'
# login_manager.login_message_category = 'info'
# login_manager.login_message = 'You must be logged in to view that page.'

serializer = URLSafeTimedSerializer(SECRET_KEY)


# Initialize Flask-Mail, used for sending confirmation emails
app.config['MAIL_SERVER'] = 'placeholder'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL_EMAIL
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_EMAIL
app.config['MAIL_DEBUG'] = True
mail = Mail(app)


# Import each route from all initializations have been finished
@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        city = request.form["city"]
        return redirect(url_for("city", cty=city))
    else:
        return render_template("home.html")

# TESTING
@app.route("/<cty>")
def city(cty):
    # Mongo markers
    doc = col.find({"SeverityScore": {"$lt": 0.04}}, {"_id": 0}).sort("SeverityScore", -1).limit(25)
    badplaces = col.find({"SeverityScore": {"$gt": 0.1, "$lt": 2.0}}, {"_id": 0}).sort("SeverityScore", -1).limit(25)
    bl = loads(dumps(badplaces))
    l = loads(dumps(doc))
    # Geosomething city location
    results = geocoder.geocode(cty)
    lat = results[0]['geometry']['lat']
    lng = results[0]['geometry']['lng']
    return render_template("waterloo.html", data=l, lat=lat, lng=lng, badplaces=bl, cty=cty)
