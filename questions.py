#!/usr/bin/python

# TODO: make that external image alternative texts are shown in a different color, maybe with a link to the external image.

"""
Question 7511789 / 35823053 at 2016-09-10 02:54:33.993394 ETA: 2016-09-29 17:33:47.519406
Traceback (most recent call last):
  File "./questions.py", line 130, in <module>
    make_questions_html()
  File "./questions.py", line 122, in make_questions_html
    f.write(render_question(cursor, post_id, renderer, prev_post_id, next_post_id))
  File "./questions.py", line 100, in render_question
    question["NextPage"]=select_question(cursor,NextId)
  File "./questions.py", line 85, in select_question
    question=select_post(cursor,Id)
  File "/home/rtoni/stackexchange-zim/utils.py", line 118, in select_post
    post["Body"]=rewriteurl.rewrite_urls_in_html(cursor,post["Body"],stackexchange_domain)
  File "/home/rtoni/stackexchange-zim/rewriteurl.py", line 168, in rewrite_urls_in_html
    assert newhtml.startswith("<html><body>") and newhtml.endswith("</body></html>")
AssertionError
"""

"""
with stackoverflow.com.squashfs compressed using "mksquashfs ./stackoverflow.com.sqlite3 ./stackoverflow.com.sqlite3.squashfs -comp xz -root-owned" and mounted:
CPU usage is at around 5%, and Disk reads at around <1 MB/s.
rtoni@debian:~/stackexchange-zim$ ./questions.py 
Questions at 2016-08-30 16:16:33.413784
Question 4 / 35823053 at 2016-08-30 16:29:14.114718
Question 6 / 35823053 at 2016-08-30 16:29:59.805194
Question 9 / 35823053 at 2016-08-30 16:31:36.229862
Question 11 / 35823053 at 2016-08-30 16:32:46.323628
Question 13 / 35823053 at 2016-08-30 16:33:24.535859
Question 14 / 35823053 at 2016-08-30 16:33:41.309147
Question 16 / 35823053 at 2016-08-30 16:33:46.220353
Question 17 / 35823053 at 2016-08-30 16:33:55.408994

with stackoverflow.com.squashfs compressed using "mksquashfs ./stackoverflow.com.sqlite3 ./stackoverflow.com.sqlite3.squashfs -comp xz -root-owned" and mounted:
CPU usage is at around 70%, and Disk reads at around 7 MB/s.
rtoni@debian:~/stackexchange-zim$ ./questions.py 
Questions
Question 4 / 35823053 at 2016-08-30 15:40:48.185610
Question 6 / 35823053 at 2016-08-30 15:43:08.604310
Question 9 / 35823053 at 2016-08-30 15:48:25.446965
Question 11 / 35823053 at 2016-08-30 15:55:26.272059
Question 13 / 35823053 at 2016-08-30 16:03:24.333881
Question 14 / 35823053 at 2016-08-30 16:09:37.595338
Question 16 / 35823053 at 2016-08-30 16:12:25.249392
Question 17 / 35823053 at 2016-08-30 16:14:43.609224

with stackoverflow.com.squashfs compressed using "mksquashfs ./stackoverflow.com.sqlite3 ./stackoverflow.com.sqlite3.squashfs-compgzip-b4096 -comp gzip -root-owned -b 4096" and mounted:
CPU usage is at around 10%, and Disk reads at around 2 MB/s.
Questions at 2016-08-30 19:35:17.218871
Question 4 / 35823053 at 2016-08-30 20:01:36.537141
Question 6 / 35823053 at 2016-08-30 20:02:08.279820
Question 9 / 35823053 at 2016-08-30 20:03:22.721451
Question 11 / 35823053 at 2016-08-30 20:04:20.140414
Question 13 / 35823053 at 2016-08-30 20:04:54.341013
Question 14 / 35823053 at 2016-08-30 20:05:06.851642
Question 16 / 35823053 at 2016-08-30 20:05:10.724873
Question 17 / 35823053 at 2016-08-30 20:05:19.007552
"""

