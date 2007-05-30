#!/usr/bin/env python
# xsl-grep
# A simple "grep-like" mechanism for initiating XPATH searches using
# an XSL stylesheet.
#
# William McVey <wam@cisco.com>
# May 09, 2003

def stylesheet(pattern, ret, namespace_options, xml=0, quote='"'):
	namespaces = {			# some common namespaces
		"xhtml": "http://www.w3.org/1999/xhtml",
		"xsl": "http://www.w3.org/1999/XSL/Transform",
		"fo": "http://www.w3.org/1999/XSL/Format"
	}
	if xml:
		method='method="xml" indent="yes" '
	else:
		method='method="text" '
	for ns in namespace_options:
		res = ns.split("=")
		if len(res) == 1:
			prefix, path = None, res[0]
		elif len(res) == 2:
			prefix, path = res
		else:
			raise RuntimeError, "Must specify a namespace prefix and specifier in definition of %s" % ns
		namespaces[prefix] =  path
	ns_string = ""
	for ns, url in namespaces.items():
		if ns:
			ns_string += 'xmlns:%s="%s"\n' % (ns, url)
	if namespaces.has_key(None):
		# specify default namespace last
		ns_string += 'xmlns="%s"\n' % namespaces[None]

	return """\
<?xml version="1.0" ?> 
<xsl:stylesheet version="1.0"
%(namespaces)s
 >
	<xsl:strip-space elements="*" />
	<xsl:output %(method)s encoding="UTF-8" />
	<xsl:template match="/">
		<xsl:for-each select=%(quote)s%(pattern)s%(quote)s>
			%(return)s
			<xsl:text>
</xsl:text>
		</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>
""" % { "pattern": pattern, "return": ret, "method": method, "quote": quote,
	"namespaces": ns_string,
}
	

if __name__ == '__main__':
	from optparse import OptionParser       # aka Optik
	import sys
	import os
	import tempfile
	import commands

	delim = ":"

	Progname=os.path.basename(sys.argv[0])
	Usage="""\
%(Progname)s usage: [-k] [-a attribute|-c] [--ns NS=URL] [-A xpath_expr]... [-d delim] xpath_expr FILE[...]
%(Progname)s usage: -h
%(Progname)s usage: -V""" % vars()

	optparser = OptionParser(usage=Usage, version="%prog: $Id: xsl-grep.py,v 1.11 2006/08/24 18:58:17 wam Exp $" )
	optparser.add_option("-k", "--keep", dest = "keep", action="store_true",
	  help="keep the stylesheet (and report the path on stderr)")
	optparser.add_option("-a", dest = "attribute", action="store",
	  help="show the specified attribute of the matching node, not the text",
	  metavar=" attribute"),
	optparser.add_option("-A", dest = "additional", action="append",
	  help="show the result of subsequent XPATH expressions relative to the matching nodes",
	  metavar=" xpath_expr", default=[])
	optparser.add_option("-c", "--copy", dest = "copy", action="store_true",
	  help="copy the entire matching node (not just the text)")
	optparser.add_option("--ns", dest = "namespaces", action="append",
	  help="add a namespace definition to the search (e.g. --ns fo=http://www.w3.org/1999/XSL/Format)", default = [], metavar=" [NS=]URL")
	optparser.add_option("-d", dest="delim", action="store",
	  help="delimiter to use to join returned values when using -A (default %s)"% delim,
	  metavar=" delim")
	optparser.remove_option("--version")    # we add our own that knows -V
	optparser.add_option("-V", "--version", action="version",
	  help="show program's version number and exit")

	(options, params) = optparser.parse_args()

	ret="""<xsl:value-of select="." />"""
	keep_stylesheet, xml_output = 0, 0
	if options.delim: delim = options.delim
	if options.keep:  keep_stylesheet = 1
	if options.copy:
		ret="""<xsl:copy-of select="current()" />""" 
		xml_output=1
	if options.attribute:
		ret="""<xsl:value-of select="@%s" />""" % options.attribute
	if options.additional:
		additional_query=['<xsl:value-of select="%s" />' % query for query in options.additional]
		delim_expr = '<xsl:text>%s</xsl:text>' % delim
		ret = ret + delim_expr + delim_expr.join(additional_query)
	
	if options.copy and options.attribute:
		sys.exit("%(Progname)s: invalid commandline. Only one of -c or -a can be specified" % vars())
	if len(params) < 2:
		sys.exit("%(Progname)s: invalid commandline.\n%(Usage)s" % vars())
	pattern=params[0]
	quote='"'
	if "'" in pattern and '"' in pattern:
		sys.exit("%(Progname)s: search pattern contains both single and double quotes" % vars())
	if '"' in pattern:
		quote = "'"
	tmpfile=tempfile.mktemp()
	open(tmpfile, "w").write(
	  stylesheet(pattern, ret, options.namespaces, xml=xml_output, quote=quote))

	for f in params[1:]:
		os.system("xsltproc %s %s" % (tmpfile, f))
	if keep_stylesheet:
		print >>sys.stderr, "Stylesheet used is", tmpfile
	else:
		os.remove(tmpfile)
