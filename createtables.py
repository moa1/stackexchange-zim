#!/usr/bin/python

# list all present attributes in a stackoverflow dump xml file.

import sys
import os
from lxml import etree
from pysqlite2 import dbapi2 as sqlite3
from utils import *
import pickle

def get_all_attributes(file):
    "Return the list of all attribute names the (XML) file has as row elements."
    parser = etree.XMLPullParser(events=('start', 'end'),tag="row")
    events = parser.read_events()

    all_keys = {}

    while True:
        buf=file.read(100000)
        if buf=="":
            break
        parser.feed(buf)
        for action, elem in events:
            if action=="end":
                row={}
                for name, value in elem.items():
                    all_keys[name]=True
                elem.clear()

    root = parser.close()

    keys = all_keys.keys()
    keys.sort()
    return keys

def create_table(cursor, table_name, attributes):
    primary_key="Id"
    attributes = [a for a in attributes if a!=primary_key]
    statement="create table "+table_name+"("+primary_key+" integer primary key" +"".join([", "+a+" text" for a in attributes])+")"
    print statement
    cursor.execute(statement)

#tables=["Badges","PostHistory","Posts","Users","Comments","PostLinks","Tags","Votes"]
tables=["Users","Posts","Comments","Tags"]

table_attributes={}
for table in tables:
    print table
    with open(stackexchange_dump_path+"/"+table+".xml","r") as f:
        attributes=get_all_attributes(f)
        table_attributes[table]=attributes

with open(tempdir+"table_attributes.pickle","w") as f:
    pickle.dump(table_attributes,f)

try:
    os.unlink(dbfile)
except:
    pass
conn = sqlite3.connect(dbfile)
cursor = conn.cursor()

for table in tables:
    attributes=table_attributes[table]
    create_table(cursor,table,attributes)

cursor.execute("create table PostsTags(PostId integer, TagId integer, primary key (PostId, TagId))")

cursor.execute("create index Posts_OwnerUserId on Posts(OwnerUserId)")
cursor.execute("create index Posts_ParentId on Posts(ParentId)")
cursor.execute("create index Comments_PostId on Comments(PostId)")
    
conn.close()
