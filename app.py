from flask import Flask, render_template, request, session,redirect,url_for, flash
import csv
import sqlite3,unicodedata
from utils import manager
from datetime import datetime
##install facebook-sdk
#import facebook

FACEBOOK_APP_ID = '378920438974120'
FACEBOOK_APP_SECRET = 'b6062e3515963deff605a9538c45f675'
##Testing
#ACCESS_TOKEN = 'CAAFYoEopxqgBAJiWUc1J3HAGbQZBw8mOZAOgktaXBcWb9Okma9Lmyd5kGOdIhhVBlJEld6uimSVMu8QNaXe9HZAPBvCsXHtYs24GfZBkXpciSgFrdfCtQMPINJmdmSkM9ZCZCOLyI0VsJoHHoGhAZCkOvZC0ADRFQh6NDncYZC2GlzOWfnxCL5hHBL81EJFvLU3VhzyGaZCEsPcvk2L0jMd6hM2Y5R1dwi8SoZD'

app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def home():
#    graph = facebook.GraphAPI(ACCESS_TOKEN)
#    print graph.get_object('me')
    if 'username' in session:
        requests = manager.getRequests(session['username'])
        requests.reverse()
        username = session['username']
        first = manager.getFirst(username)
        last = manager.getLast(username)
        email = manager.getEmail(username)
        phone = manager.getPhone(username)
        events = manager.getEventData()
        created = manager.getCreated(username)
        created.reverse()
        accepted= manager.getAccepted(username)
        accepted.reverse()
        pending=manager.getPending(username)
        pending.reverse()
        print "CREATED"
        print created
        print "ACCEPTED"
        print accepted
        print "PENDING"
        print pending
        if request.method == 'POST':
            print request.form
            if request.form["status"]=="approve":
                user = request.form["user"]
                event = request.form["event"]
                manager.addMember(event, user)
                manager.removeRequest(event, user)
                accepted= manager.getAccepted(username)
                accepted.reverse()
                requests = manager.getRequests(session['username'])
                requests.reverse()
            if request.form["status"]=="reject":
                user = request.form["user"]
                event = request.form["event"]
                manager.removeRequest(event, user)
                requests = manager.getRequests(session['username'])
                requests.reverse()
        return render_template("home.html", session=session, requests=requests, created=created, accepted=accepted, pending=pending, events=events,username=username,first=first,last=last,phone=phone,email=email)
    return render_template("home.html")

@app.route("/about", methods=['GET','POST'])
def about():
    if 'username' in session:
        loggedin=True
        username=session['username']
        first = manager.getFirst(username)
        last = manager.getLast(username)
        email = manager.getEmail(username)
        phone = manager.getPhone(username)
        created = manager.getCreated(username)
        accepted= manager.getAccepted(username)
        return render_template("about.html",username=username,first=first,last=last,email=email,phone=phone,created=created,accepted=accepted)
    return render_template("about.html")

@app.route("/create", methods=['GET', 'POST'])
def create():
    username = ""
    ids=manager.getIDs()
    if 'username' in session:
        loggedin=True
        username=session['username']
        first = manager.getFirst(username)
        last = manager.getLast(username)
        email = manager.getEmail(username)
        phone = manager.getPhone(username)
        created = manager.getCreated(username)
        accepted= manager.getAccepted(username)
        if request.method=='POST':
            if request.form["submit"] == "Go":
                if manager.getProfilePath() != "profile/":
                    return redirect(manager.getProfilePath())
            if request.form["submit"]=="Create Event":
                event = request.form["event"]
                location = request.form["location"]
                date=request.form["date"]+" "+request.form["time"]
                description = request.form["description"]
                dtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                tags = request.form["tags"]
                requestlist = tags.split(',')
                for x in requestlist:
                    x.strip()
                print requestlist
                manager.addEvent(dtime,event,username,description,location,date,tags)
                return redirect("/events")
        else:
            return render_template("makeEvents.html",loggedin=loggedin,ids=ids,username=username,first=first,last=last,phone=phone,email=email,created=created,accepted=accepted)
    else:
        return render_template("makeEvents.html",loggedin=False,ids=ids)
  
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
            registered=True

            if email != repemail:
                registered=False
                reason = "Emails do not match"
                print "Emails do not match"

            if password != reppassword:
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
            first = manager.getFirst(username)
            last = manager.getLast(username)
            email = manager.getEmail(username)
            phone = manager.getPhone(username)
            created = manager.getCreated(username)
            accepted= manager.getAccepted(username)
            return render_template("login.html",username=username,loggedin=True,first=first,last=last,email=email,phone=phone,created=created,accepted=accepted) 
        return render_template("login.html", loggedin=loggedin, username=username, reason=reason, ids=ids)
    else:
        return render_template("login.html", loggedin=False, ids=ids)

