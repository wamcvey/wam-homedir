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

sys.path.insert(1,"..")		# assumes we're being run from a 'tests' subdir
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

def test():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(Test_@(TESTED_MODULE)))
	unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
	import sys
	import os
	import logging
	from optparse import OptionParser       # aka Optik

	root_log = logging.getLogger()          # grab the root logger
	handler = logging.StreamHandler()
	logformat = "%(name)s: %(levelname)s: %(message)s"
	handler.setFormatter(logging.Formatter(logformat))
	root_log.addHandler(handler)

	test()

