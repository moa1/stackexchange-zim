#!/usr/bin/python
# -*- coding: utf-8 -*-"

from lxml import etree
from pysqlite2 import dbapi2 as sqlite3
from utils import *
import codecs
import pickle

import sys #debug

def fill_table(xmlfile, table, attributes,connection):
    parser = etree.XMLPullParser(events=('start', 'end'),tag="row")
    events = parser.read_events()

    attributes=[a for a in attributes if a!="Id"]
    attributes=["Id"]+attributes

    statement="insert into %s(%s) values (%s)" % \
        (table, ",".join(attributes), ",".join(":"+a for a in attributes))
    print statement
    
    while True:
        buf=xmlfile.read(100000)
        if buf=="":
            break
        parser.feed(buf)
        for action, elem in events:
            if action=="end":
                row={}
                for a in attributes:
                    row[a]=None
                for name, value in elem.items():
                    row[name]=value
                row["Id"]=int(row["Id"])
                #print row
                connection.execute(statement, row)
                print row["Id"]
                elem.clear()

    root = parser.close()
    #print etree.tostring(root)

xml_directory="/home/itoni/Downloads/stackexchange-to-zim-converter/blender.stackexchange.com/"

f=open(tempdir+"table_attributes.pickle","r")
table_attributes=pickle.load(f)
f.close()

connection = sqlite3.connect(dbfile)

#tables=["Badges","PostHistory","Posts","Users","Comments","PostLinks","Tags","Votes"]
tables=["Users","Posts","Comments"]

for table in tables:
    #codec "utf-8-sig" removes the BOM if present, which is required for lxml
    f=codecs.open(xml_directory+table+".xml", "r", "utf-8-sig")

    with connection:
        fill_table(f,table,table_attributes[table],connection)
