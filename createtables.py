#!/usr/bin/python

# list all present attributes in a stackoverflow dump xml file.

import sys
import os
from lxml import etree
from pysqlite2 import dbapi2 as sqlite3
from utils import *
import pickle

def get_all_attributes(file):
    tree = etree.parse(file)
    root = tree.getroot()

    all_keys = {}

    for row in root:
        keys = row.keys()
        for key in keys:
            all_keys[key] = True
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
tables=["Users","Posts","Comments"]

try:
    os.unlink(dbfile)
except:
    pass
conn = sqlite3.connect(dbfile)
cursor = conn.cursor()

table_attributes={}
for table in tables:
    f=open("/home/itoni/Downloads/stackexchange-to-zim-converter/blender.stackexchange.com/"+table+".xml","r")
    attributes=get_all_attributes(f)
    create_table(cursor,table,attributes)
    table_attributes[table]=attributes

cursor.execute("create index Posts_OwnerUserId on Posts(OwnerUserId)")
cursor.execute("create index Posts_ParentId on Posts(ParentId)")
cursor.execute("create index Comments_PostId on Comments(PostId)")
    
f=open(tempdir+"table_attributes.pickle","w")
pickle.dump(table_attributes,f)
f.close()
