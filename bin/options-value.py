#!/usr/bin/env python
# options-value
# Calculate option values with today's (or some other) price 
#
# Prints something along the lines of:
#	Current Price:						stockprice
#	Total Number of options:			count / todaysvalue
#	Fully Vested options:				count / todaysvalue
#	Partially Vested options:			count / todaysvalue
#	Next Maturation:		YYYYmmDD	count / todaysvalue
#
# Expects a file in ~/lib/ named 'options' with the following format:
# grantdate(YYYYMMDD), ticker, count, purchaseprice, cooloff time(in months), mature time(in months)
#
# This program currently assumes Cisco-Style option grants.  This means 
# nothing vests until a cooloff period of time has passed.  At the year
# mark, a cooloff period's worth of options vest.  After that, an equal
# amount of options vest every month.
#
# This is wam's first python script.  May have some rough edges but 
# it is mostly functional.
# 
# William McVey
# June 2000
# $Id: options-value.py,v 2.2 2001/08/31 18:16:32 wam Exp wam $

import sys
import os.path
import urllib
import string
import re
import time
import fileinput

import OptionsValue

OptionsTicker = "CSCO"

def do_commandline():
	homedir=os.environ["HOME"]
	portfoliofile=homedir + "/lib/options"

	Usage = """\
%%prog usage: [-C configfile] [-p price] [-d YYYYmmDD] [-l]
%%prog usage: -V
%%prog usage: -h
-C configfile	Specify an options file (default: %s)
-V		show version number
-d YYYYmmDD	pretend it's this date
-p price	use this price
-c		execute as if in a CGI (set's REMOTE_USER to USER)
-l 		print a long report
-h		show this message""" % portfoliofile

	optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
	optparser.add_option("-C", dest="portfoliofile", 
	  action="store", default=portfoliofile,)
	optparser.add_option("-p", "--price", dest="price", 
	  action="store", type= "float")
	optparser.add_option("-d", "--date", dest="date", 
	  action="store", default = None)
	optparser.add_option("--cgi", dest="cgi", action="store_true")
	optparser.add_option("-l", "--long", dest="long", action="store_true")
	(options, params) = optparser.parse_args()

	if options.price:
		curprice = options.price
	else:
		curprice = float(OptionsValue.fetchCurPrice(OptionsTicker))

	if options.cgi: 
		#os.environ["REMOTE_USER"]=os.environ.get("USER", "unknown")
		os.environ["REMOTE_USER"]=os.environ.get("USER", "wam")
		do_cgi(curprice, cgi=0)
		sys.exit(0)

	portfolio = OptionsValue.OptionsPortfolio(options.portfoliofile, options.date) 
	portfolio.set_price(curprice)

	if options.long:
		OptionsValue.LongReport(portfolio)
		sys.exit(0)

	vestarray=portfolio.vestingsched.keys()
	vestarray.sort()

	# So my field width of 12 might be a bit optimistic... one can only hope
	print "%-40s $%-.3f" % ("Current Price:", curprice)
	print "%-40s %-8d / $%12.2f" % (
	  "Total Number of options:", 
	  portfolio.totalcount, portfolio.totalval)
	print "%-40s %-8.1f / $%12.2f" % ( 
	  "Fully Vested options:",
	  portfolio.totalfullvest, portfolio.totalfullval)
	print "%-40s %-8.1f / $%12.2f" % (
	  "Partially Vested options:", 
	  portfolio.totalpartvest, portfolio.totalpartval)
	print "%-40s %-8.1f / $%12.2f" % (
	  "Options pending vesting:", 
	  portfolio.totalpending, portfolio.totalpendval)
	print "Upcoming Vestings"
	for vest_date in vestarray:
		for vestpack in portfolio.vestingsched[vest_date]:
			(grantdate, vestcount, strikeprice) = vestpack
			profit = curprice - strikeprice
			if profit < 0: profit = 0
			print "%8s - %6.1f of %8s mature @$%6.2f / $%12.2f" % (
			  vest_date, vestcount, grantdate, strikeprice, profit*vestcount)

			  #",".join(portfolio.vestingsched[vest_date][2]), 
			  #portfolio.vestingsched[vest_date][0], 
			  #portfolio.vestingsched[vest_date][1]) 

#		print "%-8s - %14s matures %-8.1f / $%12.2f" % (
#		  vest_date,
#		  ",".join(portfolio.vestingsched[vest_date][2]), 
#		  portfolio.vestingsched[vest_date][0], 
##		  portfolio.vestingsched[vest_date][1]) 


