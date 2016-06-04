#!/usr/bin/python

# this is a small hack to make python package 'lxml' able to read multiple concatenated xml dumps.
import sys

f=sys.stdin

head='\xef\xbb\xbf<?xml version="1.0" encoding="utf-8"?>\r\n'

print "<foo>"

while True:
    a = f.readline()
    if a=="":
        break
    i=a.find(head)
    if i==-1:
        print a,
    else:
        print a[:i]+a[i+len(head):]

print "</foo>"
