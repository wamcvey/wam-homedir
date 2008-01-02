#!/usr/bin/env python

"""A program to [ZZZ:do_something]

[ZZZ: Detailed documentation]
"""

__author__ =	"William McVey"
__date__ = 	"12 October, 2005"
__revision__ =	"$Id:$"


import sys
import os, os.path
import stat
import time
import logging

class SinceQuery:
	"""Stores the current parameters associated with a particular
	file or directory, and is updated by the Lookup() method of 
	the SinceDB class with the parameters for this inode found
	in the .since status file
	"""

	DB_VERSION = "2"

	def __init__(self, filename, openfile=None):
		self.log = logging.getLogger(self.__class__.__name__)
		self.filename = filename
		self.DB_VERSION = self.DB_VERSION	# ZZZ: hack  __dict__
		if openfile:				# stdin, possibly a directory
			self.file = openfile
			filestat = os.fstat(self.file.fileno())
		elif os.path.isfile(filename):	# a file
			self.file = file(filename)
			filestat = os.fstat(self.file.fileno())
		else:							# likely, a directory pathname
			self.file = None
			filestat = os.stat(filename) 
		
		if stat.S_ISDIR(filestat.st_mode):
			self.SinceContents = self.SinceDirContents
			self.time = time.time() 	# for dirs, time is *now* - not last mod
			curdir = os.path.abspath(".")
		else:
			self.SinceContents = self.SinceFileContents
			self.time = filestat.st_mtime
		self.size = filestat.st_size
		self.inode = filestat.st_ino
		self.dev = filestat.st_dev
		
		# values retrieved from a db lookup
		self.old_size = None
		self.old_time = None
		self.db_offset = None

	def __str__(self):
		return "V%(DB_VERSION)s\n" \
		       "%(time)lx L%(size)lx I%(inode)x D%(dev)x" % self.__dict__

	def SetDBVals(self, seconds, length, offset):
		self.old_size = length
		self.old_time = seconds
		self.db_offset = offset

	def IsDir(self):
		"""Returns whether this query is for a directory
		"""
		return not self.file

	def IsModified(self):
		"""Has there been mods since the last invocation for this file?
		
		Returns 'new' if the Lookup of this query failed. Returns 'yes'
		if the old version was modified from current file. Returns empty
		if the file appears to be the same as before
		"""
		if self.db_offset == None:
			return "new"
		if self.IsDir():
			return "yes"
		if self.old_size == self.size and self.old_time == self.time:
			return ""
		return "yes"

	def DevInodeString(self):
		"""Returns the device id and inode for the device the queried file
		"""
		return "%d,%d/%d" % (os.major(self.dev), os.minor(self.dev), self.inode)

	def SinceFileContents(self, **kwargs):
		"""Returns contents of the file from the point of last execution
		to current end of file
		"""
		if not self.old_size:
			return self.file.read()
		if self.size < self.old_size:
			# file has likely been trunicated, output it from the start
			self.file.seek(0)
			return self.file.read()
		self.file.seek(self.old_size)
		return self.file.read()

	def SinceDirContents(self, seperator="\n", **kwargs):
		"""Returns a text block listing of all files which have changed
		since last time we scanned this directory
		"""
		dir_contents = os.listdir(self.filename)
		dir_contents.sort()
		if not self.old_time:
			return "".join(["%s%s" %(x, seperator) for x in dir_contents])
		path = self.filename
		return "".join(
			["%s%s"%(filename, seperator) for filename in dir_contents if
			  os.stat(os.path.join(path, filename)).st_ctime > self.old_time]
		) 


