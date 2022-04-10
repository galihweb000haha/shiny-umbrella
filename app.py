import os
# flask
from flask import Flask, render_template, request
# csrf
from flask_wtf.csrf import CSRFProtect, CSRFError
# SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
# limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
project_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(125), unique=True, nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()


@app.route("/", methods=['GET'])
def home():
    return render_template('index.html')

@app.route("/login", methods=['POST'])
@limiter.limit("1 per day")
def login():
    username = request.form['username']
    password = request.form['password']

    # user = User.query.filter_by(username=username, password=password).first()

    # query = "SELECT * FROM user WHERE username = :username"
    # user = db.engine.execute(query, username = username)

    query = "SELECT * FROM user WHERE username ='" + username + "' AND password='" + password +"'"
    user = db.engine.execute(query)


    if user:
        return 'Boleh masuk'
    else :
        return 'Tidak boleh masuk'


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400


# sqlmap -u "http://127.0.0.1:5000/login" --data='username=%27%3D%22or%27&password=%27%3D%22or%27' --batch --dbms=SQLite --risk=3 --level=3 -T user --columns --flush-session
