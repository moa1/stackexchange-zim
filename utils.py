# -*- coding:utf-8 -*-
# Miscellaneous functions

from pysqlite2 import dbapi2 as sqlite3
import rewriteurl
import math
from config import *
import datetime
from templates import escape_html

dbfile=tempdir+"/"+stackexchange_domain+".sqlite3"
file_path=tempdir+"/content/"+stackexchange_domain+"/"


def tuple_factory(cursor, row):
    return row

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

def insert_table_attributes(cursor,table_attributes):
    # write attributes into table Attributes
    cursor.execute("create table if not exists Attributes(Id integer primary key,TableName text,AttributeName text)")
    for table in table_attributes.keys():
        for attribute in table_attributes[table]:
            cursor.execute("insert into Attributes(TableName,AttributeName) values(?,?)",(table,attribute,))

def get_table_attributes(connection):
    "get table attributes read by createtables.py"
    table_attributes={}
    cursor=connection.cursor()
    cursor.execute("select TableName,AttributeName from Attributes")
    for row in cursor.fetchall():
        table=row[0]
        if table not in table_attributes:
            table_attributes[table]=[]
        table_attributes[table].append(row[1])
    return table_attributes

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
    d=l[0].split("-")
    months_en=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    d_readable=d[2]+" "+months_en[int(d[1])-1]+" "+d[0]
    t=l[1].split(":")
    t_readable=t[0]+":"+t[1]
    return {'Date':d_readable,'Time':t_readable}

def split_filename_into_subdirs(filename,length=3):
    """Split `filename` into a path hierarchy, each path at most `length` characters long, and return the tuple `(paths,basename,n_subdirs)`."""
    c=filename.split("/")
    if len(c)>=2:
        prefix="/".join(c[:-1])+"/"
    else:
        prefix=""
    filename=c[-1]
    c=filename.split(".")
    if len(c)>=2:
        ext=c[-1]
        filename=".".join(c[:-1])
    else:
        ext=""
        filename=filename
    l=[filename[x:x+3] for x in range(0,len(filename),length)]
    paths="/".join(l[:-1])
    basename=l[-1]
    if ext:
        complete_basename=basename+"."+ext
    else:
        complete_basename=basename
    n_subdirs=len(l)-1
    if paths:
        complete_paths=prefix+paths+"/"
    else:
        complete_paths=prefix
    tup=(complete_paths,complete_basename,n_subdirs)
    return tup

def convert_id_to_idpath(Id):
    path=str(Id)
    (paths,basename,n_subdirs)=split_filename_into_subdirs(path)
    return paths+basename

def convert_question_id_to_idpath(Id,rootdir):
    path=rootdir+"question/"+str(Id)+".html"
    (paths,basename,n_subdirs)=split_filename_into_subdirs(path)
    return paths+basename

def convert_user_id_to_idpath(Id,rootdir):
    path=rootdir+"user/"+str(Id)+".html"
    (paths,basename,n_subdirs)=split_filename_into_subdirs(path)
    return paths+basename

def convert_tag_id_to_idpath(Id,rootdir):
    path=rootdir+"tag/"+str(Id)+".html"
    (paths,basename,n_subdirs)=split_filename_into_subdirs(path)
    return paths+basename

def select_user(cursor, Id,rootdir):
    cursor.execute('select * from Users where Id=?', (Id,))
    user=cursor.fetchone()
    if user:
        cursor.execute('select (select count(*) from Badges where UserId=? and Class="1") as Class1,(select count(*) from Badges where UserId=? and Class="2") as Class2, (select count(*) from Badges where UserId=? and Class="3") as Class3', (Id,Id,Id))
        user["NumBadges"]=cursor.fetchone()
        if user["Reputation"]:
            user["ReputationHumanReadable"]=format_number_human_readable(int(user["Reputation"]))
        user["RenderDate"]=None
        user["RootDir"]=rootdir
        user["IdPath"]=convert_user_id_to_idpath(user["Id"],rootdir)
    return user

def select_comments_for_post(cursor,PostId,rootdir):
    cursor.execute('select * from Comments where PostId=? order by CreationDate', (PostId,))
    comments=cursor.fetchall()
    for comment in comments:
        comment["User"]=select_user(cursor,comment["UserId"],rootdir)
        comment["Text"]=escape_html(comment["Text"]) #escape before rewriting, and export un-escaped, so that "<" and "&" are escaped, but links are clickable
        comment["Text"]=rewriteurl.rewrite_urls_in_text(cursor,comment["Text"],stackexchange_domain,rootdir)
        if comment["User"] and comment["CreationDate"]:
            comment["User"]["RenderDate"]=make_Date(comment["CreationDate"])
        if comment["Score"]=="0":
            comment["Score"]=None
    
    return comments

def select_post(cursor,Id,rootdir):
    cursor.execute('select * from Posts where Id=?', (Id,))
    post=cursor.fetchone()

    if not post:
        return None

    if Id in (7511791,7511795): #bugfix hack for stackoverflow.com
        post["Body"]=post["Body"].replace("<p></script></p>\n\n<p></body></p>\n\n<p></html></p>\n\n<p>No tags left unopened","<p></script></p>\n\n<p>&lt/body&gt</p>\n\n<p>&lt/html&gt</p>\n\n<p>No tags left unopened")

    post["Body"]=rewriteurl.rewrite_urls_in_html(cursor,post["Body"],stackexchange_domain,rootdir)
    post["OwnerUser"]=select_user(cursor,post["OwnerUserId"],rootdir)
    if post["OwnerUser"] and post["CreationDate"]:
        post["OwnerUser"]["RenderDate"]=make_Date(post["CreationDate"])
    if post["OwnerUser"]:
        post["OwnerUser"]["RootDir"]=rootdir
    post["LastEditorUser"]=select_user(cursor,post["LastEditorUserId"],rootdir)
    if post["LastEditorUser"] and post["LastEditDate"]:
        post["LastEditorUser"]["RenderDate"]=make_Date(post["LastEditDate"])
    if post["LastEditorUser"]:
        post["LastEditorUser"]["RootDir"]=rootdir
    if post["ClosedDate"]:
        post["ClosedDate"]=make_Date(post["ClosedDate"])

    post["RootDir"]=rootdir
    post["IdPath"]=convert_question_id_to_idpath(post["Id"],rootdir)

    post["comments"]=select_comments_for_post(cursor,Id,rootdir)

    return post

def estimated_time_arrival(start,i,total):
    """Return a datetime.datetime that is the estimated time of arrival, when processing started at `start`, and `i` out of `total` items have been processed."""
    if i<=0:
        return "NA"
    else:
        return start+datetime.timedelta(0,(datetime.datetime.now()-start).total_seconds()/i*total)