from utils import *
import codecs
import os
import templates

#PostTypeId="1" means question
#PostTypeId="2" means answer
#PostTypeId="4" means tag excerpt, with Tag.ExcerptPostId==Post.Id
#PostTypeId="5" means tag wiki, with Tag.WikiPostId==Post.Id
#PostTypeId="6" means election text
#PostTypeId="7" means posts made by stackexchange? (TODO)

def question_flat_filename(post_id):
    return 

def select_answer(cursor, Id,rootdir):
    return select_post(cursor,Id,rootdir)

def select_answers_for_question(cursor,QuestionId,rootdir):
    cursor.execute('select AcceptedAnswerId from Posts where Id=?', (QuestionId,))
    accepted_answer_id=cursor.fetchone()["AcceptedAnswerId"]
    if accepted_answer_id:
        accepted_answer_id=int(accepted_answer_id)

    cursor.execute('select Id from Posts where ParentId=?', (QuestionId,))
    answers_id=[row["Id"] for row in cursor]
    answers=[]
    for answer_id in answers_id:
        answer=select_answer(cursor,answer_id,rootdir)
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

def select_question(cursor, Id, rootdir):
    question=select_post(cursor,Id,rootdir)
    
    cursor.execute('select * from Tags where Id in (select TagId from PostsTags where PostId=?)', (Id,))
    question["Tags"]=cursor.fetchall()
    for tag in question["Tags"]:
        tag["RootDir"]=rootdir
        tag["IdPath"]=convert_tag_id_to_idpath(tag["Id"],rootdir)

    answers=select_answers_for_question(cursor,Id,rootdir)
    question["answers"]=answers

    return question


def render_question(cursor, Id, renderer, PrevId, NextId, rootdir):
    question=select_question(cursor,Id,rootdir)
    # doing the next two queries in `select_question` would recurse forever.
    question["PrevPage"]=select_question(cursor,PrevId,rootdir)
    question["NextPage"]=select_question(cursor,NextId,rootdir)
    question["RootDir"]=rootdir
    question["PrevPage"]["RootDir"]=rootdir
    question["NextPage"]["RootDir"]=rootdir
    return renderer.render("{{>question_html}}",question)

def make_questions_html(only_ids=None):
    renderer=templates.make_renderer(templates.templates)

    if only_ids:
        post_ids=only_ids
    else:
        cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
        cursor.execute('select Id from Posts where PostTypeId="1"')
        post_ids = [row["Id"] for row in cursor]
        cursor.row_factory = dict_factory
    max_Id=max(post_ids)
    len_post_ids=len(post_ids)
    start=datetime.datetime.now()
    for (i,post_id) in enumerate(post_ids):
        print "Question",post_id,"/",max_Id,"at",str(datetime.datetime.now()),"ETA:",estimated_time_arrival(start,i,len_post_ids)

        flat_path=file_path+"question/"+str(post_id)+".html"
        (paths,basename,n_subdirs)=split_filename_into_subdirs(flat_path)
        html_path=paths+basename
        if not os.access(paths,os.W_OK):
            os.makedirs(paths)
        with codecs.open(html_path, "w", "utf-8") as f:
            prev_post_id=post_ids[(i-1)%len_post_ids]
            next_post_id=post_ids[(i+1)%len_post_ids]
            html=None
            try:
                html=render_question(cursor, post_id, renderer, prev_post_id, next_post_id,"../"*(n_subdirs+1))
            except:
                print "Error rendering",post_id
                bugf=open("buggy-database-entries.txt", "a")
                bugf.write("domain: %s post_id: %i\n" % (stackexchange_domain,post_id))
                bugf.close()
            if html: f.write(html)

(connection,cursor)=init_db()

with connection:
    print "Questions","at",str(datetime.datetime.now())
    #import profile
    #profile.run("make_questions_html()",sort="tottime")
    #make_questions_html([7511791,7511795]) # spurious </html> and </body> in database.
    make_questions_html()
