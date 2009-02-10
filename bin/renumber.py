#!/usr/bin/env python

"""A program to do something

Detailed documentation
"""

__author__ =	"William McVey"
__date__ = 	"1 October, 2004"
__revision__ =	"$Id:$"


import os
import sys
import re

if __name__ == '__main__':
	import sys
	import os
	from optparse import OptionParser       # aka Optik

	Progname=os.path.basename(sys.argv[0])
	Usage="""\
%prog usage: list_of_files
%prog usage: -h
%prog usage: -V 
"""
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	#optparser.add_option("-d", "--debug", dest = "debug", 
	#  action="store_true", help="log debugging messages")
	# optparser.add_option("-v", "--verbose", dest = "verbose",
	#   action="store_true", help="be verbose")
	#optparser.add_option("-N", "--name", dest="var_n", 
	#  action= "store" | "append" | "store_true" | "store_false" 
	#  type = "int"
	#  default="foo", metavar="SOME_STRING", help="store a string")
	(options, params) = optparser.parse_args()

	#if options.var_n:
	#	# do something
	
	file_pattern = re.compile(r'(.*[^0-9])([0-9]+)\.(jpe?g|wmv|mpe?g|avi)', re.IGNORECASE)
	longest_num = 0
	for param in params:
		match = file_pattern.search(param)
		try:
			prefix, num, ext = match.groups()
		except:
			print >>sys.stderr, "no match on pattern for:", param
		if len(num) > longest_num:
			longest_num = len(num)

	for param in params:
		match = file_pattern.search(param)
		if not match:
			continue
		prefix, num, ext = match.groups()
		new = "%s%0*d.%s" % (prefix, longest_num, int(num), ext)
		if new != param:
			os.rename(param, new)
			print "mv %s %s" % (param, new)
	

