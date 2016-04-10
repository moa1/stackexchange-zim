#!/usr/bin/python

# list all present attributes in a stackoverflow dump xml file.

import os
import lxml
from pysqlite2 import dbapi2 as sqlite3
from utils import *

def get_all_attributes(file,table):
    "Return the list of all attribute names the (XML) file has as row elements."
    parser = lxml.etree.XMLPullParser(events=('start', 'end'),tag="row")
    events = parser.read_events()

    all_keys = {}

    total_size=os.fstat(file.fileno()).st_size
    while True:
        buf=file.read(100000)
        buf_pos=file.tell()
        print "%s.xml %i / %i (%f%%)" % (table,buf_pos,total_size,100.0*buf_pos/total_size)
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

if __name__=="__main__":
    #tables=["Badges","PostHistory","Posts","Users","Comments","PostLinks","Tags","Votes"]
    tables=["Badges","Users","Posts","Comments","Tags"]

    table_attributes={}
    for table in tables:
        print table
        with open(stackexchange_dump_dir+"/"+table+".xml","r") as f:
            attributes=get_all_attributes(f,table)
            table_attributes[table]=attributes

    try:
        os.unlink(dbfile)
    except:
        pass
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()

    insert_table_attributes(cursor,table_attributes)

    # create each table with its attributes
    for table in tables:
        attributes=table_attributes[table]
        create_table(cursor,table,attributes)

    cursor.execute("create table PostsTags(PostId integer, TagId integer, primary key (PostId, TagId))")

    cursor.execute("create index Posts_OwnerUserId on Posts(OwnerUserId)")
    cursor.execute("create index Posts_ParentId on Posts(ParentId)")
    cursor.execute("create index Comments_PostId on Comments(PostId)")
    cursor.execute("create index Badges_UserId on Badges(UserId)")
    cursor.execute("create index Badges_Name on Badges(Name)")
    cursor.execute("create index PostsTags_TagId on PostsTags(TagId)")
    
    connection.close()
