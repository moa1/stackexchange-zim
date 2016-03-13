#!/usr/bin/python
# -*- coding:utf-8 -*-

# TODO: make that HTML <code> is rendered with a grey background.
# TODO: make that external image alternative texts are shown in a different color, maybe with a link to the external image.

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import pickle

#PostTypeId="1" means question
#PostTypeId="2" means answer
#PostTypeId="4" means tag excerpt, with Tag.ExcerptPostId==Post.Id
#PostTypeId="5" means tag wiki, with Tag.WikiPostId==Post.Id
#PostTypeId="6" means election text
#PostTypeId="7" means ? TODO:

answers_template=pystache.parse(u"""{{#answers}}
<div class=\"answer post container\">
<a class="answerlink" name="{{Id}}" href="#{{Id}}">¶</a>
{{#accepted}}<div class=\"scoreaccepted\">{{Score}}</div>{{/accepted}}
{{^accepted}}<div class=\"score\">{{Score}}</div>{{/accepted}}
<div class=\"answer body\">{{{Body}}}</div>
{{{OwnerUser_html}}}
{{{LastEditorUser_html}}}
<div class=\"postdate\">{{LastActivityDate}}</div>
{{#comments}}
<div class=\"comment container\">{{{User_html}}}{{{Text}}}</div>
{{/comments}}
</div>
{{/answers}}""")

def select_answer(cursor, Id):
    return select_post(cursor,Id)

def select_answers_for_question(cursor,QuestionId):
    cursor.execute('select AcceptedAnswerId from Posts where Id=?', (QuestionId,))
    accepted_answer_id=cursor.fetchone()["AcceptedAnswerId"]
    if accepted_answer_id:
        accepted_answer_id=int(accepted_answer_id)

    cursor.execute('select Id from Posts where ParentId=?', (QuestionId,))
    answers_id=[row["Id"] for row in cursor]
    answers=[]
    for answer_id in answers_id:
        answer=select_answer(cursor,answer_id)
        answer["accepted"]=accepted_answer_id and answer["Id"]==accepted_answer_id
        answers.append(answer)

    # sort answers by score, but put the answer with Id==AcceptedAnswerId of the question in front
    if accepted_answer_id:
        answers_accepted=[answer for answer in answers if answer["accepted"]]
        answers_without=[answer for answer in answers if not answer["accepted"]]
        answers_without.sort(key=lambda x: int(x["Score"]), reverse=True)
        answers=answers_accepted+answers_without
    else:
        answers.sort(key=lambda x: int(x["Score"]), reverse=True)

    return answers

def render_answers_for_question(cursor,QuestionId):
    answers=select_answers_for_question(cursor,QuestionId)
    answers_html=pystache.render(answers_template,{"answers":answers})
    return answers_html

question_template=pystache.parse(u"""<div class=\"question container\">
<p>
Tags:
{{#Tags}}
<a href="tag{{Id}}.html">{{TagName}}</a>
{{/Tags}}
</p>
<h1>{{Title}}</h1>
<div class=\"score\">{{Score}}</div>
<div class=\"question body\">{{{Body}}}</div>
{{{OwnerUser_html}}}
{{{LastEditorUser_html}}}
<div class=\"postdate\">{{LastActivityDate}}</div>
{{#comments}}
<div class=\"comment container\">{{{User_html}}}{{{Text}}}</div>
{{/comments}}
</div>
<p><strong>{{AnswerCount}} answers:</strong></p>""")

def select_question(cursor, Id):
    question=select_post(cursor,Id)
    
    cursor.execute('select * from Tags where Id in (select TagId from PostsTags where PostId=?)', (Id,))
    question["Tags"]=cursor.fetchall()

    return question
    
post_template=pystache.parse(u"""
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{Title}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
  <body>
    {{{question_html}}}
    {{{answers_html}}}
  </body>
</html>
""")

def render_post(cursor, Id):
    question=select_question(cursor,Id)
    question_html=pystache.render(question_template,question)

    answers_html=render_answers_for_question(cursor,Id)

    post={"Title":question["Title"],"question_html":question_html, "answers_html":answers_html}
    post_html=pystache.render(post_template,post)
    
    return post_html

def make_posts_html(limit=None):
    if limit:
        cursor.execute('select Id from Posts where PostTypeId="1" limit '+str(limit))
    else:
        cursor.execute('select Id from Posts where PostTypeId="1"')
    post_ids = [row["Id"] for row in cursor]
    max_Id=max(post_ids)
    for post_id in post_ids:
        print "Post",post_id,"/",max_Id

        with codecs.open(tempdir+"content/post"+str(post_id)+".html", "w", "utf-8") as f:
            f.write(render_post(cursor, post_id))

(connection,cursor)=init_db()

with connection:
    print "Posts"
    #import profile
    #profile.run("make_posts_html()")
    make_posts_html()

#for post_id in (1,6,882):
#    with codecs.open(tempdir+"content/post"+str(post_id)+".html", "w", "utf-8") as f:
#        f.write(render_post(cursor, post_id))
