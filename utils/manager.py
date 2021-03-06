import urllib
import urllib2
from datetime import datetime
from flask import Flask, render_template, request, session,redirect,url_for
import csv, unicodedata, requests, sqlite3

def check(val):
    if ("'" in val):
        temp = val.split("'");
        i = 0
        new = ""
        for a in temp:
            if i == 0:
                temp[i] = a+"'"
            elif i == len(temp)-1:
                temp[i] = "'"+a
            else:
                temp[i] = "'"+a+"'"
            new+=temp[i]
            i+=1
        return new
    else:
        return val

def getIDs():
    ids=[]
    conn = sqlite3.connect("databases/users.db")
    c = conn.cursor()
    c.execute("select * from uinfo")
    tabledata = c.fetchall()
    for d in tabledata:
        ids.append(d[0]);
        conn.close()
    ids[:]=[unicodedata.normalize('NFKD',o).encode('ascii','ignore') for o in ids]
    return ids

def getProfilePath():
    ids=getIDs()
    user=request.form["query"]
    path="profile/"+user
    return path

def validateEntry(entry):
    allowChars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890"
    specialChars="!#$%&*+,-./:;<=>?@\^_`|~"
    if len(entry)<4 or len(entry)>16:
        return "Invalid Length (4-16 characters)"
    for x in entry:
        if x not in allowChars and x not in specialChars:
            return "You can't use this character. Special characters allowed: " + specialChars
    return ""

def getItem(table,ovalue,oindex,rindex):
    conn = sqlite3.connect("databases/users.db")
    c = conn.cursor()
    command = "select * from '" + table +"'"
    c.execute(command)
    tabledata=c.fetchall()
    value = ""
    for d in tabledata:
        if ovalue==d[oindex]:
            value = d[rindex]
    conn.close()
    return value

def getFirst(n):
    first = getItem("uinfo",n,0,2)
    return first
        
def getLast(n):
    last = getItem("uinfo",n,0,3)
    return last
        
def getPhone(n):
    phone = getItem("uinfo",n,0,4)
    return phone

def getEmail(n):
    email = getItem("uinfo",n,0,5)
    return email
        
def getFacebook(n):
    facebook = getItem("uinfo",n,0,6)
    return facebook
        
def getDefaultPath(n):
    fid=""
    rfacebook=getFacebook(n)[::-1]
    for n in rfacebook:
        if (n == "/"):
            break
        else:
            fid = n +fid
    return fid

def userNotifTable(username):
    conn = sqlite3.connect('databases/notif.db')
    cursor = conn.cursor()
    command= "CREATE TABLE IF NOT EXISTS'" + username +"' (id integer primary key, sender text, piclink text, link text, msg text)"
    # Create table
    cursor.execute(command)
    # Insert a row of data
    conn.close()

def addEvent(datetime,event,user,desc,loc,time,tags):    
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "INSERT INTO events (datetime,eventname,username,description,location,time,tags,status) VALUES ('"+datetime+"','"+check(event)+"','"+user+"','"+check(desc)+"','"+check(loc)+"','"+time+"','"+check(tags)+"','Ongoing')"
    c.execute(command)
    conn.commit()
    c.execute("select id from events where eventname='"+check(event)+"' and datetime='"+datetime+"' and username='"+user+"'")
    data=c.fetchall()
    idnum= int(data[0][0])
    command = "CREATE TABLE IF NOT EXISTS '" + str(idnum) +"' (username text, date text)"
    c.execute(command)
    command = "INSERT INTO '"+str(idnum)+"' (username, date) values ('"+user+"','"+datetime+"')"
    c.execute(command)
    command = "CREATE TABLE IF NOT EXISTS '" + user +"' (event text)"
    c.execute(command)
    command = "insert into '"+user+"' (event) values ('"+str(idnum)+"')"
    c.execute(command)
    conn.commit()
    conn.close()

#date-time,eventname,username,description,location,time,tags    
def remEvent(eventid):
    event = getThisEventData(eventid)
    user = event[3]
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "UPDATE events set status='Removed' where id='"+str(eventid)+"'"
    c.execute(command)
    conn.commit()
    command = "drop table '"+str(eventid)+"'"
    c.execute(command)
    command = "delete  from '"+user+"' where event='"+eventid+"'"
    c.execute(command)
    conn.commit()
    conn.close()

##Get data of all events
def getEventData():
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from events"
    c.execute(command)
    tabledata=c.fetchall()
    conn.close()
    return tabledata

##Get data of one event
def getThisEventData(eventid):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from 'events' where id='"+str(eventid)+"'"
    c.execute(command)
    data=c.fetchall()
    conn.close()
    if len(data) < 1:
        return []
    return data[0]

##Get the event name
def getEvent(eventid):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select eventname from 'events' where id='"+str(eventid)+"'"
    c.execute(command)
    data=c.fetchall()
    conn.close()
    return data

def size():
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from 'events'"
    c.execute(command)
    data=c.fetchall()
    conn.close()
    return len(data)

