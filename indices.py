#!/usr/bin/python
# -*- coding:utf-8 -*-

# TODO: make that HTML <code> is rendered with a grey background.
# TODO: make that external image alternative texts are shown in a different color, maybe with a link to the external image.

from utils import *
import pystache
import codecs

templates={
    'sites_index_template':\
u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{site_type}} Index</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<div class="linkheader">
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="index_questions.html">Questions Index</a>
<a class="internallink" href="index_tags.html">Tags Index</a>
</div>
<h1>{{site_type}} Index</h1>
<p>Number of {{site_type}}: {{sites_count}}</p>
<div class="index">
{{#sub_indices}}
<a class="internallink" href="{{filename}}">&quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</a><br/>
{{/sub_indices}}
</div>
  </body>
</html>""",

    'sites_sub_index_template':\
u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{site_type}} Index &quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<div class="linkheader">
{{#NextPage}}Next: <a class="internallink" href="{{filename}}">{{filename}}</a>{{/NextPage}}
{{#PrevPage}}Prev: <a class="internallink" href="{{filename}}">{{filename}}</a>{{/PrevPage}}
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="index_questions.html">Questions Index</a>
<a class="internallink" href="index_tags.html">Tags Index</a>
</div>
<h1>{{site_type}} Index &quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</h1>
<div class="index">
{{#sub_sites}}
<a class="internallink" href="{{Link}}">{{Title}}</a>
{{/sub_sites}}
</div>
  </body>
</html>"""}

renderer=pystache.Renderer(partials=templates,missing_tags="strict")


def write_index_html(site_type, sites, file_path, file_mask, sub_index_size=1000):
    index_filename=file_mask % ("",)
    sub_indices=[]
    starts=range(0,len(sites),sub_index_size)
    for start in starts:
        sub_sites=sites[start:start+sub_index_size]
        sub_index_filename=file_mask % (str(start),)
        sub_index={"site_type":site_type,"first_index":start,"index_filename":index_filename,"filename":sub_index_filename,"first":sub_sites[0],"last":sub_sites[-1],"sub_sites":sub_sites}
        sub_indices.append(sub_index)

    len_sub_indices=len(sub_indices)
    for (i,sub_index) in enumerate(sub_indices):
        sub_index["PrevPage"]=sub_indices[(i-1)%len_sub_indices]
        sub_index["NextPage"]=sub_indices[(i+1)%len_sub_indices]
        with codecs.open(file_path+"/"+sub_index["filename"], "w", "utf-8") as f:
            f.write(renderer.render('{{>sites_sub_index_template}}',sub_index))

    with codecs.open(file_path+"/"+index_filename, "w", "utf-8") as f:
        f.write(renderer.render('{{>sites_index_template}}',{"site_type":site_type,"sites_count":len(sites),"sub_indices":sub_indices}))
    
def write_users_index_html(cursor):
    cursor.execute('select Id,DisplayName as Title,"user"||Id||".html" as Link from Users order by DisplayName')
    users=cursor.fetchall()

    write_index_html("Users",users,tempdir+"content","index_users%s.html")

def write_questions_index_html(cursor):
    cursor.execute('select Id,Title,"question"||Id||".html" as Link from Posts where PostTypeId="1" order by Title')
    questions=cursor.fetchall()

    write_index_html("Questions",questions,tempdir+"content","index_questions%s.html")

def write_tags_index_html(cursor):
    cursor.execute('select Id,TagName as Title,"tag"||Id||".html" as Link from Tags order by TagName')
    tags=cursor.fetchall()

    write_index_html("Tags",tags,tempdir+"content","index_tags%s.html")


(connection,cursor)=init_db()

with connection:
    print "Users Index"
    write_users_index_html(cursor)
    print "Questions Index"
    write_questions_index_html(cursor)
    print "Tags Index"
    write_tags_index_html(cursor)
