#!/usr/bin/python

import sys

# a brittle XML parser, with the advantage that memory consumption is constant.
class XMLParser:
    def __init__(self):
        self.tagstate=""
        self.currenttag=""

    def parse(self, buf):
        events=[]
        for c in buf:
            if c=="<":
                self.tagstate="<"
            elif c==">":
                self.tagstate=""
                (action,tagname,attributes)=self.tagfunction(self.currenttag+c)
                events.append((action,tagname, attributes))
                self.currenttag=""

            if self.tagstate=="<":
                self.currenttag+=c
        return events

    def tagfunction(self,tagtext):
        tagtext=tagtext.decode("UTF-8")
        i=tagtext.find(" ")
        tagname=tagtext[1:i]
        tagtext=tagtext[:1]+tagtext[i:]
        # parse attributes
        attributes={}
        action="" if tagname[0]!="/" else "end"
        while True:
            i=tagtext.find("=")
            if i==-1:
                if action=="":
                    if tagtext.replace(" ","")=="<>":
                        action="start"
                    else:
                        #print "tagtext",tagtext
                        assert tagtext.replace(" ","") in ("</>","<?>")
                        action="end"
                break
            assert tagtext[i+1]=='"' #TODO: read XML spec
            j=tagtext.find('"',i+2)
            attrname=tagtext[1:i].strip()
            attrvalue=self.contentdecode(tagtext[i+2:j])
            attributes[attrname]=attrvalue
            tagtext=tagtext[:1]+tagtext[j+1:]
        assert action!=""
        return (action,tagname,attributes)

    def contentdecode(self,attrvalue):
        # TODO: this function should replace all escaped text at once, not sequentially: a sequence of "&#x123"; could be replaced with "&lt;", leading to furth replacing with "<" in this function, which is an error.
        while True:
            i=attrvalue.find("&#x")
            if i==-1:
                break
            j=attrvalue.find(";",i)
            assert i!=-1
            code=int(attrvalue[i+3:j],16)
            s=unichr(code)
            #print "attrvalue:",attrvalue,"attrvalue[i+3:j]:",attrvalue[i+3:j],"s:",s
            attrvalue=attrvalue[:i]+s+attrvalue[j+1:]
        attrvalue=attrvalue.replace("&lt;","<")
        attrvalue=attrvalue.replace("&gt;",">")
        attrvalue=attrvalue.replace("&amp;","&")
        attrvalue=attrvalue.replace("&apos;","'")
        attrvalue=attrvalue.replace("&quot;",'"')
        #print attrvalue
        return attrvalue

def main(file):

    parser = XMLParser()
    block_size=100000
    while True:
        buf=file.read(block_size)

        events=parser.parse(buf)
#        for e in events:
#            print e
        if buf=="":
            break

if __name__=="__main__":
    main(sys.stdin)
