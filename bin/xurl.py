#!/usr/bin/env python

"""A program to do something

Detailed documentation
"""

__author__ =	"William McVey"
__date__ = 	"24 May, 2004"
__revision__ =	"$Id:$"


import os
import sys
import lxml.etree
import urlparse
import re

class HTML:
	def __init__(self, text):
		self.tree = lxml.etree.HTML(text)

	def urls(self):
		urls = []
		try:
			base = tree.find("base").attrib["href"]
		except:
			base = ""
		for anchor in self.tree.xpath("//a[@href]"):
			url = urlparse.urljoin(base, anchor.attrib["href"])
			urls.append(url)
		return urls

if __name__ == '__main__':
	import sys
	import os
	from optparse import OptionParser       # aka Optik

	Progname=os.path.basename(sys.argv[0])
	Usage="""\
%prog usage: XXX:
%prog usage: -h
%prog usage: -V 
"""
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	# optparser.add_option("-v", "--verbose", dest = "verbose",
	#   action="store_true", help="be verbose")
	#optparser.add_option("-N", "--name", dest="var_n", 
	#  action= "store" | "append" | "store_true" | "store_false" 
	#  type = "int"
	#  default="foo", metavar="SOME_STRING", help="store a string")
	(options, params) = optparser.parse_args()

	p = HTML(sys.stdin.read())
	for url in p.urls():
		print url
