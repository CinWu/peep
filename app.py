from flask import Flask, render_template, request, session,redirect,url_for, flash
import csv
import sqlite3,unicodedata
from utils import manager
from datetime import datetime

app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def home():
    return render_template("home.html")

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template("about.html")

@app.route("/create", methods=['GET', 'POST'])
def create():
    return render_template("create.html")

@app.route("/logout",methods=['GET','POST'])
def logout():
    ids=manager.getIDs()
    if 'username' in session:
        session.pop('username', None)
        return render_template("logout.html", loggedin=False, previous=True, ids=ids)
    else:
        return render_template("logout.html",loggedin=False, previous=False, ids=ids)

@app.route("/register",methods=['GET','POST'])
def register():
    ids= manager.getIDs()
    if 'username' in session:
        loggedin=True
        username=session['username']
        if request.method=='POST':
            if request.form["submit"] == "Go":
                if manager.getProfilePath() != "profile/":
                    return redirect(manager.getProfilePath())
    else:
        loggedin=False
        username=''
    if request.method=='POST':
        if 'username' not in session:
            username = request.form['username']
            password = request.form['password']
            reppassword = request.form['password2']
            first = request.form['first']
            last = request.form['last']
            email = request.form['email']
            repemail = request.form['email2']
            phone = request.form['phone']
            
            if 'facebook' in request.form:
                facebook = request.form['facebook']
            else:
                facebook = ""
                
            reason = ""
            registered=False

            if email != repemail:
                registered=False
                reason = "Emails do not match"
                print "Emails do not match"

            if password == reppassword:
                registered=True
            else:
                registered=False
                reason = "Passwords do not match"
                print "Passwords do not match"


            conn = sqlite3.connect("databases/users.db")
            c = conn.cursor()
            
            c.execute("select * from uinfo")
            tabledata = c.fetchall()
            for d in tabledata:
                if username == d[0]:
                    registered=False
                    reason="The username "+username+" already exists!"
                    print "Username % is already in use" %username
                 
            pvalidate = manager.validateEntry(password)
            if pvalidate != "":
                registered=False
                reason = "Password: " + pvalidate
             
            uvalidate = manager.validateEntry(username)
            if uvalidate != "":
                registered=False
                reason = "Username: " + uvalidate
                
            if registered:
                insinfo="insert into uinfo values ('"+username+"','"+password+"','"+first+"','"+last+"','"+phone+"','"+email+"','"+facebook+"')"
                c.execute(insinfo)
                conn.commit()
                print 'Username and Password have been recorded as variables'
                manager.userNotifTable(username)
            else:
                print "Failure to register"

            conn.close()
            
            if registered:
                return render_template("register.html", page=1, username=username,ids=ids)
                return render_template("register.html", page=2, reason=reason,ids=ids)
    else:
        return render_template("register.html", page=3, loggedin=loggedin, username=username, ids=ids) 

@app.route("/login",methods=['GET','POST'])
def login():
    ids= manager.getIDs()
    if 'username' in session:
        return render_template("login.html", loggedin=True, username=luser,ids=ids)
        
    if request.method=='POST':
       
        username = request.form['username']
        password = request.form['password']
        print 'Username and Password have been recorded as variables'
      
        exists = False
        loggedin = False
        reason = ""
        
        conn = sqlite3.connect("databases/users.db")
        c = conn.cursor()
        
        c.execute("select * from uinfo")

        tabledata = c.fetchall()
        for d in tabledata:
            if username == d[0]:
                exists = True
                savedpass = d[1]
                
        conn.close()

        if exists == False:
            reason = "The username "+ username + " does not exist."
            
        if (exists == True and savedpass == password):
            loggedin = True
            
        if (exists == True and savedpass != password):
            reason = "Your username and password do not match"
          
        if loggedin:
            session['username']=username
            
        return render_template("login.html", loggedin=loggedin, username=username, reason=reason, ids=ids)
    else:
        print session
        return render_template("login.html", loggedin=False, ids=ids)

@app.route("/<username>",methods=['GET','POST'])
def profile(username=None):
    ids=manager.getIDs()
    if username in ids and 'username' in session:
        first = manager.getFirst(username)
        last = manager.getLast(username)
        email = manager.getEmail(username)
        phone = manager.getPhone(username)
        return render_template("profile.html",username=username,first=first,last=last,phone=phone,email=email )
    else:
        return render_template("base.html")

@app.route('/create_event', methods = ['GET','POST'])
def create_event():
    if request.method == "POST":
        conn = sqlite3.connect("databases/events.db")
        c = conn.cursor()
        if 'username' in session:
            username = session['username']
            event = request.form['event']
            place = request.form['location']
            time = request.form['time']
            detail = request.form['detail']
            
            c.execute('create table if not exists events (name,event,place,time,detail)')
            insinfo="insert into events values ('"+username+"','"+event+"','"+place+"','"+time+"','"+detail+"')"
            c.execute(insinfo)
            conn.commit()
            print 'event created'
            conn.close()

        else:
            flash("Login to create an event!")
            return redirect('/login')
            
    return redirect('/')

@app.route("/events", methods=['GET', 'POST'])
def events():
    data = manager.getEventData()
    print data
    return render_template('events.html', data=data)
            
if __name__ == "__main__":
    app.debug = True
    app.secret_key = "peep"
    app.run()
