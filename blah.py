import sqlite3
from utils import manager

conn=sqlite3.connect('databases/events.db')
c = conn.cursor()

command = manager.addEvent("2015-05-06 12:29:36","Testing","TLiang518","This should be a working event","Stuyvesant High School", "7th Period", "#yoloswag #peep")
c.execute(command)
conn.close()
