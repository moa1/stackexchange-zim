#!/usr/bin/python
# -*- coding:utf-8 -*-

# list all present attributes in a stackoverflow dump xml file.

from utils import *

def parse_tags(Tags):
    # Given Tags in the form "<tag 1><tag 2>...", return the list of tags.
    if Tags==u"éjavascriptà": #hack fix for stackoverflow.com, version 20160301, Post Id=310914
        Tags="<javascript>"
    s = Tags.split(">")
    l = []
    if s[-1]!="":
        print 's[-1] should be "",but is',s[-1],'for Tags=',Tags
    assert s[-1]==""
    for e in s[:-1]:
        if e[0]!="<":
            print 'e[0] should be "<",but is',e[0],'for Tags=',Tags
        assert e[0]=="<"
        l.append(e[1:])
    return l

def fill_tag_table(connection):
    cursor=connection.cursor()
    print "selecting"
    #cursor.execute('select Id from Posts where Tags NOT NULL and Id=310914')
    cursor.execute('select Id from Posts where Tags NOT NULL')
    print "fetching"
    post_ids = [row["Id"] for row in cursor]
    print "computing maximum id"
    max_Id=max(post_ids)
    print "start"
    i=0
    for post_id in post_ids:
        i+=1
        print "PostsTags",post_id,"/",max_Id
        cursor.execute('select Tags from Posts where Id=?',(post_id,))
        tags=cursor.fetchone()["Tags"]
        parsed_tags=parse_tags(tags)
        for tag in parsed_tags:
            cursor.execute('select Id from Tags where TagName=?', (tag,))
            tag_id=cursor.fetchone()["Id"]
            cursor.execute('insert into PostsTags(PostId,TagId) values (?,?)', (post_id,tag_id))

(connection,cursor)=init_db()

with connection:
    fill_tag_table(connection)

#fill_tag_table(connection)
