#!/usr/bin/python
# -*- coding:utf-8 -*-

import pystache

templates={
    "userplate":\
u"""{{#Id}}<span class=\"user\"><a class="internallink" href="user{{Id}}.html">{{DisplayName}}</a></span>{{/Id}}""",

    "comment":\
u"""<div class=\"comment container\">{{#User}}{{>userplate}}{{/User}}{{{Text}}}</div>""",

    "answer":\
u"""<div class=\"answer post container\">
<a class="internallink answerlink" name="{{Id}}" href="#{{Id}}">¶</a>
<span class=\"score\">{{Score}}</span>
{{#accepted}}<span class=\"scoreaccepted\">X</span>{{/accepted}}
<div class=\"answer body\">{{{Body}}}</div>
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
<span class=\"postdate\">{{LastActivityDate}}</span>
<br style="line-height:2em;" />
{{#comments}}{{>comment}}{{/comments}}
</div>""",

    "answers":\
u"""{{#answers}}
{{>answer}}
{{/answers}}""",
    
    "question":\
u"""
<div class=\"tag\"><span class=\"tag post\">
Tags:
{{#Tags}}
<a class="internallink" href="tag{{Id}}.html">{{TagName}}</a>
{{/Tags}}
</span></div>
<div class=\"question post container\">
<h1>{{Title}}</h1>
<div class=\"score\">{{Score}}</div>
<div class=\"question body\">{{{Body}}}</div>
{{#OwnerUser}}{{>userplate}}{{/OwnerUser}}
{{#LastEditorUser}}{{>userplate}}{{/LastEditorUser}}
<span class=\"postdate\">{{LastActivityDate}}</span>
<br style="line-height:2em;" />
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
    {{>question}}
    {{>answers}}
  </body>
</html>"""
    }

def make_renderer():
    renderer=pystache.Renderer(partials=templates,missing_tags="strict")
    return renderer