##check if event is passed
def expired(eventid):
    expired = False

    when = getThisEventData(eventid)[6]
    date = when.split(" ")[0]

    month = date.split("-")[1]
    day = date.split("-")[2]
    year = date.split("-")[0]

    time = when.split(" ")[1]
    hour = time.split(":")[0]
    minute = time.split(":")[1]

    ndate = str(datetime.now().strftime('%Y-%m-%d'))
    nmonth = ndate.split("-")[1]
    nday = ndate.split("-")[2]
    nyear = ndate.split("-")[0]

    ntime = str(datetime.now().time())
    nhour = ntime.split(":")[0]
    nminute = ntime.split(":")[1]

    if int(nyear) > int(year):
        expired = True
    elif int(nyear) == int(year):
        if int(nmonth) > int(month):
            expired = True
        elif int(nmonth) == int(month):
            if int(nday) > int(day):
                expired = True                
            elif int(nday) == int(day):
                if int(nhour) > int(hour):
                    expired = True                
                elif int(nhour) == int(hour):
                    if int(nminute) > int(minute):
                        expired = True  
  
    return expired

def expireEvent(eventid):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "UPDATE events set status='Expired' where id='"+str(eventid)+"'"
    c.execute(command)
    conn.commit()
    conn.close()

def unexpireEvent(eventid):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "UPDATE events set status='Ongoing' where id='"+str(eventid)+"'"
    c.execute(command)
    conn.commit()
    conn.close()
        
def eventSearch(keyword, keyloc):
    data = getOngoingEvents()
    res = []
    for e in data:
        if not expired(e[0]):
            if keyword == "" and keyloc == "":
                res.append(e)
            elif keyword != "" and keyloc == "":
                tags = e[7].split("#")
                name = e[2].split(' ')
                desc = e[4].split(" ")
                
                for n in name:
                    if ( keyword.lower() in n.lower() and len(keyword) >= len(n)*.5):
                        res.append(e)
                for t in tags:
                    ##really bad search. Please edit.
                    if ( keyword.lower() in t.lower() and len(keyword) >= len(t)*.5 
                         and e not in res ):
                        res.append(e)
                for d in desc:
                    if ( keyword.lower() in d.lower() and len(keyword) >= len(d)*.5 
                         and e not in res ):
                        res.append(e)
            elif keyloc != "" and keyword == "":
                if ( keyloc.lower() in e[5].lower() and e not in res ): 
                    res.append(e)
            else:
                tags = e[7].split("#")
                name = e[2].split(' ')
                desc = e[4].split(" ")
                
                for n in name:
                    if ( keyword.lower() in n.lower() and len(keyword) >= len(n)*.5) and keyloc.lower() in e[5].lower():
                        res.append(e)
                for t in tags:
                    ##really bad search. Please edit.
                    if ( keyword.lower() in t.lower() and len(keyword) >= len(t)*.5 and keyloc.lower() in e[5].lower() and e not in res ):
                        res.append(e)
                for d in desc:
                    if ( keyword.lower() in d.lower() and len(keyword) >= len(d)*.5 and keyloc.lower() in e[5].lower() and e not in res ):
                        res.append(e)

                    
    return res

def getCreated(username):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from 'events' where username='"+username+"' AND (status='Ongoing' OR status='Expired')"
    c.execute(command)
    created = c.fetchall()
    conn.commit()
    conn.close()
    return created

def getPending(username):
    conn = sqlite3.connect("databases/requests.db")
    c = conn.cursor()
    command = "select * from 'requests' where sender='"+username+"'"
    c.execute(command)
    pending = c.fetchall()
    conn.commit()
    conn.close()
    return pending

##get requests directed at this user
def getRequests(username):
    conn = sqlite3.connect("databases/requests.db")
    c = conn.cursor()
    command = "select * from 'requests' where receiver='"+username+"'"
    c.execute(command)
    tabledata=c.fetchall()
    return tabledata

##get requests on this event
def getEventRequests(eventid):
    conn = sqlite3.connect("databases/requests.db")
    c = conn.cursor()
    command = "select * from 'requests'"
    c.execute(command)
    tabledata=c.fetchall()
    results = []
    for data in tabledata:
        if data[1]==int(eventid):
            results.append(data)
    return results

def makeRequest(eventid,username,host):
    conn = sqlite3.connect("databases/requests.db")
    c = conn.cursor()
    command = "insert into 'requests' (eventid, sender, receiver) values ("+eventid+",'"+username+"','"+host+"')"
    data = getEventRequests(eventid)
    add = True
    for r in data:
        if r[2]==username:
            add = False
            break
    if add:
        c.execute(command)
        conn.commit()
    conn.close()

def getRequesters(eventid):
    requests = getEventRequests(eventid)
    requesters = []
    for r in requests:
        requesters.append(r[2])
    return requesters

def removeRequest(eventid, username):
    conn = sqlite3.connect("databases/requests.db")
    c = conn.cursor()
    command = "delete from 'requests' where sender='"+username+"' and eventid="+eventid
    c.execute(command)
    conn.commit()
    conn.close()

