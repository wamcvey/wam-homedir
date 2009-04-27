#!/usr/bin/env python

"""Searches the Cisco LDAP for some information about a user
(a faster, and more complete directory search)
"""

__author__ =	"William McVey"
__date__ = 	"24 September, 2008"
__revision__ =	"$Id:$"


import os
import sys
import logging
import pprint

import ldap

class cisco_ldap:
	"""Easy interface to the Cisco LDAP servers
	"""
	LDAP_URL= 'ldap://ldap.cisco.com:389/'
	BASE= "ou=active,ou=employees,ou=people,o=cisco.com"
	SCOPE = ldap.SCOPE_SUBTREE
	def __init__(self, retrieve_all=False, timeout=False):
		self.log = logging.getLogger(self.__class__.__name__)
		self.ldap = ldap.initialize(self.LDAP_URL)
		self.TIMEOUT = timeout		
		if retrieve_all:
			self.RETRIEVE = None		# pull all info
		else:
			self.RETRIEVE = ['uid','cn', 'title', 'description', 
			  'employeenumber', 'mail', 'manager', 'site', 
			  'mobile', 'telephonenumber']
	
	def query(self, **kwargs):
		"""Issue a query against the LDAP server and return an iterator
		over the results.
		
		Keyword arguments to this function are treated as the parameters
		to search
		"""
		query_string = "(&%s)" % "".join(["(%s=%s)" % x for x in kwargs.items()])
		self.log.info("Querying: %r", query_string)
		id = self.ldap.search(self.BASE, self.SCOPE, query_string, self.RETRIEVE)
		while True:
			result_type, result_data = self.ldap.result(id, self.TIMEOUT)
			if not result_data:
				raise StopIteration()
			yield result_data


def main(argv=sys.argv, Progname=None):
	from optparse import OptionParser, SUPPRESS_HELP       # aka Optik

	# set up commandline arguments
	if not Progname:
		Progname=os.path.basename(argv[0])
	Usage="%prog usage: [-a|-l|-L] [--uid|--pattern] PATTERN\n" \
	      "%prog usage: -h\n" \
	      "%prog usage: -V" 
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	optparser.remove_option("--version")    # we add our own that knows -V
	optparser.add_option("-V", "--version", action="version",
	  help="show program's version number and exit")
	optparser.add_option("-d", "--debug", dest = "debug", 
	  action="store_true", help=SUPPRESS_HELP)
	optparser.add_option("-u", "--uid", dest = "query_userid",
	  action="store_true",
	  help="Query on userid (default is to query on common name)")
	optparser.add_option("--pattern", dest = "query_pattern",
	  action="store_true",
	  help="Query on an arbitrary search expression (e.g. site=*Austin*)")
	optparser.add_option("-a", dest = "return_all",
	  action="store_true",
	  help="Return all available information (ordinarily, only a subset is returned")
	optparser.add_option("-l", dest = "return_list_uid",
	  action="store_true",
	  help="Only print the matching userid")
	optparser.add_option("-L", dest = "return_list_dn",
	  action="store_true",
	  help="Only print the matching distinguished name")
	optparser.add_option("-v", "--verbose", dest = "verbose",
	  action="store_true", help="be verbose")
	(options, params) = optparser.parse_args(argv[1:])

	# set up logging environment
	root_log = logging.getLogger()          # grab the root logger
	if options.debug:
		root_log.setLevel(logging.DEBUG)
	elif options.verbose:
		root_log.setLevel(logging.INFO)
	else:
		root_log.setLevel(logging.WARN)
	handler = logging.StreamHandler()
	logformat = "%(name)s: %(levelname)s: %(message)s"
	handler.setFormatter(logging.Formatter(logformat))
	root_log.addHandler(handler)
	log = logging.getLogger(Progname)


	if options.query_userid and options.query_pattern:
		log.error("Can only specify one of --pattern or --uid")
		sys.exit(1)
	if options.return_list_dn and options.return_list_uid:
		log.error("Can only specify one of -l or -L")
		sys.exit(1)
	
	if options.query_pattern:
		query = dict(sub_pattern.split("=") for sub_pattern in params[0].split(","))
	elif options.query_userid:
		query = {"uid": params[0]}
	else:
		query = {"cn": params[0]}
	
	ldap_engine = cisco_ldap(retrieve_all=options.return_all)
	for results in ldap_engine.query(**query):
		if options.return_list_dn:
			print results[0][0]
		elif options.return_list_uid:
			print " ".join(results[0][1]["uid"])
		else:
			pprint.pprint(results)
			print

if __name__ == '__main__':
	progname=os.path.basename(sys.argv[0])
	try:
		main()
	except SystemExit, value:
		sys.exit(value)
	except:
		(exc_type, exc_value, exc_tb) = sys.exc_info()
		#sys.excepthook(exc_type, exc_value, exc_tb)	# if debugging
		sys.exit("%s: %s: %s" % (progname, exc_type.__name__, exc_value))
	sys.exit(0)
