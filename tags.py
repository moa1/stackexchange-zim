#!/usr/bin/python
# -*- coding:utf-8 -*-

from utils import *
import codecs
import os
import templates

"""
Tags
Tag 1 / 118310
2016-08-16 15:43:28.911488 select_tag(cursor,Id)
2016-08-16 15:43:30.144048 select questions
2016-08-16 15:51:49.647039 select number_questions
2016-08-16 15:59:28.883504 select questions
2016-08-16 15:59:28.968285 select number_questions
2016-08-16 15:59:35.162972 select questions
2016-08-16 16:09:44.278063 select number_questions
2016-08-16 16:20:34.990333 rendering
Tag 2 / 118310
2016-08-16 16:20:35.150056 select_tag(cursor,Id)
2016-08-16 16:20:41.927126 select questions
2016-08-16 16:29:44.415969 select number_questions
"""

def select_tag(cursor,Id,rootdir,overview_only=False):
    cursor.execute('select * from Tags where Id=?', (Id,))
    tag=cursor.fetchone()

    tag["RootDir"]=rootdir
    tag["IdPath"]=convert_tag_id_to_idpath(Id,rootdir)

    if overview_only:
        return tag

    excerpt_post_id=tag["ExcerptPostId"]
    if excerpt_post_id:
        tag["ExcerptPost"]=select_post(cursor,int(excerpt_post_id),rootdir)
    else:
        tag["ExcerptPost"]=None
    wiki_post_id=tag["WikiPostId"]
    if wiki_post_id:
        tag["WikiPost"]=select_post(cursor,int(wiki_post_id),rootdir)
    else:
        tag["WikiPost"]=None

    #print str(datetime.datetime.now()), "select questions"
    cursor.execute('select Id,Title from Posts where Id in (select PostId from PostsTags where TagId=?) order by (0+Score) desc limit 1000', (Id,))
    tag["questions"]=cursor.fetchall()
    for question in tag["questions"]:
        question["RootDir"]=rootdir
        question["IdPath"]=convert_question_id_to_idpath(question["Id"],rootdir)

    #print str(datetime.datetime.now()), "select number_questions"
    cursor.execute('select max(0,count(*)-1000) as NumberMoreQuestions from PostsTags where TagId=?', (Id,))
    tag["number_questions"]=cursor.fetchone()["NumberMoreQuestions"]

    return tag

def render_tag(cursor,Id,renderer,PrevId,NextId,rootdir):
    #print str(datetime.datetime.now()), "select_tag(cursor,Id)"
    tag=select_tag(cursor,Id,rootdir)
    # doing the next two queries in `select_question` would recurse forever.
    tag["PrevPage"]=select_tag(cursor,PrevId,rootdir,True)
    tag["NextPage"]=select_tag(cursor,NextId,rootdir,True)
    #print str(datetime.datetime.now()), "rendering"
    return renderer.render("{{>tag_html}}",tag,True)

def make_tags_html(only_ids=[]):
    renderer=templates.make_renderer(templates.templates)

    if only_ids:
        tag_ids=only_ids
    else:
        cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
        cursor.execute('select Id from Tags')
        tag_ids = [row["Id"] for row in cursor]
        cursor.row_factory = dict_factory
    max_tag_id=max(tag_ids)
    len_tag_ids=len(tag_ids)
    start=datetime.datetime.now()
    for (i,tag_id) in enumerate(tag_ids):
        print "Tag",tag_id,"/",max_tag_id,"at",str(datetime.datetime.now()),"ETA:",estimated_time_arrival(start,i,len_tag_ids)

        flat_path=file_path+"tag/"+str(tag_id)+".html"
        (paths,basename,n_subdirs)=split_filename_into_subdirs(flat_path)
        html_path=paths+basename
        if not os.access(paths,os.W_OK):
            os.makedirs(paths)
        with codecs.open(html_path, "w", "utf-8") as f:
            prev_tag_id=tag_ids[(i-1)%len_tag_ids]
            next_tag_id=tag_ids[(i+1)%len_tag_ids]
            f.write(render_tag(cursor, tag_id, renderer, prev_tag_id, next_tag_id,"../"*(n_subdirs+1)))


(connection,cursor)=init_db()

with connection:
    print "Tags","at",str(datetime.datetime.now())
    #import profile
    #profile.run("make_tags_html()",sort="tottime")
    make_tags_html()