def addMember(eventid, username):
    conn=sqlite3.connect("databases/events.db")
    c = conn.cursor()
    dtime = datetime.now().strftime('%Y-%m-%d')
    command = "insert into '"+str(eventid)+"' (username, date) values ('"+username+"','"+dtime+"')"
    c.execute(command)
    command = "CREATE TABLE IF NOT EXISTS '" + username +"' (event text)"
    c.execute(command)
    command = "insert into '"+username+"' (event) values ('"+str(eventid)+"')"
    c.execute(command)
    conn.commit()
    conn.close()

def remMember(eventid, username):
    conn=sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "delete from '"+str(eventid)+"' where username='"+username+"'"
    c.execute(command)
    command = "delete from '"+username+"' where event='"+str(eventid)+"'"
    c.execute(command)
    conn.commit()
    conn.close()

def getOngoingEvents():
    conn=sqlite3.connect("databases/events.db")
    c=conn.cursor()
    command="select * from events where status='Ongoing'"
    c.execute(command)
    events = c.fetchall()
    conn.close()
    return events

def getRemovedEvents():
    conn=sqlite3.connect("databases/events.db")
    c=conn.cursor()
    command="select * from events where status='Removed'"
    c.execute(command)
    events = c.fetchall()
    conn.close()
    return events

def updateExpired():
    temp = getOngoingEvents()
    for a in temp:
        if expired(a[0]):
            expireEvent(int(a[0]))

def removeExpired(events):
    temp = []
    for a in events:
        try:
            isInt = int(a)
        except TypeError:
            isInt = 0
        if isInt:
            if not expired(a):
                temp.append(a)
        else:
            if not expired(a[0]):
                temp.append(a)
    return temp

def getAccepted(username):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "CREATE TABLE IF NOT EXISTS '" + username +"' (event)"
    c.execute(command)
    command = "select * from '"+username+"'"
    c.execute(command)
    events = getEventData()
    tabledata=c.fetchall()
    accepted = []
    for data in tabledata:
        if events[int(data[0])-1][8]=="Ongoing":
            accepted.append(int(data[0]))
        elif events[int(data[0])-1][8]=="Removed":
            command = "delete from '"+username+"' where event='"+str(int(data[0]))+"'"
            c.execute(command)
            conn.commit()
    return accepted

def getAcceptedPast(username):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "CREATE TABLE IF NOT EXISTS '" + username +"' (event)"
    c.execute(command)
    command = "select * from '"+username+"'"
    c.execute(command)
    tabledata=c.fetchall()
    events = getEventData()
    pastaccepted = []
    for x in tabledata:
        if events[int(x[0])-1][8]=="Expired":
            pastaccepted.append(x[0])
    return pastaccepted

def getEventAccepted(eventid):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from '"+str(eventid)+"'"
    c.execute(command)
    tabledata=c.fetchall()
    accepted = []
    for a in tabledata:
        accepted.append(a[0])
    return accepted

def getEventAcceptedFB(eventid):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from '"+str(eventid)+"'"
    c.execute(command)
    tabledata=c.fetchall()
    fb = []
    for a in tabledata:
        fb.append(getDefaultPath(a[0]))
    return fb

def updateName(username,first,last):
    conn=sqlite3.connect("databases/users.db")
    c = conn.cursor()
    command = "update uinfo set first='"+first+"',last='"+last+"' where username='"+username+"'"
    c.execute(command)
    conn.commit()
    conn.close()

def updatePhone(username,phone):
    conn=sqlite3.connect("databases/users.db")
    c = conn.cursor()
    command = "update uinfo set phone='"+phone+"' where username='"+username+"'"
    c.execute(command)
    conn.commit()
    conn.close()

def updateEmail(username,email):
    conn=sqlite3.connect("databases/users.db")
    c = conn.cursor()
    command = "update uinfo set email='"+email+"' where username='"+username+"'"
    c.execute(command)
    conn.commit()
    conn.close()

def updateFacebook(username,facebook):
    conn=sqlite3.connect("databases/users.db")
    c = conn.cursor()
    command = "update uinfo set facebook='"+facebook+"' where username='"+username+"'"
    c.execute(command)
    conn.commit()
    conn.close()

def updateEvent(event,name,location,description,tags,date):
    conn=sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "update events set eventname='"+name+"',description='"+description+"',location='"+location+"',tags='"+tags+"',time='"+date+"' where id='"+event+"'"
    c.execute(command)
    conn.commit()
    conn.close()
    if not expired(event):
        unexpireEvent(event)

def getTags(eventid):
    event  = getThisEventData(str(eventid))
    tagstring = str(event[7])
    tags = tagstring.split(" ")
    for a in tags:
        a.strip(',')
    return tags

def getAllTags():
    events = getEventData()
    tags = []
    for e in events:
        ind = int(e[0])
        tags.append(getTags(ind))
    return tags

def getEventByTag(tag):
    tagevents = []
    events = getEventData()
    for a in events:
        if tag in getTags(int(a[0])):
            tagevents.append(a)
    return tagevents
