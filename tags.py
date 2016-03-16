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
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="tag{{Id}}.html">Next Tag</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="tag{{Id}}.html">Prev Tag</a>{{/PrevPage}}
<a class="internallink" href="index_tags.html">Tags Index</a>
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="index_questions.html">Questions Index</a>
</div>
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

{{/WikiPost}}
<h2>{{Count}} Questions with tag &lt;{{TagName}}&gt;</h2>
{{#questions}}
<p><a class="internallink" href="question{{Id}}.html">{{Title}}</a></p>
{{/questions}}
  </body>
</html>
""")

def render_tag(cursor,Id,PrevId,NextId):
    cursor.execute('select * from Tags where Id=?', (Id,))
    tag=cursor.fetchone()

    cursor.execute('select * from Tags where Id=?', (PrevId,))
    tag["PrevPage"]=cursor.fetchone()
    cursor.execute('select * from Tags where Id=?', (NextId,))
    tag["NextPage"]=cursor.fetchone()

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
    tag_ids = [row["Id"] for row in cursor]
    max_tag_id=max(tag_ids)
    len_tag_ids=len(tag_ids)
    for (i,tag_id) in enumerate(tag_ids):
        print "Tag",tag_id,"/",max_tag_id

        with codecs.open(tempdir+"content/tag"+str(tag_id)+".html", "w", "utf-8") as f:
            prev_tag_id=tag_ids[(i-1)%len_tag_ids]
            next_tag_id=tag_ids[(i+1)%len_tag_ids]
            f.write(render_tag(cursor, tag_id, next_tag_id, prev_tag_id))


(connection,cursor)=init_db()

with connection:
    print "Tags"
    make_tags_html()
