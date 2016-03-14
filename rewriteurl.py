#!/usr/bin/python
# -*- coding:utf-8 -*-

from pysqlite2 import dbapi2 as sqlite3
from lxml import etree

def internal_url_for_question(cursor,question_id):
    cursor.execute('select Id,PostTypeId from Posts where Id=? and PostTypeId="1"',(question_id,))
    row=cursor.fetchone()
    if not row:
        return None
    return "question%i.html" % row["Id"]

def internal_url_for_answer(cursor,answer_id):
    cursor.execute('select Id,ParentId from Posts where Id=? and PostTypeId="2"',(answer_id,))
    row=cursor.fetchone()
    if not row:
        return None
    assert row["ParentId"] #if this happens, there is an error in the database or the stackexchange XML dumps.
    return "question%i.html#%i" % (int(row["ParentId"]),row["Id"])

def internal_url_for_comment(cursor,comment_id):
    cursor.execute("select Id,ParentId,PostTypeId from Posts where Id=(select PostId from Comments where Id=?)",(comment_id,))
    row=cursor.fetchone()
    if not row:
        return None
    if row["PostTypeId"]=="1":
        return "question%i.html" % (row["Id"],)
    elif row["PostTypeId"]=="2":
        return "question%i.html#%i" % (int(row["ParentId"]),row["Id"])
    elif row["PostTypeId"]=="4":
        cursor.execute("select Id from Tags where ExcerptPostId=?",(row["Id"],))
        row2=cursor.fetchone()
        if not row2:
            return None
        return "tag%i.html" % (row2["Id"],)
    elif row["PostTypeId"]=="5":
        cursor.execute("select Id from Tags where WikiPostId=?",(row["Id"],))
        row2=cursor.fetchone()
        if not row2:
            return None
        return "tag%i.html" % (row2["Id"],)
    else:
        return None

def internal_url_for_tag_name(cursor,tag_name):
    cursor.execute("select Id from Tags where TagName=?",(tag_name,))
    row=cursor.fetchone()
    if not row:
        return None
    return "tag%i.html" % (row["Id"],)


def internal_url_for_user(cursor,user_id):
    cursor.execute("select Id from Users where Id=?",(user_id,))
    row=cursor.fetchone()
    if not row:
        return None
    return "user%i.html" % (row["Id"],)

def safe_int(object,default=None):
    try:
        a=int(object)
    except ValueError:
        a=default
    return a

def internal_url_for_stackexchange_url(cursor,url,stackexchange_domain):
    "Return the internal url for the given `url` in the given `stackexchange_domain`, or None if there is no internal url for the `url`. Query the database accessible by `cursor` to validate that `url` points to an accessible object in the database, and return None otherwise."
    if url.startswith("http://"):
        url=url[7:]
    l=url.split("/")
    if len(l)<=0:
        return None
    if l[0]!=stackexchange_domain: #only accept urls with the given stackexchange_domain
        return None
#    print Id,ParentId,url
    if len(l)<=1:
        return None
    elif l[1] in ("q","questions"):
        if len(l)<=2:
            return None
        question_id=safe_int(l[2])
        if not question_id:
            return None
        return internal_url_for_question(cursor,question_id)
    elif l[1]=="a":
        if len(l)<=2:
            return None
        answer_id=safe_int(l[2])
        if not answer_id:
            return None
        return internal_url_for_answer(cursor,answer_id)
    elif l[1]=="posts":
        if len(l)<=2:
            return None
        elif l[2]=="comments":
            if len(l)<=3:
                return None
            comment_id=safe_int(l[3].split("?")[0])
            if not comment_id:
                return None
            return internal_url_for_comment(cursor,comment_id)
        else:
            return None
    #elif l[1]=="revisions": #maybe TODO: these seem to refer to PostHistory.xml
    elif l[1]=="tags":
        if len(l)<=2:
            return None
        tag_name=l[2]
        return internal_url_for_tag_name(cursor,tag_name)
    elif l[1]=="users":
        if len(l)<=2:
            return None
        user_id=safe_int(l[2])
        if not user_id:
            return None
        return internal_url_for_user(cursor,user_id)
    return None

def rewrite_urls(cursor,html,stackexchange_domain):
    "Given the HTML fragment `html`, replace stackexchange urls that point to `stackexchange_domain` by the corresponding internal urls if they exist in the database accessible using `cursor`."
    parser=etree.XMLParser(recover=True)
    # encapsulate the html in <body> tags so that the parser doesn't just parse the first tag
    root=etree.fromstring("<body>"+html+"</body>",parser)

    aiter=root.iter("a")
    for atag in aiter:
        href=atag.get("href")
        if href:
            href=href.strip()
            internal_url=internal_url_for_stackexchange_url(cursor,href,stackexchange_domain)
            if internal_url:
                #print href,internal_url
                #print Id,ParentId,href,internal_url
                atag.set("href",internal_url)
                # add the class "internallink" to the link, so that it will be displayed not in italics, but like an internal link.
                aclass=atag.get("class")
                if not aclass:
                    aclass="internallink"
                else:
                    aclass+=' internallink'
                atag.set("class",aclass)

    newhtml=etree.tostring(root)
    if newhtml=="<body/>":
        return ""
    assert newhtml.startswith("<body>") and newhtml.endswith("</body>")
    newhtml=newhtml[6:-7]
    return newhtml

if __name__=="__main__":
    from utils import *

    (connection,cursor)=init_db()

    with connection:
        cursor=connection.cursor()
        cursor.execute("select Id,ParentId,Body from Posts")
        #cursor.execute('select Id,ParentId,Body from Posts where Id=527')
        rows=cursor.fetchall()
        for row in rows:
            html=row["Body"]
            Id=row["Id"]
            ParentId=row["ParentId"]
            print Id,rewrite_urls(cursor,html,"blender.stackexchange.com")