@app.route("/profile/<username>",methods=['GET','POST'])
def profile(username=None):
    ids=manager.getIDs()
    data = manager.getEventData()
    if username in ids:
        pfirst = manager.getFirst(username)
        plast = manager.getLast(username)
        pemail = manager.getEmail(username)
        pphone = manager.getPhone(username)
        taccepted = manager.getAccepted(username)
        paccepted = []
        for a in taccepted:
            paccepted.append(int(a))
        if 'username' in session:
            ausername=session['username']
            first = manager.getFirst(ausername)
            last = manager.getLast(ausername)
            email = manager.getEmail(ausername)
            phone = manager.getPhone(ausername)
            created = manager.getCreated(ausername)
            accepted= manager.getAccepted(ausername)
            return render_template("profile.html",pusername=username,pfirst=pfirst,plast=plast,pphone=pphone,pemail=pemail, username=ausername, first=first,last=last,email=email,phone=phone,created=created,accepted=accepted,paccepted=paccepted, events=data)
        return render_template("profile.html",pusername=username,pfirst=pfirst,plast=plast,pphone=pphone,pemail=pemail,paccepted=paccepted,events=data)
    else:
        return redirect("/")

@app.route("/events",methods=['GET','POST'])
@app.route("/events/<eventname>", methods=['GET', 'POST'])
def events(eventname=None):
    username=""
    first=""
    last=""
    email=""
    phone=""
    created=""
    accepted=""
    data = manager.getEventData()
    if eventname==None:
        if request.method == "POST":
            peep = request.form['peep']
            at = request.form['at']
            data = manager.eventSearch(peep)        
            #if data is null return some text
        data.sort(key=lambda x:x[6])
        data = manager.removeExpired(data)
        if 'username' in session:
            username = session['username']
            first = manager.getFirst(username)
            last = manager.getLast(username)
            email = manager.getEmail(username)
            phone = manager.getPhone(username)
            created = manager.getCreated(username)
            accepted= manager.getAccepted(username)
        return render_template('events.html', data=data, search=True,username=username,first=first,last=last,email=email,phone=phone,created=created,accepted=accepted)
    else:
        newdata=[]
        eaccepted = manager.getAccepted(eventname)
        if int(eventname) > len(data):
            return render_template("error.html")
        newdata.append(data[int(eventname)-1])
        ##no button if user is not logged in
        button = "none"
        if 'username' in session:
            username = session['username']
            first = manager.getFirst(username)
            last = manager.getLast(username)
            email = manager.getEmail(username)
            phone = manager.getPhone(username)
            created = manager.getCreated(username)
            accepted= manager.getAccepted(username)
            if request.method == "POST":
                if "request" in request.form:
                    eventdata = manager.getEventData()
                    manager.makeRequest(eventname,username,eventdata[int(eventname)-1][3])
                    print username+" requests to join"
                if "cancel" in request.form:
                    manager.removeRequest(eventname,username)
                    print username+" cancels membership"
                if "leave" in request.form:
                    manager.remMember(eventname,username)
                    print username+" leaves event"
                    return redirect("/events/"+eventname)
            if manager.getThisEventData(eventname)[3]==username:
                button = "creator"
            else:
                button = "request"
                if username in eaccepted:
                    button = "leave"
                requested = manager.getRequesters(eventname)
                if username in requested:
                    button = "pending"
        return render_template('events.html', button = button, data=newdata, eaccepted=eaccepted,username=username,first=first,last=last,phone=phone,email=email, created=created, accepted=accepted)

@app.route("/edit",methods=['GET','POST'])
@app.route("/edit/<user>", methods=['GET', 'POST'])
@app.route("/edit/<user>/<field>", methods=['GET', 'POST'])

def editProfile(username=None,field=None):
    if user:
        if field:
            if 'username' in session:
                username = session['username']
                first = manager.getFirst(username)
                last = manager.getLast(username)
                email = manager.getEmail(username)
                phone = manager.getPhone(username)
                facebook = manager.getFacebook(username)
                created = manager.getCreated(username)
                accepted= manager.getAccepted(username)

                access = True
                if username == user:
                    if request.method == "POST":
                        #will finish later

                    
                    return render_template(access=access,username=username,first=first,last=last,email=email,phone=phone,facebook=facebook,created=created,accepted=accepted,field=field)
                else:
                    access = False
                    return render_template(access=access,username=username,first=first,last=last,email=email,phone=phone,created=created,accepted=accepted)

        else:
            return redirect("/profile/"+username)
    return redirect("/")

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "peep"
    app.run()
