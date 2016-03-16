# -*- coding:utf-8 -*-
# Miscellaneous functions

from pysqlite2 import dbapi2 as sqlite3
import pystache
import rewriteurl
import math

stackexchange_dump_path="/home/itoni/Downloads/stackexchange-to-zim-converter/blender.stackexchange.com/"
tempdir="temp/"
dbfile=tempdir+"stackexchange-dump.sqlite3"
stackexchange_domain="blender.stackexchange.com"

# TODO: FIXME: I think there is a bug in pystache. A template "{{& name}}" should unescape html according to "mustache(5) - Logic-less templates..html", but pystache does not do this. When this bug is reported/fixed, I should remove function unescape_html below and replace calls to it by correct pystache usage.

def unescape_html(string, quote=None):
    """The opposite of cgi.escape():
Replace special characters "&", "<" and ">" to HTML-safe sequences.
If the optional flag quote is true, the quotation mark character (")
is also translated."""
    string = string.replace("&amp;","&")
    string = string.replace("&lt;","<")
    string = string.replace("&gt;",">")
    if quote:
        string = string.replace("&quot;","\"")
    return string

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db():
    connection = sqlite3.connect(dbfile)
    connection.row_factory = dict_factory
    #connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return (connection,cursor)

def format_number_human_readable(number):
    "Returns a human-readable string representation of a number."
    # TODO: FIXME: this cannot handle floating-point numbers yet. E.g. format 1500 as "1.5k"
    if number==0:
        return "0"
    elif number<0:
        sign="-"
        number=-number
    else:
        sign=""
    log1000=math.log(number,1000)
    suffix_gt1=["","K","M","G","T"]
    suffix_lt1=["","m","µ","n","p"] #include "" so that indexing is easier
    i=int(math.floor(log1000))
    if i>=0:
        if i>=len(suffix_gt1):
            i=len(suffix_gt1)-1
        suffix=suffix_gt1[i]
    else:
        if -i>=len(suffix_lt1):
            i=-(len(suffix_lt1)-1)
        suffix=suffix_lt1[-i]
    number/=10**(i*3)
    rep=sign+"{:.0f}".format(number)+suffix
    return rep

def make_Date(date):
    "Format a stackexchange-date human-readably."
    l=date.split(".")[0].split("T")
    d=l[0]
    t=l[1]
    return {'Date':d,'Time':t}

def select_user(cursor, Id):
    cursor.execute('select * from Users where Id=?', (Id,))
    user=cursor.fetchone()
    if user:
        if user["Reputation"]:
            user["ReputationHumanReadable"]=format_number_human_readable(int(user["Reputation"]))
        user["RenderDate"]=None
    return user

def select_comments_for_post(cursor,PostId):
    cursor.execute('select * from Comments where PostId=? order by CreationDate', (PostId,))
    comments=cursor.fetchall()
    for comment in comments:
        comment["User"]=select_user(cursor,comment["UserId"])
        comment["Text"]=rewriteurl.rewrite_urls(cursor,comment["Text"],stackexchange_domain)
        if comment["User"] and comment["CreationDate"]:
            comment["User"]["RenderDate"]=make_Date(comment["CreationDate"])
    
    return comments

def select_post(cursor,Id):
    cursor.execute('select * from Posts where Id=?', (Id,))
    post=cursor.fetchone()
    
    post["Body"]=rewriteurl.rewrite_urls(cursor,post["Body"],stackexchange_domain)
    post["OwnerUser"]=select_user(cursor,post["OwnerUserId"])
    if post["OwnerUser"] and post["CreationDate"]:
        post["OwnerUser"]["RenderDate"]=make_Date(post["CreationDate"])
    post["LastEditorUser"]=select_user(cursor,post["LastEditorUserId"])
    if post["LastEditorUser"] and post["LastEditDate"]:
        post["LastEditorUser"]["RenderDate"]=make_Date(post["LastEditDate"])
    if post["ClosedDate"]:
        post["ClosedDate"]=make_Date(post["ClosedDate"])

    post["comments"]=select_comments_for_post(cursor,Id)

    return post
