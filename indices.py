#!/usr/bin/python
# -*- coding:utf-8 -*-

# TODO: make that HTML <code> is rendered with a grey background.
# TODO: make that external image alternative texts are shown in a different color, maybe with a link to the external image.

from utils import *
import pystache
from pysqlite2 import dbapi2 as sqlite3
import codecs
import pickle

sites_index_template=pystache.parse(u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{site_type}} Index</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<h1>{{site_type}} Index</h1>
<p>Number of {{site_type}}: {{sites_count}}</p>
{{#sub_indices}}
<p>
<a href="{{sub_index_filename}}">&quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</a>
</p>
{{/sub_indices}}
  </body>
</html>""")

sites_sub_index_template=pystache.parse(u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{site_type}} Index &quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<h1>{{site_type}} Index &quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</h1>
<p>
<a href="{{index_filename}}">Back to {{site_type}} Index</a>
</p>
{{#sub_index}}
<div class=\"floatleft\"><a href="{{Link}}">{{Title}}</a></div>
{{/sub_index}}
  </body>
</html>""")

def write_index_html(site_type, sites, file_path, file_mask, sub_index_size=1000):
    index_filename=file_mask % ("",)
    sub_indices=[]
    for i in range(0,len(sites),sub_index_size):
        sub_index=sites[i:i+sub_index_size]
        sub_index_filename=file_mask % (str(i),)
        d={"site_type":site_type,"first_index":i,"index_filename":index_filename,"sub_index_filename":sub_index_filename,"first":sub_index[0],"last":sub_index[-1],"sub_index":sub_index}
        sub_indices.append(d)

        print sub_index_filename

        with codecs.open(file_path+"/"+sub_index_filename, "w", "utf-8") as f:
            f.write(pystache.render(sites_sub_index_template,d))

    with codecs.open(file_path+"/"+index_filename, "w", "utf-8") as f:
        f.write(pystache.render(sites_index_template,{"site_type":site_type,"sites_count":len(sites),"sub_indices":sub_indices}))
    
def write_users_index_html(cursor):
    cursor.execute('select Id,DisplayName as Title,"user"||Id||".html" as Link from Users order by DisplayName')
    users=cursor.fetchall()

    write_index_html("Users",users,tempdir+"content","index_users%s.html")

def write_posts_index_html(cursor):
    cursor.execute('select Id,Title,"post"||Id||".html" as Link from Posts where PostTypeId="1" order by Title')
    posts=cursor.fetchall()

    write_index_html("Posts",posts,tempdir+"content","index_posts%s.html")

def write_tags_index_html(cursor):
    cursor.execute('select Id,TagName as Title,"tag"||Id||".html" as Link from Tags order by TagName')
    tags=cursor.fetchall()

    write_index_html("Tags",tags,tempdir+"content","index_tags%s.html")


(connection,cursor)=init_db()

with connection:
    print "Users Index"
    write_users_index_html(cursor)
    print "Posts Index"
    write_posts_index_html(cursor)
    print "Tags Index"
    write_tags_index_html(cursor)