def cgi_gen_value_table(user, curprice=None, date=None):
	portfoliofile= os.path.expanduser("~%s/lib/options" % user)
	portfolio = OptionsValue.OptionsPortfolio(portfoliofile, date) 
	portfolio.set_price(curprice)
	vestarray=vestingsched.keys()
	vestarray.sort()

	table=TableLite(border=1)
	table.append(TR(
	  TH("Current Price"), TD(BR()),
	  TD(BR()), TD("$%5.2f" % curprice)))
	table.append(TR(
	  TH("Total Number of options:"), TD(BR()),
	  TD(portfolio.totalcount), TD("$%5.2f" % portfolio.totalval)))
	table.append(TR(
	  TH("Fully Vested options:"), TD(BR()), 
	  TD(portfolio.totalfullvest), TD("$%5.2f" % portfolio.totalfullval)))
	table.append(TR(
	  TH("Partially Vested options:"), TD(BR()),
	  TD("%5.2f" % portfolio.totalpartvest), 
	  TD("$%5.2f" % portfolio.totalpartval)))
	table.append(TR(
	  TH("Options pending vesting:"), TD(BR()),
	  TD(portfolio.totalpending), TD("$%5.2f" % portfolio.totalpendval)))
	for pack in vestarray:
		table.append(TR(
		  TH("Next Maturation of #%s" % ",".join(portfolio.vestingsched[pack][2])), 
		  TD(pack),
		  TD(portfolio.vestingsched[pack][0]), 
		  TD("$ %.2f" % portfolio.vestingsched[pack][1])))
	return table

def cgi_gen_modparm_form(price=None, date=None):
	"""Print out form elements allowing users to tweak variables"""
	if date==None:
		nowtime=time.localtime(time.time())
	else:
		nowtime=time.strptime(date, "%Y%m%d")
	(year, month, day) = nowtime[:3]
	if price == None:
		try:
			price= fetchCurPrice("CSCO")
		except:
			price= "0.0"
		price= string.atof(price)
	paramform= Form()
	paramform.append("Date:")
	months=	[ 
		("January", "01"),
		("Febuary", "02"),
		("March", "03"),
		("April", "04"),
		("May", "05"),
		("June", "06"),
		("July", "07"),
		("August", "08"),
		("September", "09"),
		("October", "10"),
		("November", "11"),
		("December", "12") 
	]
	paramform.append(Select(
		months,
		name= "month",
		selected = months[month-1] 
	))
	days=[]
	for number in range(1,31):
		days.append("%02d" % number)
	paramform.append(Select(days, name = "day", selected = [ "%02d" % day ]))
	years=[]
	for number in range(year-10, year+20):
		years.append("%s" % number)
	paramform.append(Select(years, name='year', selected= ["%s" % year]))
	paramform.append(BR())
	paramform.append("Price: $ ")
	paramform.append(Input(name="price", value= "%.2f" % price) )
	paramform.append(BR())
	paramform.append(Input(type='submit', name='reset', value='Reset to default values'))
	paramform.append(BR())
	return paramform

def do_cgi(price=None, cgi=1, date=None):
	#user=os.environ.get("REMOTE_USER", "unknown")
	user=os.environ.get("REMOTE_USER", "wam")
	input=CGI.FieldStorage()

	if input.has_key("reset"):
		useDefault=1
	else:
		useDefault=0
	if input.has_key("price") and not useDefault:
		price=input["price"].value
		price= string.atof(price) 
	if price == None:
		try:
			price= fetchCurPrice("CSCO")
		except:
			price= "0.0"
		price= string.atof(price) 
	if input.has_key("year") and input.has_key("month") and input.has_key("day") and not useDefault:
		date=input["year"].value + input["month"].value+input["day"].value

	page=SimpleDocument()
	page.cgi= cgi
	page.title = "Options Value for %s" % user

	page.append(ciscoStdHeader(page.title))
	page.append(cgi_gen_modparm_form(price, date))
	page.append(HR())
	page.append(cgi_gen_value_table(user, price, date))
	page.append(HR())
	page.append(HREF(OptionsValue.editURL, "Option Portfolio Editor"))
	page.append(ciscoStdFooter())
	page.write()

def ciscoStdHeader(title):
	"""This is a placeholder until cfv.py can be integrated"""
	return Head(1, title)

def ciscoStdFooter():
	return ""

#
# Main Program
#
if __name__ == '__main__':
	from optparse import OptionParser
	import cgi as CGI
	nohtml=0
	try:
		from HTMLgen import * 
		import HTMLutil
	except:
		nohtml=1

	global Progname
	#from cfv import *		# import the cisco style, per eric

	Progname= os.path.basename(sys.argv[0])
	# support running as a CGI or as a standalone program
	if os.environ.has_key('HTTP_USER_AGENT'):
		if nohtml == 1:
			sys.exit("Failed to load HTMLgen\n")
		do_cgi()
	else:
		do_commandline()
