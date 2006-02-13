#!/usr/bin/env python

"""A "haven" client

Mostly a toy to play with sockets running under threads
"""

__author__ =	"William McVey"
__date__ = 	"4 February, 2005"
__revision__ =	"$Id:$"

import os, sys, logging, thread, time, re, ConfigParser
import socket, telnetlib

import AnsiColor

try:
	import readline
except:
	sys.stderr.write("No readline module available.  No tab completion.\n")


class haven_config_file(ConfigParser.ConfigParser):
	"""Process a config file for the haven client
	"""

	def __init__(self, site, configfile):
		ConfigParser.ConfigParser.__init__(self)
		self.read(os.path.expanduser(configfile))
		self.site = site
		try:
			if self.has_section(site):
				self.host, self._port_str = self.get(site, "site").split(":")
			else:
				self.add_section("site")
				self.host, self._port_str = site.split(":")
		except:
			raise RuntimeError, "Couldn't find hostname and port for site %s"% site

	def Port(self):
		return int(self._port_str)

	def Log(self):
		return self.getboolean(self.site, "log")

	def Hilights(self):
		"""Returns the list of regexs to hilite in the client, along with
		prefered coloring for the matching lines.
		
		The list returned is composed of (regex_obj, color) tuples, where
		regex_obj is a regex object to search on, and color is a tuple of the
		form (fg_color, bg_color)
		"""
		regex_strings, color, hilights, hilight_string = "", "", "", ""
		try:
			regex_strings = self.get(self.site, "private_mesg")
			color = eval(self.get(self.site, "private_color"))
			hilights= [(re.compile(pattern), color) for pattern in eval(regex_strings)]
		except:
			raise RuntimeError, "Error parsing private mesg definitions on " \
			   "%s: private_mesg pattern=%s, private_color=%s, list=%s" % (
			     self.site, regex_strings, color, hilights)
		try:
			hilight_string = self.get(self.site, "hilight")
			hilights.extend([(re.compile(pattern), color) for pattern, color in eval(hilight_string)])
		except:
			raise RuntimeError, "Error parsing hilight definitions on %s: " \
			    "hilight=%s, list=%s" % (self.site, hilight_string, hilights)
		return hilights

	def Gags(self):
		"""Return a list of regex objects that should be gagged
		"""
		gag_string = ""
		try:
			gag_string = self.get(self.site, "gag")
			return [re.compile(pattern) for pattern in eval(gag_string)]
		except:
			raise RuntimeError, "Error parsing gag definitions on %s: " \
			    "gag=%s" % (self.site, gag_string)


class haven_client:
	def __init__(self, host, port, log=False, hilights = [], gags=[]):
		self.hilights = hilights
		self.gags = gags
		self.log = logging.getLogger("haven_client")
		self.homedir = os.path.join(os.environ.get("HOME", "/home"), ".ah")
		self.histfile=os.path.join(self.homedir, "history")
		self.logfile=os.path.join(self.homedir, "logfile")
		try:
			readline.read_history_file(self.histfile)
		except IOError:
			pass
		if log:
			handler = logging.FileHandler(self.logfile, "a")
			handler.setLevel(logging.DEBUG)
			self.log.addHandler(handler)
		self.log.info("Connecting to %s:%s at %s", host, port, time.asctime())
		self.sock = socket.socket()
		self.sock.connect((host, port))

		thread.start_new_thread(self.reader, ())
		while 1:
			line = raw_input()
			if not line:
				continue
			if line in (":-)", ":-/", ":-(", ":(", ":)", ":-*"):
				line = ":" + line
			if line == "/quit":
				break
			self.sock.sendall(line + '\r\n')

	def reader(self):
		"""Read from the socket and display to UI
		"""
		try:
			data = ""
			while True:
				try:
					data += self.sock.recv(1024)
				except EOFError:
					print '*** Connection closed by remote host ***'
					return
				self.log.debug("Received: %s", repr(data))
				lines = data.split('\n')
				if lines[-1] != "":
					# we got an incomplete line read from the socket
					data = lines[-1]
				else:
					data = ""
				for line in lines[:-1]:
					self.log.debug("Processing: %s", repr(line))
					self.display(line)
		except:
			self.log.critical("Exception in reader:", exc_info=1)

	def display(self, line):
		"""emit a read in line to the output"""
		# ZZZ: should really be a class of it's own, supporting multiple interface
		# types (e.g. dump display, curses, gui)
		for regex_obj in self.gags:
			match = regex_obj.search(line)
			if match:
				self.log.debug("found gag %s so skipping: %s", `match.group()`, `line`)
				return
		for regex_obj, (fg_color, bg_color) in self.hilights:
			if regex_obj.search(line):
				line= AnsiColor.colorize(fg_color, bg_color, line)
				break
		self.log.debug("Displaying: %s", repr(line))
		line = self.process_timestamp(line)
		if line:
			sys.stdout.write(line +"\n")
		else:
			sys.stdout.flush()

	def process_timestamp(self, line):
		return AnsiColor.colorize("white", None, time.strftime("[%H:%M:%S] "))+ line


if __name__ == '__main__':
	import sys
	import os
	from optparse import OptionParser       # aka Optik

	Progname=os.path.basename(sys.argv[0])
	Usage="%prog usage: [-C config] world\n" \
	      "%prog usage: -h\n" \
	      "%prog usage: -V\n"
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	optparser.add_option("-d", "--debug", dest = "debug", 
	    action="store_true", help="log debugging messages")
	optparser.add_option("-C", "--config", dest="config", 
	    action= "store", default="~/.haven/config", metavar="CONFIGFILE", 
	    help="config file specifying haven worlds and parameters "
	         "(default is ~/.haven/config)")
	(options, params) = optparser.parse_args()

	root_log = logging.getLogger()          # grab the root logger
	root_log.setLevel((logging.INFO, logging.DEBUG)[options.debug == True])
	handler = logging.StreamHandler()
	# handler = logging.FileHandler(options.logfile) 
	logformat = "%(name)s: %(levelname)s: %(message)s"
	handler.setFormatter(logging.Formatter(logformat))
	# logformat = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
	#handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
	root_log.addHandler(handler)
	log = logging.getLogger(Progname)

	if len(params) != 1:
		log.critical("Must specify a haven to connect to (either one listed in the config, or a host:port")
		sys.exit(1)
	
	config = haven_config_file(params[0], options.config)
	ah =  haven_client(host = config.host, port=config.Port(), log=config.Log(),
	    hilights=config.Hilights(), gags=config.Gags())
	sys.exit(0)
