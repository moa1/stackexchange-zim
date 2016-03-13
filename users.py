#!/usr/bin/python
# -*- coding:utf-8 -*-

# TODO: make that HTML <code> is rendered with a grey background.

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import pickle

#user["AboutMe"]=unescape_html(user["AboutMe"],True)

def select_user(cursor, Id):
    cursor.execute('select * from Users where Id=?', (Id,))
    user=cursor.fetchone()

    cursor.execute('select * from Posts where OwnerUserId=? and PostTypeId="1"', (Id,))
    user["questions"]=cursor.fetchall()
    user["questions_count"]=len(user["questions"])
        
    cursor.execute('select Id,ParentId from Posts where OwnerUserId=? and PostTypeId="2"', (Id,))
    user["answers"]=cursor.fetchall()
    user["answers_count"]=len(user["answers"])
    for row in user["answers"]:
        cursor.execute('select Id,Title from Posts where Id=?',(row["ParentId"],))
        question=cursor.fetchone()
        row["QuestionId"]=question["Id"]
        row["QuestionTitle"]=question["Title"]

    cursor.execute('select (select Id from Tags where ExcerptPostId=Posts.Id or WikiPostId=Posts.Id) as Id, (select TagName from Tags where ExcerptPostId=Posts.Id or WikiPostId=Posts.Id) as TagName from Posts where OwnerUserId=? and PostTypeId in ("4","5") and TagName not NULL', (Id,))
    user["tags"]=cursor.fetchall()
    user["tags"].sort(key=lambda x:x["TagName"])
    user["tags_count"]=len(user["tags"])

    return user

user_template=pystache.parse(u"""
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>User {{DisplayName}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<h1>User {{DisplayName}}</h1>
<div class=\"user\">{{DisplayName}}</div>
Creation: <div class=\"date\">{{CreationDate}}</div>
<p>Reputation: {{Reputation}}</p>
<p>Homepage: <a href="{{WebsiteUrl}}">{{WebsiteUrl}}</a></p>
<p>Location: {{Location}}</p>
<p>Age: {{Age}}</p>
<p>Up votes: {{UpVotes}} Down votes: {{DownVotes}}</p>
<p><a href="#questions">Questions: {{questions_count}}</a> <a href="#answers">Answers: {{answers_count}}</a> <a href="#tags">Tags: {{tags_count}}</a></p>
<h2>About Me</h2>
{{{AboutMe}}}
<h2>My {{questions_count}} questions<a class="internallink" name="questions" href="#questions">¶</a></h2>
{{#questions}}
<p><a href="post{{Id}}.html">{{Title}}</a></p>
{{/questions}}
<h2>My {{answers_count}} answers<a class="internallink" name="answers" href="#answers">¶</a></h2>
{{#answers}}
<p><a href="post{{QuestionId}}.html#{{Id}}">{{QuestionTitle}}</a></p>
{{/answers}}
<h2>My {{tags_count}} tags<a class="internallink" name="tags" href="#tags">¶</a></h2>
{{#tags}}
<p><a href="tag{{Id}}.html">{{TagName}}</a></p>
{{/tags}}
  </body>
</html>""")

def render_user_home(user):
    user_html=pystache.render(user_template,user)
    return user_html

def make_users_html(limit=None):
    if limit:
        cursor.execute('select Id from Users limit '+str(limit))
    else:
        cursor.execute('select Id from Users')
    user_ids = [row["Id"] for row in cursor]
    max_Id=max(user_ids)
    for user_id in user_ids:
        user=select_user(cursor, user_id)
        print "User",user["Id"],"/",max_Id

        with codecs.open(tempdir+"content/user"+str(user["Id"])+".html", "w", "utf-8") as f:
            f.write(render_user_home(user))

(connection,cursor)=init_db()

with connection:
    #import profile
    #profile.run("make_users_html()")
    make_users_html()
