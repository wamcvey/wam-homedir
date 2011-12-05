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

class ldap_user(object):
	"""Provide a more convienient object interface to returned LDAP values
	"""
	def __init__(self, ldap_results):
		if len(ldap_results) != 1:
			raise RuntimeError("Ldap result expected to be a list of length 1, got length %d" % len(ldap_results))
		self.dn, self.attr_dict = ldap_results[0]

	@property
	def attributes(self):
		"""lists the attributes this object knows about
		"""
		return sorted(self.attr_dict.keys())
	
	def __getattr__(self, key):
		try:
			val = self.attr_dict[key]
			if isinstance(val, list) and len(val) == 1:
				val = val[0]
			return val
		except:
			raise AttributeError("no info for key %r" % key)

	def __repr__(self):
		return "<ldap_user: %r>" % self.dn

class cisco_ldap(object):
	"""Easy interface to the Cisco LDAP servers
	"""
	LDAP_URL= 'ldap://ldap.cisco.com:389/'
	PEOPLE_BASE= "ou=active,ou=employees,ou=people,o=cisco.com"
	RESOURCE_BASE = "ou=resources,o=cisco.com"
	SCOPE = ldap.SCOPE_SUBTREE
	def __init__(self, retrieve_all=False, timeout=-1, resources=False):
		self.log = logging.getLogger(self.__class__.__name__)
		self.log.debug("Initializing against: %s", self.LDAP_URL)
		self.ldap = ldap.initialize(self.LDAP_URL)
		self.TIMEOUT = timeout		
		self.BASE = self.RESOURCE_BASE if resources else self.PEOPLE_BASE
		if retrieve_all:
			self.RETRIEVE = None		# pull all info
		else:
			self.RETRIEVE = ['uid','cn', 'title', 'description', 
			  'employeenumber', 'mail', 'manager', 'site', 
			  'mobile', 'telephonenumber', 'alternatephoneflag']
	
	def query(self, **kwargs):
		"""Issue a query against the LDAP server and return an iterator
		over the results.
		
		Keyword arguments to this function are treated as the parameters
		to search
		"""
		query_string = "(&%s)" % "".join(["(%s=%s)" % x for x in kwargs.items()])
		self.log.info("Querying: %r", query_string)
		self.log.debug("Searching: base=%s, scope=%s, query_string=%s"
		               " , attrlist=%s)", self.BASE, self.SCOPE,
			       query_string, self.RETRIEVE)
		id = self.ldap.search(self.BASE, self.SCOPE, query_string, self.RETRIEVE)
		while True:
			# we choose 'all=False' so that we get results as they
			# are available. The generator will simply block until
			# all results have been retrieved
			result_type, result_data = self.ldap.result(id, all=False, timeout=self.TIMEOUT)
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
	  help="Query on an arbitrary search expression (e.g. building=*Austin*)")
	optparser.add_option("-a", dest = "return_all",
	  action="store_true",
	  help="Return all available information (ordinarily, only a subset is returned")
	optparser.add_option("-l", dest = "return_list_uid",
	  action="store_true",
	  help="Only print the matching userid")
	optparser.add_option("-L", dest = "return_list_dn",
	  action="store_true",
	  help="Only print the matching distinguished name")
	optparser.add_option("-r", dest = "resources",
	  action="store_true", default=False,
	  help="Query for defined resources (e.g. conference rooms)")
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
	
	ldap_engine = cisco_ldap(retrieve_all=options.return_all, resources=options.resources)
	for results in ldap_engine.query(**query):
		user = ldap_user(results)
		if options.return_list_dn:
			print user.dn
		elif options.return_list_uid:
			print user.uid
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
