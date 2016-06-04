#!/usr/bin/python

# list all present attributes in a stackoverflow dump xml file.

import os
import lxml
from pysqlite2 import dbapi2 as sqlite3
from utils import *
import sys
import codecs

def get_all_attributes(file,tables):
    "Return the list of all attribute names the (XML) file has as row elements."
    parser = lxml.etree.XMLPullParser(events=('start', 'end'),encoding="UTF-8")
    events = parser.read_events()

    table_attributes = {}

    #total_size=os.fstat(file.fileno()).st_size
    table=None
    block_size=100000
    buf_pos=0
    skip=True
    while True:
        buf=file.read(block_size)
        buf_pos+=block_size
        #buf_pos=file.tell()
        #print "create %s.xml %i / %i (%f%%)" % (table,buf_pos,total_size,100.0*buf_pos/total_size)
        print "create %s.xml %i" % (table,buf_pos)
        if buf=="":
            break
        parser.feed(buf)
        for action, elem in events:
            if action=="start":
                if elem.tag in tables.keys():
                    table=tables[elem.tag]
                    table_attributes[table]=dict()
                    skip=False
                elif elem.tag=="row":
                    pass
                else:
                    table=None
                    skip=True
            elif action=="end":
                if elem.tag=="row" and not skip:
                    row={}
                    for name, value in elem.items():
                        table_attributes[table][name]=True
                elem.clear()

    root = parser.close()

    keys=dict()
    for table in table_attributes:
        k = table_attributes[table].keys()
        k.sort()
        keys[table]=k
    return keys

def get_all_attributes_precomputed():
    a=dict()
    a["Comments"]=["CreationDate","Id","PostId","Score","Text","UserDisplayName","UserId"]
    a["Posts"]=["AcceptedAnswerId","AnswerCount","Body","ClosedDate","CommentCount","CommunityOwnedDate","CreationDate","FavoriteCount","Id","LastActivityDate","LastEditDate","LastEditorDisplayName","LastEditorUserId","OwnerDisplayName","OwnerUserId","ParentId","PostTypeId","Score","Tags","Title","ViewCount"]
    a["Users"]=["AboutMe","AccountId","Age","CreationDate","DisplayName","DownVotes","Id","LastAccessDate","Location","ProfileImageUrl","Reputation","UpVotes","Views","WebsiteUrl"]
    a["Badges"]=["Class","Date","Id","Name","TagBased","UserId"]
    a["Tags"]=["Count","ExcerptPostId","Id","TagName","WikiPostId"]
    return a

def create_table(cursor, table_name, attributes):
    primary_key="Id"
    attributes = [a for a in attributes if a!=primary_key]
    statement="create table "+table_name+"("+primary_key+" integer primary key" +"".join([", "+a+" text" for a in attributes])+")"
    print statement
    cursor.execute(statement)

if __name__=="__main__":
    if len(sys.argv)!=1:
        print "Syntax: cat DUMP-FILE-TO-CREATE-TABLES-FOR.XML | ",sys.argv[0]
        sys.exit(1)
    
    tables={"badges":"Badges","users":"Users","posts":"Posts","comments":"Comments","tags":"Tags"}

    #with open(stackexchange_dump_dir+"/"+table+".xml","r") as f:
    #    table_attributes=get_all_attributes(f,tables)
    
    #table_attributes=get_all_attributes(sys.stdin,tables)
    
    table_attributes=get_all_attributes_precomputed()

    try:
        os.unlink(dbfile)
    except:
        pass
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()

    insert_table_attributes(cursor,table_attributes)

    # create each table with its attributes
    for table in table_attributes:
        attributes=table_attributes[table]
        create_table(cursor,table,attributes)

    connection.close()
