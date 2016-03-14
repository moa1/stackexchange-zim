#!/usr/bin/python
# -*- coding:utf-8 -*-

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import pickle

tag_template=pystache.parse(u"""<!DOCTYPE html>
<html>
  <head>
    <title>{{TagName}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
  <body>
<h1>Tag &lt;{{TagName}}&gt;</h1>
{{#ExcerptPost}}

<h2>Excerpt</h2>
<div class=\"excerpt body\">{{{Body}}}</div>
{{{OwnerUser_html}}}
{{{LastEditorUser_html}}}
<div class=\"postdate\">{{LastActivityDate}}</div>
{{#comments}}
<div class=\"comment container\">{{{User_html}}}{{{Text}}}</div>
{{/comments}}
</div>

{{/ExcerptPost}}
{{#WikiPost}}

<h2>Wiki</h2>
<div class=\"wiki body\">{{{Body}}}</div>
{{{OwnerUser_html}}}
{{{LastEditorUser_html}}}
<div class=\"postdate\">{{LastActivityDate}}</div>
{{#comments}}
<div class=\"comment container\">{{{User_html}}}{{{Text}}}</div>
{{/comments}}
</div>

{{/WikiPost}}
<h2>Questions with tag &lt;{{TagName}}&gt;</h2>
{{#questions}}
<p><a class="internallink" href="post{{Id}}.html">{{Title}}</a></p>
{{/questions}}
  </body>
</html>
""")

def render_tag(cursor,Id):
    cursor.execute('select * from Tags where Id=?', (Id,))
    tag=cursor.fetchone()

    excerpt_post_id=tag["ExcerptPostId"]
    if excerpt_post_id:
        tag["ExcerptPost"]=select_post(cursor,int(excerpt_post_id))
    wiki_post_id=tag["WikiPostId"]
    if wiki_post_id:
        tag["WikiPost"]=select_post(cursor,int(wiki_post_id))

    cursor.execute('select * from Posts where Id in (select PostId from PostsTags where TagId=?)', (Id,))
    tag["questions"]=cursor.fetchall()

    tag_html=pystache.render(tag_template,tag)
    return tag_html

def make_tags_html():
    cursor.execute('select Id from Tags')
    Ids = [row["Id"] for row in cursor]
    max_Id=max(Ids)
    for Id in Ids:
        print "Tag",Id,"/",max_Id

        with codecs.open(tempdir+"content/tag"+str(Id)+".html", "w", "utf-8") as f:
            f.write(render_tag(cursor, Id))


(connection,cursor)=init_db()

with connection:
    print "Tags"
    make_tags_html()
