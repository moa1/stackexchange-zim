#!/usr/bin/python
# -*- coding:utf-8 -*-

import pystache

templates={
    "date":\
u"""<span class=\"date\">{{Date}}<br/>{{Time}}</span>""",
    
    "userplate":\
    u"""{{#Id}}<span class=\"user\"><a class="internallink" href="user{{Id}}.html">{{#RenderDate}}{{>date}}{{/RenderDate}}{{DisplayName}}</a><br/>{{#ReputationHumanReadable}}<span class="reputation">{{ReputationHumanReadable}}</span>{{/ReputationHumanReadable}}</span>{{/Id}}""",
    
    "comment":\
u"""<div class=\"comment post\">
{{#Score}}<div class=\"score\">{{Score}}</div>{{/Score}}
{{#User}}{{>userplate}}{{/User}}{{{Text}}}
</div><br/>""",

    "answer":\
u"""<div class=\"answer post\">
<a class="internallink answerlink" name="{{Id}}" href="#{{Id}}">¶</a>
<div class=\"answer body\">
<span class=\"score\">{{Score}}</span>
{{#accepted}}<span class=\"scoreaccepted\">X</span>{{/accepted}}
{{{Body}}}
</div>
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
<br/><br/><br/>
{{#comments}}{{>comment}}{{/comments}}
</div>""",

    "answers":\
u"""{{#answers}}
{{>answer}}
{{/answers}}""",

    "tag":\
u"""<span class=\"tag\">
<a class="internallink" href="tag{{Id}}.html">{{TagName}}</a>
</span>""",

    "question":\
u"""
<div class=\"question post\">
<h1>{{Title}}</h1>
<div class=\"question body\">
<span class=\"score\">{{Score}}</span>
{{{Body}}}
{{#Tags}}{{>tag}}{{/Tags}}
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
{{#ClosedDate}}<div class="closed">Closed:<div>{{Date}} {{Time}}</div></div>{{/ClosedDate}}
</div>
<br/><br/><br/>
{{#comments}}{{>comment}}{{/comments}}
</div>
<p><strong>{{AnswerCount}} answers:</strong></p>""",

    "question_html":\
u"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>{{Title}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
  <body>
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="question{{Id}}.html">Next Question</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="question{{Id}}.html">Prev Question</a>{{/PrevPage}}
<a class="internallink" href="index_tags.html">Tags Index</a>
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="index_questions.html">Questions Index</a>
Question Id: {{Id}}
</div>
    {{>question}}
    {{>answers}}
  </body>
</html>""",

    "tagpost":\
u"""
<div class=\"post\">
<div class=\"body\">{{{Body}}}</div>
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
<br/><br/><br/>
{{#comments}}{{>comment}}{{/comments}}
</div>""",

    "tag_html":\
u"""<!DOCTYPE html>
<html>
  <head>
    <title>{{TagName}}</title>
    <link href="se.css" rel="stylesheet" type="text/css">
  </head>
  <body>
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="tag{{Id}}.html">Next Tag</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="tag{{Id}}.html">Prev Tag</a>{{/PrevPage}}
<a class="internallink" href="index_tags.html">Tags Index</a>
<a class="internallink" href="index_users.html">Users Index</a>
<a class="internallink" href="index_questions.html">Questions Index</a>
Tag Id: {{Id}}
</div>
<h1>Tag {{>tag}}</h1>
<div class="tagpage">
<h2>Excerpt</h2>
{{#ExcerptPost}}{{>tagpost}}{{/ExcerptPost}}
<h2>Wiki</h2>
{{#WikiPost}}{{>tagpost}}{{/WikiPost}}
</div>
<h2>{{Count}} Questions with tag {{>tag}}</h2>
{{#questions}}
<p><a class="internallink" href="question{{Id}}.html">{{Title}}</a></p>
{{/questions}}
  </body>
</html>
"""
    }

def make_renderer():
    renderer=pystache.Renderer(partials=templates,missing_tags="strict")
    return renderer
