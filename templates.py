#!/usr/bin/python
# -*- coding:utf-8 -*-

import pystache

templates={
    "date":\
u"""<span class=\"date\">{{Date}}<br/>{{Time}}</span>""",
    
    "userplate":\
    u"""{{#Id}}<span class=\"user\"><a class="internallink" href="user{{Id}}.html">{{#RenderDate}}{{>date}}{{/RenderDate}}{{DisplayName}}</a><br/>{{#ReputationHumanReadable}}{{ReputationHumanReadable}}{{/ReputationHumanReadable}}</span>{{/Id}}""",
    
    "comment":\
u"""<div class=\"comment container\">
<div class=\"score\">{{Score}}</div>
{{#User}}{{>userplate}}{{/User}}{{{Text}}}
</div><br/>""",

    "answer":\
u"""<div class=\"answer post container\">
<a class="internallink answerlink" name="{{Id}}" href="#{{Id}}">¶</a>
<span class=\"score\">{{Score}}</span>
{{#accepted}}<span class=\"scoreaccepted\">X</span>{{/accepted}}
<div class=\"answer body\">{{{Body}}}</div>
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
<br/><br/><br/>
{{#comments}}{{>comment}}{{/comments}}
</div>""",

    "answers":\
u"""{{#answers}}
{{>answer}}
{{/answers}}""",
    
    "question":\
u"""
<div class=\"question post container\">
<h1>{{Title}}</h1>
<div class=\"score\">{{Score}}</div>
<div class=\"question body\">
{{{Body}}}
{{#Tags}}
<span class=\"tag post\">
<a class="internallink" href="tag{{Id}}.html">{{TagName}}</a>
</span>
{{/Tags}}
</div>
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
{{#ClosedDate}}<div class="closed">Closed:<div>{{Date}} {{Time}}</div></div>{{/ClosedDate}}
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
</div>
    {{>question}}
    {{>answers}}
  </body>
</html>"""
    }

def make_renderer():
    renderer=pystache.Renderer(partials=templates,missing_tags="strict")
    return renderer
