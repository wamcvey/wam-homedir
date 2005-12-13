#!/usr/bin/env python

"""A program to parse the trace request at fedex and return info

Detailed documentation should be written. For now, just invoke with
a -h option to get the commandline arguments. The format of the report can
very easily be modified by small changes in the embedded XSL stylesheet.
"""

__author__ =	"William McVey"
__date__ = 	"12 December, 2003"
__revision__ =	"$Id:$"


import os
import sys
import urllib
import libxml2, libxslt

class FedExTrack:
	# url="http://www.fedex.com/cgi-bin/tracking/?action=track&language=english&cntry_code=us&mime_type=xml&tracknumber=%s"
	url="http://www.fedex.com/Tracking?action=track&language=english&cntry_code=us&mime_type=xml&tracknumber=%s"
	xsl_report = """\
<?xml version="1.0" standalone="no" ?> 
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns="http://www.w3.org/1999/XSL/Transform">
	<xsl:strip-space elements="*" />
	<xsl:output method="text" encoding="UTF-8" /> 
	<xsl:template match="/trackingrequest/package">
<xsl:text/>Tracking Number:  <xsl:value-of select="@trackingnumber"/>
Ship Date:        <xsl:value-of select="shipdate"/>
<!-- Status:           <xsl:value-of select="statusdescription"/> -->
Delivered on:     <xsl:value-of select="deliverydatetime" /> 
Delivered to:     <xsl:value-of select="deliveredto" /> 
Signed for by:    <xsl:value-of select="signedforby" />
Location:         <xsl:value-of select="deliverylocation" />
Scans:
<xsl:text />
		<xsl:for-each select="scan">
			<xsl:text>     </xsl:text>
			<xsl:value-of select="description" />
			<xsl:value-of select="address" />
			<xsl:text>   (</xsl:text>
			<xsl:value-of select="date_time" />
			<xsl:text>)</xsl:text>
			<xsl:text>
</xsl:text>
		</xsl:for-each> 
	</xsl:template>
</xsl:stylesheet>  
"""


	def __init__(self, verbose=0):
		self.report_xsl = libxslt.parseStylesheetDoc(libxml2.parseDoc(self.xsl_report))
		self.verbose = verbose
	
	def report(self, track):
		track_xml = libxml2.parseDoc(self.fetch_page(track))
		newdoc = self.report_xsl.applyStylesheet(track_xml, None)
		if newdoc:
			return newdoc.children.serialize()
		return None
	
		
	def fetch_page(self, track):
		url=self.url % track
		if self.verbose:
			print >>sys.stderr, "Fetching:", url
		page =  urllib.urlopen(url).read()
		if self.verbose:
			print >>sys.stderr, "FedEx Returned:\n", page
		return page
	

if __name__ == '__main__':
	import sys
	import os
	from optparse import OptionParser       # aka Optik

	Progname=os.path.basename(sys.argv[0])
	Usage="""\
%prog TRACKNUMBER[...]
usage: %prog -h
usage: %prog -V"""
	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	#action= "store" | "append" | "store_true" | "store_false" 
	#type = "int"
	optparser.add_option("-v", "--verbose", dest="verbose", 
	  action = "store_true", help="be verbose")
	(options, params) = optparser.parse_args()

	error = 0
	f =  FedExTrack(verbose=options.verbose)
	for param in params:
		try:
			report = f.report(param)
			if report:
				print report
		except:
			print >>sys.stderr, "Error processing", param 
			error = 1
	sys.exit(error or 0)
