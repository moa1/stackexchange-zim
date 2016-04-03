#!/usr/bin/python

from config import *
from createtables import *
from filltables import *
from pysqlite2 import dbapi2 as sqlite3
import utils

dbfile=tempdir+"/sites.sqlite3"

try:
    os.unlink(dbfile)
except:
    pass
connection = sqlite3.connect(dbfile)    

table_attributes={}
try:
    with open(sites_xml,"r") as f:
        attributes=get_all_attributes(f,"Sites")
except IOError:
    attributes=[]

with connection:
    create_table(connection,"Sites",attributes)

try:
    #codec "utf-8-sig" removes the BOM if present, which is required for lxml
    with codecs.open(sites_xml, "r", "utf-8-sig") as f:
        with connection:
            fill_table(f,"Sites",attributes,connection)
except IOError:
    pass

connection.close()
