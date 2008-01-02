#!/usr/bin/env python

"""A program to do something

Detailed documentation
"""

__author__ =	"William McVey"
__date__ = 	"24 May, 2004"
__revision__ =	"$Id:$"


import os
import sys
import BeautifulSoup
import urlparse
import re

class HTML(BeautifulSoup.BeautifulSoup):
	def __init__(self):
		BeautifulSoup.BeautifulSoup.__init__(self)

	def urls(self):
		urls = []
		try:
			base = self.fetch(name="base")[0]["href"]
		except:
			base = ""
		for anchor in self.fetch("a", {"href": re.compile('.+')}):
			try:
				url = urlparse.urljoin(base, anchor["href"])
				urls.append(url)
			except:
				pass
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

	p = HTML()
	p.feed(sys.stdin.read())

	for url in p.urls():
		print url
