#!/usr/bin/env python

"""A program to switch workspaces in Gnome (and possibly even KDE)

"""

__author__ =	"William McVey"
__date__ = 	"3 October, 2006"
__revision__ =	"$Id:$"


import os
import sys
import logging

import wnck, gtk

class Screen:
	def __init__(self):
		self.log = logging.getLogger(self.__class__.__name__)
		self.screen = wnck.screen_get_default()
		self.update_events()

	def current_workspace(self):
		"""Returns the number of the current workspace
		
		Workspaces are numbered starting at 0
		"""
		cur = self.screen.get_active_workspace()
		self.update_events()
		return cur.get_number()

	def workspace_count(self):
		"""Returns the count of active workspaces
		"""
		return self.screen.get_workspace_count()
	
	def activate_workspace(self, num):
		workspace = self.screen.get_workspace(num)
		workspace.activate(0)
		self.update_events()

	def activate_next_workspace(self, wrap=True):
		max = self.workspace_count()
		cur = self.current_workspace() 
		if not wrap and cur == max-1:
			# no-op, we are at the end of our list and don't wrap
			return False
		self.activate_workspace((cur+1) % max)
		return True

	def activate_prior_workspace(self, wrap=True):
		cur = self.current_workspace() 
		if not wrap and cur == 0:
			# no-op, we are at the start of our list and don't wrap
			return False
		max = self.workspace_count()
		self.activate_workspace((cur-1) % max)
		return True

	def list_workspaces(self):
		"""Return a list of workspace names
		"""
		return [self.screen.get_workspace(num).get_name()
		        for num in range(self.workspace_count())]
			
	
	def update_events(self):
		"""Clear out the event queue 
		
		per http://www.thescripts.com/forum/thread23046.html
		"""
		while gtk.events_pending():
			gtk.main_iteration()


def main(argv=sys.argv, Progname=None):
	from optparse import OptionParser       # aka Optik

	# set up commandline arguments
	if not Progname:
		Progname=os.path.basename(argv[0])
	Usage="%prog usage: [-n num|-N|-P]\n" \
	      "%prog usage: -l\n" \
	      "%prog usage: -h\n" \
	      "%prog usage: -V" 
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	optparser.remove_option("--version")    # we add our own that knows -V
	optparser.add_option("-V", "--version", action="version",
	  help="show program's version number and exit")
	optparser.add_option("-d", "--debug", dest = "debug", 
	  action="store_true", help="log debugging messages")
	optparser.add_option("-n", "--num", dest="workspace_num",
	  action="store", type="int", help="go to specified workspace")
	optparser.add_option("-N", "--next", dest="next_workspace",
	  action="store_true", help="go to next workspace")
	optparser.add_option("-P", "--prior", dest="prior_workspace",
	  action="store_true", help="go to prior workspace")
	optparser.add_option("-W", dest="wrap", default=True,
	  action="store_false", help="turn off workspace wrapping")
	optparser.add_option("-l", dest="list_workspaces",
	  action="store_true", help="list workspaces")
	(options, params) = optparser.parse_args(argv[1:])

	# set up logging environment
	root_log = logging.getLogger()          # grab the root logger
	root_log.setLevel((logging.INFO, logging.DEBUG)[options.debug == True])
	handler = logging.StreamHandler()
	logformat = "%(name)s: %(levelname)s: %(message)s"
	handler.setFormatter(logging.Formatter(logformat))
	root_log.addHandler(handler)
	log = logging.getLogger(Progname)

	if (bool(options.prior_workspace) + bool(options.next_workspace) + \
	    bool(options.workspace_num is not None)) > 1:
		log.critical("Only one of -N, -P, or -n options may be specified")
		sys.exit(1)
		

	screen = Screen()
	if options.list_workspaces:
		cur = screen.current_workspace()
		for count, workspace in enumerate(screen.list_workspaces()):
			print "%d: %s %s" % (count+1, [" ", "*"][cur == count],
			                     workspace)
		sys.exit(0)

	if options.prior_workspace:
		screen.activate_prior_workspace(wrap=options.wrap)
	elif options.next_workspace: 
		screen.activate_next_workspace(wrap=options.wrap)
	elif options.workspace_num is not None:
		try:
			screen.activate_workspace(options.workspace_num + 1)
		except:
			exc_type, exc_val, exc_tb = sys.exc_info()
			log.critical("Couldn't activate workspace %d: %s",
			  options.workspace_num, exc_val)
			sys.exit(2)
	sys.exit(0)

if __name__ == '__main__':
	progname=os.path.basename(sys.argv[0])
	try:
		main()
	except SystemExit, value:
		sys.exit(value)
	except:
		(exc_type, exc_value, exc_tb) = sys.exc_info()
		# sys.excepthook(exc_type, exc_value, exc_tb)	# if debugging
		sys.exit("%s: %s: %s" % (progname, exc_type.__name__, exc_value))
	sys.exit(0)
