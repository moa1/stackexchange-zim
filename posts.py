#!/usr/bin/python

# TODO: make a page for each Tag in Tags.xml
# TODO: parse Tags and link them to its Tag page
# TODO: make that HTML <code> is rendered with a grey background.

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import pickle

#PostTypeId="1" means question
#PostTypeId="2" means answer
#PostTypeId="4" means tag description, with Tag.ExcerptPostId==Post.Id
#PostTypeId="5" means tag wiki, with Tag.WikiPostId==Post.Id
#PostTypeId="6" means election text
#PostTypeId="7" means ? TODO:

user_template=pystache.parse(u"""<div class=\"user\"><a href="user{{Id}}.html">{{DisplayName}}</a></div>""")

def render_user(cursor, Id):
    cursor.execute('select * from Users where Id=?', (Id,))
    user=cursor.fetchone()
    user_html=pystache.render(user_template,user)
    return user_html

answers_template=pystache.parse(u"""{{#answers}}
<div class=\"answer post container\">
{{#accepted}}<div class=\"scoreaccepted\">{{Score}}</div>{{/accepted}}
{{^accepted}}<div class=\"score\">{{Score}}</div>{{/accepted}}
<div class=\"answer body\">{{{Body}}}</div>
<p>
  {{{OwnerUser_html}}}
  {{{LastEditorUser_html}}}
  <div class=\"postdate\">{{LastActivityDate}}</div>
</p>
{{#comments}}
<div class=\"comment container\">{{{User_html}}}{{{Text}}}</div>
{{/comments}}
</div>
{{/answers}}""")

def select_comments_for_post(cursor,PostId):
    cursor.execute('select * from Comments where PostId=?', (PostId,))
    posts=cursor.fetchall()
    return posts

def select_answer(cursor, Id):
    answer_comments=select_comments_for_post(cursor,Id)
    for answer_comment in answer_comments:
        answer_comment["User_html"]=render_user(cursor,answer_comment["UserId"])

    cursor.execute('select * from Posts where Id=?', (Id,))
    answer=cursor.fetchone()
    
    answer["OwnerUser_html"]=render_user(cursor,answer["OwnerUserId"])
    answer["LastEditorUser_html"]=render_user(cursor,answer["LastEditorUserId"])
    answer["comments"]=answer_comments

    return answer

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
<p>Tags:{{Tags}}</p>
<h1>{{Title}}</h1>
<div class=\"score\">{{Score}}</div>
<div class=\"question body\">{{{Body}}}</div>
{{#comments}}
<div class=\"comment container\">{{{User_html}}}{{{Text}}}</div>
{{/comments}}
<p>
  {{{OwnerUser_html}}}
  {{{LastEditorUser_html}}}
  <div class=\"postdate\">{{LastActivityDate}}</div>
</p>
</div>
<p><strong>{{AnswerCount}} answers:</strong></p>""")

def select_question(cursor, Id):
    question_comments=select_comments_for_post(cursor,Id)
    for question_comment in question_comments:
        question_comment["User_html"]=render_user(cursor,question_comment["UserId"])

    cursor.execute('select * from Posts where Id=?', (Id,))
    question=cursor.fetchone()
    
    question["OwnerUser_html"]=render_user(cursor,question["OwnerUserId"])
    question["LastEditorUser_html"]=render_user(cursor,question["LastEditorUserId"])
    question["comments"]=question_comments

    return question
    
post_template=pystache.parse(u"""
<html>
  <head>
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


(connection,cursor)=init_db()



def make_posts_html(limit=None):
    if limit:
        cursor.execute('select Id from Posts where PostTypeId="1" limit '+str(limit))
    else:
        cursor.execute('select Id from Posts where PostTypeId="1"')
    post_ids = [row["Id"] for row in cursor]
    for post_id in post_ids:
        print post_id

        f=codecs.open(tempdir+"content/post"+str(post_id)+".html", "w", "utf-8")
        f.write(render_post(cursor, post_id))
        f.close()

(connection,cursor)=init_db()

#import profile
#profile.run("make_posts_html()")
make_posts_html()

#post_id=882
#f=codecs.open(tempdir+"content/post"+str(post_id)+".html", "w", "utf-8")
#f.write(render_post(cursor, post_id))
#f.close()
