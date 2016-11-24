#!/usr/bin/python
# -*- coding:utf-8 -*-

# TODO: make that HTML <code> is rendered with a grey background.
# TODO: make that external image alternative texts are shown in a different color, maybe with a link to the external image.

from utils import *
import codecs
import templates

indices_templates={
    'sites_index_template':\
u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{site_type}} Index</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<div class="linkheader">
<a class="internallink" href="../index.html">Home</a>
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="index_questions.html">Questions Index</a>
<a class="internallink" href="index_tags.html">Tags Index</a>
<a class="internallink" href="index_badges.html">Badges Index</a>
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
<a class="internallink" href="{{index_filename}}">{{site_type}} Index</a>
</div>
<h1>{{site_type}} Index &quot;{{#first}}{{Title}}{{/first}}&quot; to &quot;{{#last}}{{Title}}{{/last}}&quot;</h1>
<div class="index">
{{#sub_sites}}
<a class="internallink" href="{{Link}}">{{Title}}</a>
{{/sub_sites}}
</div>
  </body>
</html>""",
}


renderer=templates.make_renderer(indices_templates)


def write_index_html(cursor, select_entry, site_type, sites, file_mask, sub_index_size=1000):
    cursor.row_factory = dict_factory # We have to modify the Link

    print "writing index for '%s': %i entries" % (site_type, len(sites))
    index_filename=file_mask % ("",)
    sub_indices=[]
    starts=range(0,len(sites),sub_index_size)
    for start in starts:
        sub_sites=sites[start:start+sub_index_size]
        sub_index_filename=file_mask % (str(start),)
        sub_index={"site_type":site_type,"first_index":start,"index_filename":index_filename,"filename":sub_index_filename,"sub_ids":sub_sites}
        sub_indices.append(sub_index)

    #cursor.row_factory = dict_factory #necessary for access as a dict
    len_sub_indices=len(sub_indices)
    for (i,sub_index) in enumerate(sub_indices):
        print "writing "+sub_index["filename"],"/",len(sites)
        sub_index["PrevPage"]=sub_indices[(i-1)%len_sub_indices]
        sub_index["NextPage"]=sub_indices[(i+1)%len_sub_indices]
        sub_sites = []
        for Id in sub_index["sub_ids"]:
            cursor.execute(select_entry, (Id["Id"],))
            new_site=cursor.fetchone()
            if site_type in ["Users","Users by Reputation","Questions by Score","Tags","Tags by Questions"]:
                new_site["Link"]=convert_id_to_idpath(new_site["Link"])
            sub_sites.append(new_site)
        sub_index["sub_sites"]=sub_sites
        sub_index["first"]=sub_sites[0]
        sub_index["last"]=sub_sites[-1]
        with codecs.open(file_path+sub_index["filename"], "w", "utf-8") as f:
            f.write(renderer.render('{{>sites_sub_index_template}}',sub_index))
        # free memory
        sub_index["sub_sites"]=None
        # do not set sub_index["first"]=None, it is needed below
        # do not set sub_index["last"]=None, it is needed below

    print "writing "+index_filename
    with codecs.open(file_path+index_filename, "w", "utf-8") as f:
        f.write(renderer.render('{{>sites_index_template}}',{"site_type":site_type,"sites_count":len(sites),"sub_indices":sub_indices}))
    
def write_badges_index_html(cursor):
    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute('select distinct Name as Id from Badges order by Name')
    users=cursor.fetchall()
    select_entry='select distinct Name as Id,Name as Title,"badge/"||Name||".html" as Link from Badges where Name=?'
    write_index_html(cursor, select_entry, "Badges",users,"index_badges%s.html")

def write_users_index_html(cursor,connection):
    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute('select Id from Users order by DisplayName')
    users=cursor.fetchall()
    select_entry='select Id,DisplayName as Title,"user/"||Id||".html" as Link from Users where Id=?'
    write_index_html(cursor, select_entry, "Users",users,"index_users%s.html")

def write_users_by_reputation_index_html(cursor):
    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute('select Id from Users order by (Reputation+0) desc')
    questions=cursor.fetchall()
    select_entry='select Id,Reputation||": "||DisplayName as Title,"user/"||Id||".html" as Link from Users where Id=?'
    write_index_html(cursor, select_entry, "Users by Reputation",questions,"index_users_by_reputation%s.html")

def write_questions_by_score_index_html(cursor):
    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute('select Id from Posts where PostTypeId="1" order by (Score+0) desc')
    questions=cursor.fetchall()
    select_entry='select Id,Score||": "||Title as Title,"question/"||Id||".html" as Link from Posts where Id=?'
    write_index_html(cursor, select_entry, "Questions by Score",questions,"index_questions_by_score%s.html")

def write_tags_index_html(cursor):
    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute('select Id from Tags order by TagName')
    tags=cursor.fetchall()
    select_entry='select Id,TagName as Title,"tag/"||Id||".html" as Link from Tags where Id=?'
    write_index_html(cursor, select_entry, "Tags",tags,"index_tags%s.html")

def write_tags_by_questions_index_html(cursor):
    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute('select Id from (select TagId as Id, count(*) as Count from PostsTags group by Id) order by Count desc;')
    tags=cursor.fetchall()
    select_entry='select Id,TagName||": "||(select count(*) from PostsTags where TagId=Tags.Id) as Title,"tag/"||Id||".html" as Link from Tags where Id=?;'
    write_index_html(cursor, select_entry, "Tags by Questions",tags,"index_tags_by_questions%s.html")

def write_main_index_html(cursor):
    template=u"""<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Index</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<div class="linkheader">
<a class="internallink" href="../index.html">Home</a>
</div>
<h1>Index</h1>
<p><a class="internallink" href="index_users.html">Index of {{UsersCount}} users by name</a></p>
<p><a class="internallink" href="index_users_by_reputation.html">Index of {{UsersCount}} users by reputation</a></p>
<p><a class="internallink" href="index_questions_by_score.html">Index of {{QuestionsCount}} questions by score</a></p>
<p><a class="internallink" href="index_tags.html">Index of {{TagsCount}} tags</a></p>
<p><a class="internallink" href="index_tags_by_questions.html">Index of {{TagsCount}} tags by number of questions</a></p>
<p><a class="internallink" href="index_badges.html">Index of {{BadgesCount}} badges</a></p>
  </body>
</html>"""

    cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
    cursor.execute("""select
(select count(*) from Users) as UsersCount,
(select count(*) from Posts where PostTypeId="1") as QuestionsCount,
(select count(*) from Tags) as TagsCount,
(select count(distinct Name) from Badges) as BadgesCount""")
    data=cursor.fetchone()

    with codecs.open(file_path+"index.html", "w", "utf-8") as f:
        f.write(renderer.render(template,data))


(connection,cursor)=init_db()

with connection:
    print "Tags Index"
    write_tags_index_html(cursor)
    print "Tags by Questions Index"
    write_tags_by_questions_index_html(cursor)
    print "Badges Index"
    write_badges_index_html(cursor)
    print "Users Index"
    write_users_index_html(cursor,connection)
    print "Users by Reputation Index"
    write_users_by_reputation_index_html(cursor)
    print "Questions By Score Index"
    write_questions_by_score_index_html(cursor)
    print "Main Index"
    write_main_index_html(cursor)
