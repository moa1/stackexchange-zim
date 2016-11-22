#!/usr/bin/python
# -*- coding:utf-8 -*-

from utils import *
import codecs
import rewriteurl
import templates

def select_badge_home(cursor, Name, PrevName, NextName):
    cursor.execute('select Name,Class,TagBased from Badges where Name=? limit 1', (Name,))
    badge=cursor.fetchone()
    badge["ClassMetal"]={"1":"gold","2":"silver","3":"bronze"}[badge["Class"]]

    if badge["TagBased"]=="True":
        cursor.execute('select (select Id from Tags where TagName=Badges.Name) as Id, Name from Badges where Name=? limit 1', (Name,))
        badge["Tag"]=cursor.fetchone()
    else:
        badge["Tag"]=None
        
    badge["PrevPage"]={"Name":PrevName}
    badge["NextPage"]={"Name":NextName}

    cursor.execute('select count(*) from Badges where Name=?', (Name,))
    badge["Awarded_count"]=cursor.fetchone()
    cursor.execute('select UserId,(select DisplayName from Users where Id=Badges.UserId) as UserName,Date from Badges where Name=? order by Date desc limit 1000', (Name,))
    badge["Awarded"]=cursor.fetchall()
    for awarded in badge["Awarded"]:
        awarded["RenderDate"]=make_Date(awarded["Date"])
    badge["Awarded_display_count"]=len(badge["Awarded"])

    return badge

badge_template=u"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Badge {{Name}}</title>
    <link href="../se.css" rel="stylesheet" type="text/css">
  </head>
    <body>
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="{{Name}}.html">Next Badge</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="{{Name}}.html">Prev Badge</a>{{/PrevPage}}
<a class="internallink" href="../index_badges.html">Badges Index</a>
<a class="internallink" href="../../index.html">Home</a>
Badge Name: {{Name}}
</div>
<div class=\"badgeinfo\">
<p>Badge {{Name}}</p>
<p>Class: <span class="class{{Class}}">{{ClassMetal}}</span></p>
{{#Tag}}Based on tag <a class="internallink" href="../tag/{{Id}}.html">{{Name}}</a>{{/Tag}}
<p><a class="internallink" href="#awarded">Awarded {{Awarded_count}} times</a></p>
</div>
<h1>{{Name}}</h1>
<h2>Awarded {{Awarded_count}} times<a class="internallink" name="awarded" href="#awarded"><span style="float:right;">¶</span></a></h2>
{{#Awarded}}
<p>Only the first {{Awarded_display_count}} are displayed.</p>
<p>Awarded to <a class="internallink" href="../user/{{UserId}}.html">{{UserName}}</a> on <span class="date">{{#RenderDate}}{{Date}} {{Time}}{{/RenderDate}}</span></p>
{{/Awarded}}
  </body>
</html>"""

def render_badge_home(badge,renderer):
    html=renderer.render("{{>badge_html}}",badge)
    return html

def make_badges_html(only_names=None):
    renderer=templates.make_renderer({"badge_html":badge_template})

    if only_names:
        badge_names=only_names
    else:
        cursor.row_factory = sqlite3.Row #saves memory compared to =dict_factory
        cursor.execute('select distinct Name from Badges order by Name')
        badge_names = [row["Name"] for row in cursor]
        cursor.row_factory = dict_factory
    len_badge_names=len(badge_names)
    start=datetime.datetime.now()
    for (i,badge_name) in enumerate(badge_names):
        prev_badge_name=badge_names[(i-1)%len_badge_names]
        next_badge_name=badge_names[(i+1)%len_badge_names]
        badge_home=select_badge_home(cursor, badge_name, prev_badge_name, next_badge_name)
        print "Badge",i,"/",len_badge_names,"at",str(datetime.datetime.now()),"ETA:",estimated_time_arrival(start,i,len_badge_names)

        with codecs.open(file_path+"badge/"+badge_name+".html", "w", "utf-8") as f:
            f.write(render_badge_home(badge_home,renderer))

(connection,cursor)=init_db()

with connection:
    print "Badges","at",str(datetime.datetime.now())
    #import profile
    #profile.run("make_badges_html()",sort="tottime")
    make_badges_html()
