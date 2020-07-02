import os
import requests
from datetime import datetime
from flask import Flask, session,render_template,request,redirect,url_for,flash,make_response,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"),pool_size=20,max_overflow=0)
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if request.cookies.get('username'):
        return redirect(url_for('login'))
    if request.cookies.get('msg'):
        return render_template("register.html",msg=request.cookies.get('msg'))
    return render_template("register.html")


@app.route("/register",methods=["POST","GET"])
def register():
    if request.cookies.get('username'):
        return render_template("home.html",user=request.cookies.get('username'))
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if db.execute("SELECT * from users WHERE username= :u AND password= :p",{"u":username,"p":password}).rowcount == 1 :
            print("User already exists,Log In")
            r1 = make_response(redirect(url_for('loginpage')))
            r1.set_cookie('msg','User already exists,Log In',max_age=10) 
            return r1
        elif db.execute("SELECT * from users WHERE username= :u",{"u":username}).rowcount == 1:
            print("Username already exists, try using another one 🤔")
            r2 =make_response(redirect(url_for('index')))
            r2.set_cookie('msg','Username already exists, try using another one 🤔',max_age=10)
            return r2 
        else :
            db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",{"username":username,"password":password})
            db.commit()
            print("Registration Successful!!!,now login to the world of books")
            r3 = make_response(redirect(url_for('loginpage')))
            r3.set_cookie('msg','Registration Successful!!!,now login to start writing a Diary',max_age=10) 
            return r3


@app.route("/login",methods=["POST","GET"])
def loginpage():
    if request.cookies.get('username'):
        return redirect(url_for('login'))
    if request.method == "GET" and request.cookies.get('msg'):
        msg = request.cookies.get('msg')
        return render_template("login.html",msg=msg)
    else:
        re=make_response(render_template("login.html"))
        re.set_cookie('msg','',expires=0)
        return re

@app.route("/home",methods=["POST","GET"])
def login():
    if request.cookies.get('username'):
        now = datetime.now()
        dt = now.strftime(" %d %B %Y ")
        ti = now.strftime(" %X ")
        print(dt)
        return render_template("home.html",user=request.cookies.get('username'),msg=request.cookies.get('msg'),dt=dt,ti=ti)
    if request.method == "POST":
        UName = request.form.get("username")
        Pwd = request.form.get("password")
        
        if db.execute("SELECT * from users WHERE username= :u AND password= :p",{"u":UName,"p":Pwd}).rowcount == 1 :
            print("Successful login")
            resp=make_response(render_template("home.html",user=UName))
            resp.set_cookie('username',UName)
            return resp
        else :
            print("Incorrect username/password, Try again")
            r3 =make_response(redirect(url_for('loginpage')))
            r3.set_cookie('msg','Incorrect username/password, Try again 😓',max_age=10) 
            return r3
    if request.method == "GET":
        return redirect(url_for('index'))

@app.route("/read")
def readpage():
    if request.cookies.get('username'):
        u = request.cookies.get('username')
        diary=db.execute("SELECT * FROM diary WHERE username=:u",{"u":u}).fetchall()
        return render_template('read.html',user=request.cookies.get('username'),diary=diary)
    else:
        return redirect(url_for('index'))


    

@app.route("/submission-in-progress",methods=["POST","GET"])
def diarysubmit():
    if request.method == "GET":
        return redirect(url_for('index'))
    if request.method == "POST":
        now = datetime.now()
        dt = now.strftime(" %d %B %Y ")
        ti = now.strftime(" %X ")
        text=request.form.get("diarytext")
        t=request.form.get("title")
        user = request.cookies.get('username')
        db.execute("INSERT INTO diary (username,diarytext,date,time,title) VALUES (:u, :diary, :date, :time, :t)",{"u":user,"diary":text,"date":dt,"time":ti,"t":t})
        db.commit()
        return redirect(url_for('login'))




@app.route("/logout")
def logout():
    res=make_response(render_template("logout.html"))
    res.set_cookie('username','',expires=0)
    return res

