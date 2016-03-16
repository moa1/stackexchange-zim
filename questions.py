#!/usr/bin/python

# TODO: make that external image alternative texts are shown in a different color, maybe with a link to the external image.

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import rewriteurl
import templates

#PostTypeId="1" means question
#PostTypeId="2" means answer
#PostTypeId="4" means tag excerpt, with Tag.ExcerptPostId==Post.Id
#PostTypeId="5" means tag wiki, with Tag.WikiPostId==Post.Id
#PostTypeId="6" means election text
#PostTypeId="7" means posts made by stackexchange? (TODO)

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

def select_question(cursor, Id):
    question=select_post(cursor,Id)
    
    cursor.execute('select * from Tags where Id in (select TagId from PostsTags where PostId=?)', (Id,))
    question["Tags"]=cursor.fetchall()

    answers=select_answers_for_question(cursor,Id)
    question["answers"]=answers
    
    return question


def render_question(cursor, Id, renderer, prev_post_id, next_post_id):
    question=select_question(cursor,Id)
    question["PrevPage"]=select_question(cursor,prev_post_id)
    question["NextPage"]=select_question(cursor,next_post_id)
    return renderer.render("{{>question_html}}",question)

def make_questions_html(only_ids=None):
    renderer=templates.make_renderer()
    
    cursor.execute('select Id from Posts where PostTypeId="1"')
    post_ids = [row["Id"] for row in cursor]
    if only_ids:
        post_ids=only_ids
    max_Id=max(post_ids)
    len_post_ids=len(post_ids)
    for (i,post_id) in enumerate(post_ids):
        print "Question",post_id,"/",max_Id

        with codecs.open(tempdir+"content/question"+str(post_id)+".html", "w", "utf-8") as f:
            prev_post_id=post_ids[(i-1)%len_post_ids]
            next_post_id=post_ids[(i+1)%len_post_ids]
            f.write(render_question(cursor, post_id, renderer, prev_post_id, next_post_id))

(connection,cursor)=init_db()

with connection:
    print "Questions"
    #import profile
    #profile.run("make_questions_html()")
    make_questions_html()
