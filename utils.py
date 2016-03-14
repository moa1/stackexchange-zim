# Miscellaneous functions

from pysqlite2 import dbapi2 as sqlite3
import pystache
import rewriteurl

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

def select_user(cursor, Id):
    cursor.execute('select * from Users where Id=?', (Id,))
    user=cursor.fetchone()
    return user

def select_comments_for_post(cursor,PostId):
    cursor.execute('select * from Comments where PostId=? order by CreationDate', (PostId,))
    comments=cursor.fetchall()
    for comment in comments:
        comment["User"]=select_user(cursor,comment["UserId"])
        comment["Text"]=rewriteurl.rewrite_urls(cursor,comment["Text"],stackexchange_domain)
    
    return comments

def select_post(cursor,Id):
    cursor.execute('select * from Posts where Id=?', (Id,))
    post=cursor.fetchone()
    
    post["comments"]=select_comments_for_post(cursor,Id)

    post["OwnerUser"]=select_user(cursor,post["OwnerUserId"])
    post["LastEditorUser"]=select_user(cursor,post["LastEditorUserId"])

    post["Body"]=rewriteurl.rewrite_urls(cursor,post["Body"],stackexchange_domain)

    return post
