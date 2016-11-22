#!/usr/bin/python
# -*- coding: utf-8 -*-"

import os
import parsexml
from pysqlite2 import dbapi2 as sqlite3
from utils import *
import sys
import codecs

def fill_table(file, tables, table_attributes, connection):
    parser=parsexml.XMLParser()
    
    statement=dict()
    for table in tables.values():
        attributes=table_attributes[table]
        statement[table]="insert into %s(%s) values (%s)" % \
            (table, ",".join(attributes), ",".join(":"+a for a in attributes))

    #total_size=os.fstat(file.fileno()).st_size
    table=None
    block_size=100000
    buf_pos=0
    skip=True
    while True:
        buf=file.read(block_size)
        buf_pos+=block_size
        #buf_pos=file.tell()
        #print "fill %s.xml %i / %i (%f%%)" % (table,buf_pos,total_size,100.0*buf_pos/total_size)
        print "fill %s.xml %i" % (table,buf_pos)
        if buf=="":
            break

        events=parser.parse(buf)
        for (action,tag,attributes) in events:
            if action=="start":
                if tag in tables.keys():
                    table=tables[tag]
                    print statement[table]
                    skip=False
                elif tag=="row":
                    pass
                else:
                    table=None
                    skip=True
            elif action=="end":
                if tag=="row" and not skip:
                    row={}
                    for a in table_attributes[table]:
                        row[a]=None
                    for name, value in attributes.items():
                        row[name]=value
                    row["Id"]=int(row["Id"])
                    #print row
                    connection.execute(statement[table], row)
                    #print "Insert",table,row["Id"]
                    
if __name__=="__main__":
    if len(sys.argv)!=1:
        print "Syntax: cat DUMP-FILE-TO-CREATE-TABLES-FOR.XML | ",sys.argv[0]
        sys.exit(1)

    print "connecting to database",dbfile
    connection = sqlite3.connect(dbfile)

    table_attributes=get_table_attributes(connection)

    tables={"badges":"Badges","users":"Users","posts":"Posts","comments":"Comments","tags":"Tags"}

    with connection:
        fill_table(sys.stdin,tables,table_attributes,connection)