class SinceDB:
	DB_VERSION = "2"

	def __init__(self, filename, lock=True):
		self.log = logging.getLogger("SinceDB: %s" % filename)
		# the following is somewhat complicated by the fact that python's
		# file() initializer wrap's STDIO's fopen() function call, which can't
		# do the equivalent of O_CREAT|O_RDWR .  Bleh. 
		# This *should* work on UNIX as well as Win32 and Mac
		fd = os.open(filename, os.O_CREAT|os.O_RDWR)
		self.db_file = os.fdopen(fd, "r+")

	def Dispatch(self, filename):
		"""Passes off the filename argument to appropriate method, based
		on the type of file/dir it is
		"""
		if filename == "-":
			query = SinceQuery("stdin", sys.stdin)
		elif os.path.isdir(filename) or os.path.isfile(filename):
			query = SinceQuery(filename)
		else:
			raise RuntimeError, "%s: not a plain file or directory" % filename
		return self.Lookup(query)

	def Lookup(self, query):
		self.db_file.seek(0)
		lineno = -1
		offset = 0
		for status in self.db_file:
			info = self.db_file.next()
			lineno += 2
			if status.rstrip() != "V%s"%self.DB_VERSION :
				self.log.warn("Non V%s db format detected on line %d: %s", 
				  self.DB_VERSION, lineno, `status`)
				continue
			(seconds, length, inode, device) = info.rstrip().split()
			seconds = int(seconds, 16)
			length = int(length[1:], 16)
			inode = int(inode[1:], 16)
			device = int(device[1:], 16)
			if (query.inode == inode and query.dev == device):
				self.log.debug("Lookup found query: %s at %s", `query`, offset)
				query.SetDBVals(seconds, length, offset)
				break
			else:
				self.log.debug("Skipping offset %s at line %d: " \
				  "query.inode(%s) ? inode(%s) and? query.dev(%s) ? " \
				  "device(%s)", offset, lineno, query.inode, inode , 
				  query.dev , device)
			offset += len(status) + len(info)
		return query

	def Update(self, query):
		# XXX: seriously needs some file locking 
		if query.db_offset != None:
			self.log.debug("Updating... seeking off to %s", query.db_offset)
			# remove our old record
			self.db_file.seek(query.db_offset)
			results = self.db_file.readlines()[2:]
			self.log.debug("results are %s", `results`)
			self.db_file.truncate(query.db_offset) 
			self.db_file.seek(0, 2)
			map(self.db_file.write, results)
		print >>self.db_file, query
		


if __name__ == '__main__':
	import sys
	import os
	from optparse import OptionParser, SUPPRESS_HELP    # aka Optik

	# set up commandline arguments
	Progname=os.path.basename(os.path.splitext(sys.argv[0])[0])
	Usage="%prog usage: [-d] [-L] [-F DB_FILE] [-c SEP] [file_or_directory...]\n" \
	      "%prog usage: -h\n" \
	      "%prog usage: -V" 
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	optparser.add_option("-d", "--debug", dest = "debug", 
	  action = "store_true", help = "log debugging messages")
	optparser.add_option("-F", "--filename", dest = "sinceFilename",
	  action = "store", 
	  default=os.path.join(os.path.expanduser("~"), ".%s"%Progname),
	  help = "time stamp meta file / database", metavar = "DB_FILE")
	optparser.add_option("-c",  dest = "dirDelim",
	  action = "store", default="\n",
	  help = "output separator for filenames under -d", metavar = "SEP")
	optparser.add_option("-L", "--list", dest = "listOnly",
	  action = "store_true", default=False,
	  help = "list present status of each file (only)")
	optparser.remove_option("--version")	# we add our own that knows -V
	optparser.add_option("-V", "--version", action="version", 
	  help="show program's version number and exit")
	optparser.add_option("-n", dest = "print_output", default = True,
	  action = "store_false",
	  help="don't print file contents, just update db")
	(options, params) = optparser.parse_args()

	# set up logging environment
	root_log = logging.getLogger()          # grab the root logger
	root_log.setLevel((logging.INFO, logging.DEBUG)[options.debug == True])
	handler = logging.StreamHandler()
	logformat = "%(name)s: %(levelname)s: %(message)s"
	handler.setFormatter(logging.Formatter(logformat))
	root_log.addHandler(handler)
	log = logging.getLogger(Progname)

	sinceDB = SinceDB(options.sinceFilename)
	if not params:
		params = ["-"]
	printHeader = True
	try:
		for target in params:
			result = sinceDB.Dispatch(target)
			if options.listOnly:
				if printHeader:
					printHeader = False
					print "%-5s %14s %14s %16s %s" % (
					  "Mod", "Last-count", "Count", "Device/inode", "Name")
				print "%-5s %14s %14d %16s %s" % (
				  result.IsModified() or "no",
				  [result.old_size, "-"][result.old_size == None], 
				  result.size, result.DevInodeString(), target
				)
				continue
			if result.IsModified():
				sinceDB.Update(result)
			if options.print_output:
				sys.stdout.write(result.SinceContents(seperator=options.dirDelim))
	except:
		(exc_type, exc_value, exc_tb) = sys.exc_info()
		log.critical("%s: %s", exc_type.__name__, exc_value, exc_info=options.debug)
		sys.exit(1)
