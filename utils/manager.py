import urllib
import urllib2
from datetime import datetime
from flask import Flask, render_template, request, session,redirect,url_for
import csv, unicodedata, requests, sqlite3

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
    print path
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
    print command
    cursor.execute(command)
    # Insert a row of data
    conn.close()

def addEvent(datetime,event,user,desc,loc,time,tags):    
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "INSERT INTO 'events' (datetime,eventname,username,description, location, time, tags) VALUES ('"+datetime+"','"+event+"','"+user+"','"+desc+"','"+loc+"','"+time+"','"+tags+"')"
    c.execute(command)
    conn.close()

#date-time,eventname,username,description,location,time,tags    
def remEvent(datetime,event,user):
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "DELETE FROM 'events' WHERE datetime='" + datetime + "' AND eventname='"+event+"' AND username='"+user+"'"
    c.execute(command)
    conn.close()

def getEventData():
    conn = sqlite3.connect("databases/events.db")
    c = conn.cursor()
    command = "select * from events"
    c.execute(command)
    tabledata=c.fetchall()
    conn.close()
    return tabledata
