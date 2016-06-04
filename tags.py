#!/usr/bin/python
# -*- coding:utf-8 -*-

from utils import *
import codecs
import templates

def select_tag(cursor,Id):
    cursor.execute('select * from Tags where Id=?', (Id,))
    tag=cursor.fetchone()

    excerpt_post_id=tag["ExcerptPostId"]
    if excerpt_post_id:
        tag["ExcerptPost"]=select_post(cursor,int(excerpt_post_id))
    else:
        tag["ExcerptPost"]=None
    wiki_post_id=tag["WikiPostId"]
    if wiki_post_id:
        tag["WikiPost"]=select_post(cursor,int(wiki_post_id))
    else:
        tag["WikiPost"]=None

    cursor.execute('select * from Posts where Id in (select PostId from PostsTags where TagId=?)', (Id,))
    tag["questions"]=cursor.fetchall()

    return tag


def render_tag(cursor,Id,renderer,PrevId,NextId):
    tag=select_tag(cursor,Id)
    # doing the next two queries in `select_question` would recurse forever.
    tag["PrevPage"]=select_tag(cursor,PrevId)
    tag["NextPage"]=select_tag(cursor,NextId)
    return renderer.render("{{>tag_html}}",tag)

def make_tags_html():
    renderer=templates.make_renderer(templates.templates)

    cursor.execute('select Id from Tags')
    tag_ids = [row["Id"] for row in cursor]
    max_tag_id=max(tag_ids)
    len_tag_ids=len(tag_ids)
    for (i,tag_id) in enumerate(tag_ids):
        print "Tag",tag_id,"/",max_tag_id

        with codecs.open(file_path+"tag/"+str(tag_id)+".html", "w", "utf-8") as f:
            prev_tag_id=tag_ids[(i-1)%len_tag_ids]
            next_tag_id=tag_ids[(i+1)%len_tag_ids]
            f.write(render_tag(cursor, tag_id, renderer, prev_tag_id, next_tag_id))


(connection,cursor)=init_db()

with connection:
    print "Tags"
    #import profile
    #profile.run("make_tags_html()",sort="tottime")
    make_tags_html()
