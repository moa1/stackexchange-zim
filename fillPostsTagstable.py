#!/usr/bin/python

# list all present attributes in a stackoverflow dump xml file.

from utils import *

def parse_tags(Tags):
    # Given Tags in the form "<tag 1><tag 2>...", return the list of tags.
    s = Tags.split(">")
    l = []
    assert s[-1]==""
    for e in s[:-1]:
        assert e[0]=="<"
        l.append(e[1:])
    return l

def fill_tag_table(connection):
    cursor=connection.cursor()
    cursor.execute('select Id,Tags from Posts where Tags NOT NULL')
    rows=cursor.fetchall()
    max_Id=max([row["Id"] for row in rows])
    for row in rows:
        post_id=row["Id"]
        print "PostsTags",post_id,"/",max_Id
        tags=row["Tags"]
        parsed_tags=parse_tags(tags)
        for tag in parsed_tags:
            cursor.execute('select Id from Tags where TagName=?', (tag,))
            tag_id=cursor.fetchone()["Id"]
            cursor.execute('insert into PostsTags(PostId,TagId) values (?,?)', (post_id,tag_id))

(connection,cursor)=init_db()

with connection:
    fill_tag_table(connection)
