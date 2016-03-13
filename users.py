#!/usr/bin/python

# TODO: make that HTML <code> is rendered with a grey background.

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import pickle

#user["AboutMe"]=unescape_html(user["AboutMe"],True)

def select_user(cursor, Id):
    cursor.execute('select * from Posts where OwnerUserId=? and PostTypeId="1"', (Id,))
    questions=cursor.fetchall()
    for q in questions: q["html_file"]="post%i.html" % q["Id"]
    cursor.execute('select * from Posts where Id in (select ParentId from Posts where OwnerUserId=? and PostTypeId="2")', (Id,))
    answers=cursor.fetchall()
    for a in answers: a["html_file"]="post%i.html" % a["Id"]

    cursor.execute('select * from Users where Id=?', (Id,))
    user=cursor.fetchone()
    user["questions"]=questions
    user["answers"]=answers
    return user

def render_user(user):
    site_template=pystache.parse(u"""
<html>
  <head>
    <title>User {{DisplayName}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<p>
User: {{DisplayName}}
<div class=\"user\">{{DisplayName}}</div>
Creation: <div class=\"date\">{{CreationDate}}</div>
</p>
<p>Reputation: {{Reputation}}</p>
<p>Homepage: <a href="{{WebsiteUrl}}">{{WebsiteUrl}}</a></p>
<p>Location: {{Location}}</p>
<p>Up votes: {{UpVotes}} Down votes: {{DownVotes}}</p>
<strong>About Me:</strong>
{{{AboutMe}}}
<p>
<strong>My questions:</strong>
{{#questions}}
<p><a href="{{{html_file}}}">{{Title}}</a></p>
{{/questions}}
</p>
<p>
<strong>My answers:</strong>
{{#answers}}
<p><a href="{{{html_file}}}">{{Title}}</a></p>
{{/answers}}
</p>
  </body>
</html>
""")
    #TODO: replace link "post1.html" above with the list of questions/answers that the user created.
    site_html=pystache.render(site_template,user)
    return site_html


def make_users_html(limit=None):
    if limit:
        cursor.execute('select Id from Users limit '+str(limit))
    else:
        cursor.execute('select Id from Users')
    user_ids = [row["Id"] for row in cursor]
    for user_id in user_ids:
        user=select_user(cursor, user_id)
        print user["Id"]

        f=codecs.open(tempdir+"content/user"+str(user["Id"])+".html", "w", "utf-8")
        f.write(render_user(user))
        f.close()

(connection,cursor)=init_db()

#import profile
#profile.run("make_users_html()")
make_users_html()
