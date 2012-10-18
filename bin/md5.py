#!/usr/bin/env python
# md5
# A short script to calculate md5 checksums
#
# William McVey <wam@cisco.com>
# Nov 20, 2002

import md5
import sys
import string

# stolen from test_md5.py
def hexstr(s):
	h = string.hexdigits
	r = ''
	for c in s:
		i = ord(c)
		r = r + h[(i >> 4) & 0xF] + h[i & 0xF]
	return r

if __name__ == '__main__':
	import getopt
	import sys
	import os

	Progname=os.path.basename(sys.argv[0])
	Version= "%(Progname)s: $Id:$" % vars()
	Usage="""\
%(Progname)s usage: [FILES]...
%(Progname)s usage: -h
%(Progname)s usage: -V""" % vars()
	Help="""%(Usage)s
FILES           filenames to compute a checksum on (default stdin)
-V              show version info
-h              show this message""" %  vars()

	try:
		opts, params = getopt.getopt(sys.argv[1:], "hV")
	except:
		sys.exit("%(Progname)s: invalid commandline.\n%(Usage)s" % vars())

	for (option, val) in opts:
		if option == "-h":
			print Help
			sys.exit(0)
		if option == "-V":
			print Version
			sys.exit(0)

	if len(params) == 0:
		sum=md5.new(sys.stdin.read())
		print hexstr(sum.digest())
		sys.exit(0)
		
	for f in params:
		#ZZZ: should catch exceptions from either the open or the read
		sum=md5.new(open(f).read())
		print hexstr(sum.digest()), f
