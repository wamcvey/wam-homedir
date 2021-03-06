@{
TESTED_MODULE=BASE[len("test_"):]
}#!/usr/bin/env python

"""A driver for testing the @(TESTED_MODULE) module
"""

__author__ =	"@(NAME)"
__date__ = 	"@(DAY) @(MONTH), @(YEAR)"
__revision__ =	"$Id:$"


import os
import sys
import unittest
import inspect

def filename_in_testdir(filename):
	"""Return the pathname to the specified file relative to the 
	directory that this unittest was found in. (Good for locating
	datafiles)
	"""
	return os.path.join(
		os.path.dirname(inspect.getfile(filename_in_testdir)),
		filename)

# assumes this test module is located in 'tests' subdir relative to 
# module being tested
sys.path.insert(1, filename_in_testdir(".."))		
import @(TESTED_MODULE)

class Test_@(TESTED_MODULE)(unittest.TestCase):
	def setUp(self):
		pass
	
	def tearDown(self):
		pass
	
	# def test_DoSomething(self):
	#	self.failUnless(expr[, msg])
	#	self.failUnlessEqual(first, second[, msg])
	# 	self.failIfEqual( first, second[, msg])
	#	self.failUnlessAlmostEqual(first, second[, places[, msg]])
	# 	self.failIfAlmostEqual(first, second[, places[, msg]])
	#	self.failUnlessRaises(exception, callable, kwargs)
	#	self.failIf( expr[, msg])
	#	self.fail([msg])

def test(verbosity=0):
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(Test_@(TESTED_MODULE)))
	unittest.TextTestRunner(verbosity=verbosity).run(suite)

if __name__ == '__main__':
	import sys
	import os
	import logging
	from optparse import OptionParser       # aka Optik

	# set up commandline arguments
	Progname=os.path.basename(sys.argv[0])
	Usage="%prog usage: @(TESTED_MODULE) [-v [-v [-v]]]\n" \
	      "%prog usage: -h\n" \
	      "%prog usage: -V" 
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	optparser.remove_option("--version")    # we add our own that knows -V
	optparser.add_option("-V", "--version", action="version",
	  help="show program's version number and exit")
	optparser.add_option("-v", "--verbose", dest = "verbose",
	  action="count", help="be verbose (each -v adds more verbosity)")
	(options, params) = optparser.parse_args(sys.argv[1:])

	root_log = logging.getLogger()          # grab the root logger
	handler = logging.StreamHandler()
	logformat = "%(name)s: %(levelname)s: %(message)s"
	handler.setFormatter(logging.Formatter(logformat))
	root_log.addHandler(handler)

	test(verbosity=options.verbose)
