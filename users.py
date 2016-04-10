#!/usr/bin/python
# -*- coding:utf-8 -*-

from utils import *
import codecs
import rewriteurl
import templates

def select_user_home(cursor, Id, PrevUserId, NextUserId):
    user=select_user(cursor, Id)
    user["PrevPage"]={"Id":PrevUserId}
    user["NextPage"]={"Id":NextUserId}
    if user["AboutMe"]:
        user["AboutMe"]=rewriteurl.rewrite_urls_in_html(cursor,user["AboutMe"],stackexchange_domain)
    def get_badges(badgeclass):
        cursor.execute('select * from Badges where UserId=? and Class=? order by Name,Date desc', (Id,badgeclass))
        res=cursor.fetchall()
        for badge in res:
            badge["RenderDate"]=make_Date(badge["Date"])
        return res
    user["badgesclass1"]=get_badges("1")
    user["badgesclass2"]=get_badges("2")
    user["badgesclass3"]=get_badges("3")

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

    cursor.execute('select distinct (select Id from Tags where ExcerptPostId=Posts.Id or WikiPostId=Posts.Id) as Id, (select TagName from Tags where ExcerptPostId=Posts.Id or WikiPostId=Posts.Id) as TagName from Posts where OwnerUserId=? and PostTypeId in ("4","5") and TagName not NULL', (Id,))
    user["tags"]=cursor.fetchall()
    user["tags"].sort(key=lambda x:x["TagName"])
    user["tags_count"]=len(user["tags"])

    return user

user_template=u"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>User {{DisplayName}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="user{{Id}}.html">Next User</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="user{{Id}}.html">Prev User</a>{{/PrevPage}}
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="../index.html">Home</a>
User Id: {{Id}}
</div>
<div class=\"userinfo\">
<p>{{DisplayName}}</p>
<p>Creation: {{CreationDate}}</p>
<p>Reputation: {{Reputation}}</p>
<p>Badges: <a class="internallink" href="#class1badges"><span class="class1">{{#NumBadges}}{{Class1}}{{/NumBadges}}</span></a><a class="internallink" href="#class2badges"><span class="class2">{{#NumBadges}}{{Class2}}{{/NumBadges}}</span></a><a class="internallink" href="#class3badges"><span class="class3">{{#NumBadges}}{{Class3}}{{/NumBadges}}</span></a></p>
<p>Homepage: {{#WebsiteUrl}}<a href="{{WebsiteUrl}}">{{WebsiteUrl}}</a>{{/WebsiteUrl}}</p>
<p>Location: {{#Location}}{{Location}}{{/Location}}</p>
<p>Age: {{#Age}}{{Age}}{{/Age}}</p>
<p>Up votes: {{UpVotes}} Down votes: {{DownVotes}}</p>
<p><a class="internallink" href="#questions">Questions: {{questions_count}}</a> <a class="internallink" href="#answers">Answers: {{answers_count}}</a> <a class="internallink" href="#tags">Tags: {{tags_count}}</a></p>
</div>
<h1>User {{DisplayName}}</h1>
<h2>About Me</h2>
<div class=\"aboutme post\">
{{#AboutMe}}{{{AboutMe}}}{{/AboutMe}}
</div>
<h2>My {{#NumBadges}}{{Class1}}{{/NumBadges}} gold badges<a class="internallink" name="class1badges" href="#class1badges"><span style="float:right;">¶</span></a></h2>
{{#badgesclass1}}
<p><a class="internallink" href="badge{{Name}}.html"><span class="class1">{{Name}}</span></a> awarded on <span class="date">{{#RenderDate}}{{Date}} {{Time}}{{/RenderDate}}</span></p>
{{/badgesclass1}}
<h2>My {{#NumBadges}}{{Class2}}{{/NumBadges}} silver badges<a class="internallink" name="class2badges" href="#class2badges"><span style="float:right;">¶</span></a></h2>
{{#badgesclass2}}
<p><a class="internallink" href="badge{{Name}}.html"><span class="class2">{{Name}}</span></a> awarded on <span class="date">{{#RenderDate}}{{Date}} {{Time}}{{/RenderDate}}</span></p>
{{/badgesclass2}}
<h2>My {{#NumBadges}}{{Class3}}{{/NumBadges}} bronze badges<a class="internallink" name="class3badges" href="#class3badges"><span style="float:right;">¶</span></a></h2>
{{#badgesclass3}}
<p><a class="internallink" href="badge{{Name}}.html"><span class="class3">{{Name}}</span></a> awarded on <span class="date">{{#RenderDate}}{{Date}} {{Time}}{{/RenderDate}}</span></p>
{{/badgesclass3}}
<h2>My {{questions_count}} questions<a class="internallink" name="questions" href="#questions"><span style="float:right;">¶</span></a></h2>
{{#questions}}
<p><a class="internallink" href="question{{Id}}.html">{{Title}}</a></p>
{{/questions}}
<h2>My {{answers_count}} answers<a class="internallink" name="answers" href="#answers"><span style="float:right;">¶</span></a></h2>
{{#answers}}
<p><a class="internallink" href="question{{QuestionId}}.html#{{Id}}">{{QuestionTitle}}</a></p>
{{/answers}}
<h2>My {{tags_count}} tags<a class="internallink" name="tags" href="#tags"><span style="float:right;">¶</span></a></h2>
{{#tags}}
<p><a class="internallink" href="tag{{Id}}.html">{{TagName}}</a></p>
{{/tags}}
  </body>
</html>"""

def render_user_home(user,renderer):
    user_html=renderer.render("{{>user_html}}",user)
    return user_html

def make_users_html(only_ids=None):
    renderer=templates.make_renderer({"user_html":user_template})

    cursor.execute('select Id from Users')
    user_ids = [row["Id"] for row in cursor]
    if only_ids:
        user_ids=only_ids
    max_user_id=max(user_ids)
    len_user_ids=len(user_ids)
    for (i,user_id) in enumerate(user_ids):
        prev_user_id=user_ids[(i-1)%len_user_ids]
        next_user_id=user_ids[(i+1)%len_user_ids]
        user_home=select_user_home(cursor, user_id, prev_user_id, next_user_id)
        print "User",user_home["Id"],"/",max_user_id

        with codecs.open(file_path+"user"+str(user_home["Id"])+".html", "w", "utf-8") as f:
            f.write(render_user_home(user_home,renderer))

(connection,cursor)=init_db()

with connection:
    #import profile
    #profile.run("make_users_html()",sort="tottime")
    make_users_html()
