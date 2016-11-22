#!/usr/bin/python

# create SQL indices

from pysqlite2 import dbapi2 as sqlite3
from utils import *

if __name__=="__main__":
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()

    cursor.execute("create table if not exists PostsTags(PostId integer, TagId integer, primary key (PostId, TagId))")

    cursor.execute("create index if not exists Posts_OwnerUserId on Posts(OwnerUserId)")
    cursor.execute("create index if not exists Posts_ParentId on Posts(ParentId)")
    #cursor.execute("create index if not exists Posts_Score on Posts(Score)") # don't know how to sort it by numerical value, not string value.
    cursor.execute("create index if not exists Comments_PostId on Comments(PostId)")
    cursor.execute("create index if not exists Badges_UserId on Badges(UserId)")
    cursor.execute("create index if not exists Badges_Name on Badges(Name)")
    cursor.execute("create index if not exists PostsTags_TagId on PostsTags(TagId)")
    
    connection.close()
