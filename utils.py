# Miscellaneous functions

from pysqlite2 import dbapi2 as sqlite3

tempdir="temp/"
dbfile=tempdir+"stackexchange-dump.sqlite3"

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
