#!/usr/bin/python
# -*- coding:utf-8 -*-

# templates are in mustache format
templates={
    "date":\
u"""<span class=\"date\">{{Date}}</span><span class=\"time\">{{Time}}</span>""",
    
    "userplate":\
    u"""{{#Id}}<span class=\"user\"><a class="internallink" href="{{IdPath}}">{{#RenderDate}}{{>date}}{{/RenderDate}}{{DisplayName}}</a><br/>{{#ReputationHumanReadable}}<span class="reputation">{{ReputationHumanReadable}}</span>{{/ReputationHumanReadable}}<span class="class1">{{#NumBadges}}{{Class1}}{{/NumBadges}}</span><span class="class2">{{#NumBadges}}{{Class2}}{{/NumBadges}}</span><span class="class3">{{#NumBadges}}{{Class3}}{{/NumBadges}}</span></span>{{/Id}}""",
    
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
<a class="internallink" href="{{IdPath}}">{{TagName}}</a>
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
    <link href="{{RootDir}}se.css" rel="stylesheet" type="text/css">
  </head>
  <body>
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="{{IdPath}}">Next Question</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="{{IdPath}}">Prev Question</a>{{/PrevPage}}
<a class="internallink" href="{{RootDir}}index_questions.html">Questions Index</a>
<a class="internallink" href="{{RootDir}}../index.html">Home</a>
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
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>Tag {{TagName}}</title>
    <link href="{{RootDir}}se.css" rel="stylesheet" type="text/css">
  </head>
  <body>
<div class="linkheader">
{{#NextPage}}<a class="internallink" href="{{IdPath}}">Next Tag</a>{{/NextPage}}
{{#PrevPage}}<a class="internallink" href="{{IdPath}}">Prev Tag</a>{{/PrevPage}}
<a class="internallink" href="{{RootDir}}index_tags.html">Tags Index</a>
<a class="internallink" href="{{RootDir}}../index.html">Home</a>
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
<p><a class="internallink" href="{{IdPath}}">{{Title}}</a></p>
{{/questions}}
<p>({{number_questions}} more questions with tag {{>tag}})</p>
  </body>
</html>
"""
    }

def strip_html(html):
    "Strip text between closing and opening html tags if it only consists of whitespace."
    # FIXME: this erroneously removes the newline in "<code>hello<div>\n</div>world</code>"
    new=[]
    CLOSED=0
    OPENED=1
    state=CLOSED
    i=0
    while i<len(html):
        ilast=i
        #print ilast,state
        if state==CLOSED:
            i=html.find("<",i)
            if i==-1:
                i=len(html)
            else:
                state=OPENED
            between=html[ilast:i]
            if between.strip()!="":
                new.append(between)
        elif state==OPENED:
            i=html.find(">",i)
            assert i>=0
            i+=1
            new.append(html[ilast:i])
            state=CLOSED
    assert state==CLOSED
    return "".join(new)

def escape_html(html):
    """Return html that has "&", "<", and ">" escaped.
TODO: search for and import a html-escaping function from a built-in Python module."""
    html = html.replace("&", "&amp;")
    html = html.replace("<", "&lt;")
    html = html.replace(">", "&gt;")
    return html

# Own Renderer, like pystache but faster
def _parse_template(fsplit,template_name):
    inst=[]
    while fsplit!=[]:
        head=fsplit[0]
        if type(head)==unicode or type(head)==str:
            def make_render_string(head,template_name):
                def render_string(funs,data,debug):
                    return head
                return render_string
            if head!="":
                inst.append(make_render_string(head,template_name))
            fsplit=fsplit[1:]
        elif head.mode in ("#","^"): #section and inverted section
            name=head.name
            # search for closing tag
            end_index=-1
            for i in range(1,len(fsplit)):
                if type(fsplit[i]) in (str,unicode): continue
                if fsplit[i].name==head.name and fsplit[i].mode=="/":
                    end_index=i
                    break
            assert end_index>0
            #print template_name
            #if template_name=="question":
            #    print head.mode,head.name
            #    print fsplit[1:end_index]
            inner_fun=_parse_template(fsplit[1:end_index],template_name)
            def make_render_section(name,inner_fun,template_name):
                def render_section(funs,data,debug):
                    try:
                        var=data[name]
                    except KeyError:
                        raise Exception("Cannot render template '%s' (path %s): variable '%s' not found in '%s'" % (str(template_name),", ".join(['{{'+d+'}}' for d in debug]),name,data.keys()))
                    try:
                        # this is a small hack to be able to use pysqlite2.dbapi2.Row like a dict. It provides the .keys()-method.
                        var.keys()
                        dict_like=True
                    except:
                        dict_like=False
                    if type(var)==list:
                        #print "list(",name,"):",var
                        #print "inner_fun",inner_fun
                        ret=[]
                        for i,e in enumerate(var):
                            er=inner_fun(funs,e,debug+["#"+name+"["+str(i)+"]"] if debug else debug)
                            ret.append(er)
                        return "".join(ret)
                    elif type(var)==dict or dict_like: 
                        return inner_fun(funs,var,debug+["#"+name+"[]"] if debug else debug)
                    else:
                        if var:
                            return inner_fun(funs,data,debug+["#"+name] if debug else debug)
                        else:
                            return ""
                return render_section
            def make_render_inverted(name,inner_fun,template_name):
                def render_inverted(funs,data,debug):
                    try:
                        var=data[name]
                    except KeyError:
                        raise Exception("Cannot render template '%s' (path %s): variable '%s' not found in '%s'" % (str(template_name),", ".join(['{{'+d+'}}' for d in debug]),name,data.keys()))
                    if var:
                        return ""
                    else:
                        return inner_fun(funs,data,debug+["^"+name] if debug else debug)
                return render_inverted
            if head.mode=="#":
                inst.append(make_render_section(name,inner_fun,template_name))
            elif head.mode=="^":
                inst.append(make_render_inverted(name,inner_fun,template_name))
            else:
                assert(False)
            fsplit=fsplit[end_index+1:]
        elif head.mode==">": #partial
            name=str(head.name)
            def make_render_partial(name,template_name):
                def render_partial(funs,data,debug):
                    if name not in funs:
                        raise Exception("Cannot render template '%s' (path %s): partial '%s' not found in '%s'" % (str(template_name),", ".join(['{{'+d+'}}' for d in debug]),name,funs.keys()))
                    return funs[name](funs,data,debug+[">"+name] if debug else debug)
                return render_partial
            inst.append(make_render_partial(name,template_name))
            fsplit=fsplit[1:]
        elif head.mode in ("","{"): #normal variable and non-escaped variable
            name=head.name
            if type(name)==unicode: #TODO: FIXME: hack to be able to use pysqlite2.dbapi2.Row, which only accepts strings as keys
                name=str(name)
            def make_render_variable(name,template_name,escaped):
                def render_variable_escaped(funs,data,debug):
                    try:
                        var=data[name]
                    except KeyError:
                        raise Exception("Cannot render template '%s' (path %s): variable '%s' not found in '%s'" % (str(template_name),", ".join(['{{'+d+'}}' for d in debug]),name,data.keys()))
                    return escape_html(unicode(var))
                def render_variable_unescaped(funs,data,debug):
                    try:
                        var=data[name]
                    except KeyError:
                        raise Exception("Cannot render template '%s' (path %s): variable '%s' not found in '%s'" % (str(template_name),", ".join(['{{'+d+'}}' for d in debug]),name,data.keys()))
                    return unicode(var)
                if escaped:
                    return render_variable_escaped
                else:
                    return render_variable_unescaped
            #mustache by default html-escapes all variables, and we do as well.
            escaped=head.mode==""
            inst.append(make_render_variable(name,template_name,escaped))
            fsplit=fsplit[1:]
        else:
            raise Exception("invalid mode",head.mode)
    def make_render_combination(inst,template_name):
        #print "inst(",template_name,")",inst
        def render_combination(funs,data,debug):
            return "".join([i(funs,data,debug) for i in inst])
        return render_combination
    return make_render_combination(inst,template_name)

class template_var:
    def __init__(self,var):
        if var.startswith("{{#"):
            assert var.endswith("}}")
            self.mode="#"
            self.name=var[3:-2]
        elif var.startswith("{{^"):
            assert var.endswith("}}")
            self.mode="^"
            self.name=var[3:-2]
        elif var.startswith("{{/"):
            assert var.endswith("}}")
            self.mode="/"
            self.name=var[3:-2]
        elif var.startswith("{{>"):
            assert var.endswith("}}")
            self.mode=">"
            self.name=var[3:-2]
        # an unescaped list/dict section doesn't make sense: "{{{#"
        # an unescaped inverted section doesn't make sense: "{{{^"
        # an unescaped closing tag doesn't make sense: "{{{/"
        # an unescaped partial-section doesn't make sense: "{{{>"
        elif var.startswith("{{{"):
            assert var.endswith("}}}")
            self.mode="{"
            self.name=var[3:-3]
        elif var.startswith("{{"):
            assert var.endswith("}}")
            self.mode=""
            self.name=var[2:-2]
        else:
            raise Exception("unknown variable mode",var)
    def __repr__(self):
        return "<template_var(%s%s) at 0x%x>" % (self.mode,self.name,id(self))

def parse_template(template,template_name=None):
    new=[]
    ilastnew=0
    i=0
    while i<len(template):
        if template.startswith("{{",i):
            if template.startswith("{{{",i):
                end=template.find("}}}",i)+3
            else:
                end=template.find("}}",i)+2
            varpat=template[i:end]
            new.append(template[ilastnew:i])
            new.append(template_var(varpat))
            i=end
            ilastnew=end
        else:
            i+=1
    new.append(template[ilastnew:i])
    return _parse_template(new,template_name)

def parse_template_old(template,template_name=None):
    fsplit=template.split("{{")
    new=[fsplit[0]]
    while True:
        fsplit=fsplit[1:]
        if fsplit==[]: break
        f=fsplit[0].split("}}")
        assert len(f)==2
        new.append(template_var(f[0]))
        new.append(f[1])
    return _parse_template(new,template_name)

def parse_templates(templates):
    funs={}
    for key in templates.keys():
        funs[key]=parse_template(templates[key],key)
    return funs

def make_own_renderer(templates,stripped_html=False):
    funs=parse_templates(templates)
    class helper:
        def render(self,template,data,debug=False):
            template_fun=parse_template(template)
            text=template_fun(funs,data,[""] if debug else [])
            if stripped_html:
                text=strip_html(text)
            return text
    return helper()

# pystache renderer
def make_pystache_renderer(templates,stripped_html=False):
    import pystache
    renderer=pystache.Renderer(partials=templates,missing_tags="strict")
    class helper:
        def render(self,template,data):
            text=renderer.render(template,data)
            if stripped_html:
                text=strip_html(text)
            return text
    return helper()

# set renderer here
#make_renderer=make_pystache_renderer
make_renderer=make_own_renderer

def render(template,data,debug=False):
    renderer=make_renderer({"template":template})
    if debug:
        text=renderer.render("{{>template}}",data,debug)
    else:
        text=renderer.render("{{>template}}",data)
    return text


if __name__=="__main__":
    renderer1=make_pystache_renderer(templates)
    renderer2=make_own_renderer(templates)
    data={"Id":-1,"DisplayName":"CommunityWiki","RenderDate":{"Date":"2016-01-01","Time":"00:00"},"ReputationHumanReadable":False,"NumBadges":False}

    def check():
        r1=renderer1.render("{{>userplate}}",data)
        r2=renderer2.render("{{>userplate}}",data)
        assert r1==r2,"r1!=r2 where\nr1=%s\nr2=%s" % (r1,r2)

    def main():
        import time
        start=time.clock()
        res=[]
        for i in range(3000):
            res.append(renderer2.render("{{>userplate}}",data,debug=True))
        print "main took %f seconds" % (time.clock()-start)

    check()
    main()

    print "'%s'" %(strip_html("   <a> x  </a> <a>  \t \n </a>   xc"),)
    print "'%s'" %(strip_html(" x  <a> x  </a> <a>  \t \n </a>   \t"),)

    s="<code>hello<div>\n</div>world</code>"
    print s
    print strip_html(s)
