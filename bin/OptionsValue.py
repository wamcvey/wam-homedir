#!/usr/bin/env python
# OptionsValue.py
# functions and class definitions for options-value
#
# William McVey
# June 2001
# $Id: OptionsValue.py,v 2.0 2001/06/29 18:48:06 wam Exp $

import sys
import getopt
import os.path
import urllib
import string
import re
import time
import fileinput

optionsvalueURL="http://localhost/cgi-bin/options-value.py"
editURL="http://localhost/cgi-bin/edit-options-portfolio.py"

# jan starts at index 1 since gmtime starts at 1, index 0 is Dec
DaysPerMonths=(31, 31,28,31,30,31,30,31,31,30,31,30,31)


def IsLeapYear(year):
	if year % 400 == 0: return 1
	if year % 100 == 0: return 0
	if year % 4 == 0: return 1
	return 0


def fetchCurPrice(ticker):
	url="http://quotes.nasdaq.com/Quote.dll?page=multi&mode=Stock&symbol=" + ticker
	try:
		fPage = urllib.urlopen(url)
	except IOError:
		raise IOError, "error loading url: %s\n" % (url)
	page=fPage.read()
	pricematch=re.search("Last Sale:[^$]+\$(\&nbsp;)?(?P<price>[ .0-9]+)", page, re.M) 
	if pricematch == None:
		raise IOError, "can't find price in page: %s\n" % (url)
	return pricematch.group('price')

class OptionsPortfolio:
	marker = "# Updated by OptionsValue on " 
	def __init__(self, file=None, nowdate=None):
		self.price = None
		self.portfoliofile=file
		self.portfolio=[]
		if nowdate==None:
			self.nowtime=time.localtime(time.time())
		else:
			self.nowtime=time.strptime(nowdate, "%Y%m%d")

		self.totalcount= self.totalval= self.totalfullvest= 0
		self.totalfullval= self.totalpartvest= self.totalpartval= 0
		self.totalpending=  self.totalpendval = 0
		self.vestingsched = {}

		if file != None:
			self.parse(file)

	def parse(self, file=None, nowdate=None):
		if file != None:
			self.portfoliofile=file
		if self.portfoliofile == None:
			raise IOError, "OptionsPortfolio.parse() requires file\n"
		if nowdate != None:
			self.nowtime=time.strptime(nowdate, "%Y%m%d")
		for line in fileinput.input(self.portfoliofile):
			line=string.strip(line)
			if line == "": continue
			if line[0] == "#": continue
			line = line.split('#')[0].strip() # allow line comments
			optionpack = re.split('[\s,]+', line)
			try:
				(grantdate, ticker, count, sold, strikeprice, coolofftime, maturetime) = optionpack
			except:
				raise RuntimeError, "bad file format: %s line %d: %s\n" % (self.portfoliofile, fileinput.lineno(), line)
			count=string.atoi(count)
			sold=string.atoi(sold)
			strikeprice=string.atof(strikeprice)
			coolofftime=string.atoi(coolofftime)
			maturetime=string.atoi(maturetime)
			(fullvested, partialvested, pending) = vested(grantdate, count, strikeprice, coolofftime, maturetime, self.nowtime)
			nextvest = findNextVest(grantdate, count, coolofftime, maturetime, self.nowtime)

			optionpack=(grantdate, count, sold, strikeprice, coolofftime, maturetime, fullvested, partialvested, pending, nextvest)

			self.totalcount += count - sold
			self.totalfullvest += fullvested - sold
			self.totalpartvest += partialvested
			self.portfolio.append(optionpack)
			self.totalpending += pending

	def set_price(self, price):
		self.price = price
		self.totalval = 0
		for optionpack in self.portfolio:
			(grantdate, count, sold, strikeprice, coolofftime, maturetime, fullvested, partialvested, pending, nextvest) = optionpack
			profit = price - strikeprice
			if (profit < 0):
				profit = 0
			self.totalval += (count - sold) * profit
			self.totalfullval += (fullvested - sold) * profit
			self.totalpartval += partialvested * profit
			self.totalpendval += pending * profit

			if nextvest:
				(nextvestday, nextvestcount) = nextvest
				self.vestingsched.setdefault(nextvestday, []).append((grantdate, nextvestcount, strikeprice))
	#			(vestshares, vestcash, vestgrantday) = self.vestingsched.get(nextvestday, (0,0,[]))
	#			vestgrantday.append(grantdate)
	#			self.vestingsched[nextvestday] = (
	#			  vestshares + nextvestcount, 
	#			  vestcash + nextvestcount*profit,
	#			  vestgrantday)

			
	def write(self):
		lines=[]
		lines.append("%s %s\n" %( self.marker, time.asctime(time.localtime(time.time()))))
		for pack in self.portfolio:
			(grantdate, count, sold, strikeprice, coolofftime, maturetime, fullvested, partialvested, pending, nextvest) = pack
			# XXX: I should remove the ticker if it isn't going to be
			# used
			lines.append("%s, %s, %d, %d, %f, %d, %d\n" % (grantdate, "CSCO", count, sold, strikeprice, coolofftime, maturetime))
		file=open(self.portfoliofile, 'w')
		file.writelines(lines)
		file.close()
		return

def findNextVest(grantdate, count, coolofftime, maturetime, nowtime):
	"Returns a date string YYYYMMDD of the next vesting of an option pack"

	(nowyear, nowmonth, nowday) = nowtime[:3]
	granttime=time.strptime(grantdate, "%Y%m%d") 
	(grantyear, grantmonth, grantday) = granttime[:3]
	(year, month, day) = timedifference(granttime, nowtime)
	monthsaged=month + 12 * year
	if monthsaged >= maturetime:		
		# all shares have vested, no next vesting for this grant
		return None
	if monthsaged < coolofftime:		# vesting cooloff
		vestyear = grantyear
		vestmonth = grantmonth + coolofftime
		if vestmonth > 12:
			vestyear = vestyear + 1
			vestmonth = vestmonth - 12
		day= "%4d%02d%02d" % (vestyear, vestmonth, grantday)
		grantamount= 1.0 * count / maturetime * coolofftime
	elif nowday < grantday:
		grantamount= 1.0 * count / maturetime
		day= "%4d%02d%02d" % (nowyear, nowmonth, grantday)
	elif nowmonth+1 >  12:
		grantamount= 1.0 * count / maturetime
		day= "%4d%02d%02d" % (nowyear+1, 1, grantday)
	else:
		grantamount= 1.0 * count / maturetime
		day="%4d%02d%02d" % (nowyear, nowmonth+1, grantday) 
	return (day, grantamount)

def vested(grantdate, count, strikeprice, coolofftime, maturetime, nowtime):
	"returns the tuple of count of (fullvested, partialvested, pendingvested)"
	optionspermonth=1.0 * count / maturetime
	granttime=time.strptime(grantdate, "%Y%m%d")
	(years, months, days) = timedifference(granttime, nowtime)
	# if years >= 1:
	monthsaged = years * 12 + months
	if monthsaged >= coolofftime:
		fullvested= monthsaged * optionspermonth
		# partialvested= optionspermonth / nowtime[1]
		partialvested= optionspermonth / DaysPerMonths[nowtime[1]] * days
		if fullvested >= count:
			fullvested = count
			partialvested = 0
	else:
		fullvested= 0
		partialvested= monthsaged * optionspermonth + optionspermonth / DaysPerMonths[nowtime[1]] * days
	# pendingvested= count - fullvested - partialvested 
	pendingvested= count - fullvested 
	return (fullvested, partialvested, pendingvested)


# time1 is expected to be earlier than time2
def timedifference(time1, time2):
	"takes a 2 time tuples, returns integral years, months, and days different"
	(year1, month1, day1) = time1[0:3]
	(year2, month2, day2) = time2[0:3]
	if month2 > month1:		# in a month following the anniversery
		yeardiff=year2-year1
		if day2 >= day1:
			monthdiff= month2-month1
			daydiff=day2-day1
		else:
			monthdiff= month2-month1-1
			daydiff=day2 + DaysPerMonths[month2-1] - day1
			if year1 == year2 and month2 == 3:
				daydiff = daydiff + IsLeapYear(year1)
	elif month2 == month1 and day2 >= day1: # after anniversery for the year
		yeardiff=year2-year1
		monthdiff=0
		daydiff=day2 - day1
	else:					# not yet to anniversery for this calendar year
		yeardiff=year2-year1-1
		if day2 >= day1:
			monthdiff= 12-month1+month2
			daydiff=day2-day1
		else:
			monthdiff= 12-month1+month2-1
			daydiff=day2 + DaysPerMonths[month2-1] - day1
			if year1 == year2 and month2 == 3:
				daydiff = daydiff + IsLeapYear(year1)
	return (yeardiff, monthdiff, daydiff)


def LongReport(portfolio):
	print "%-40s $%-.3f" % ("Current Price:", portfolio.price)
	print "%9s %5s %6s %6s %9s %7s %9s %9s" % (
	 "GrantDate", "Count", "Strike", "Vested", "VestedVal",
	 "Partial", "Pending", "Next Vest")
	print "%9s %5s %6s %6s %9s %7s %9s %9s" % (
	     "="*9, "="*5, "="*6, "="*6, "="*9, "="*7, "="*9, "="*9)
	for pack in portfolio.portfolio:
		(grantdate, count, sold, strikeprice, coolofftime, maturetime,
		  fullvested, partialvested, pending, nextvest) = pack
		fullvested = int(fullvested)	# only vest in full shares
		if strikeprice < portfolio.price:
			sell_value = portfolio.price - strikeprice
		else:
			sell_value = 0.0
		if nextvest:
			nextvest = "%8s - %7.2f" % tuple(nextvest)
		print "%9s %5s %6.2f %6d %9.2f %7.1f %9.1f %s" % (
			grantdate, count-sold, strikeprice, fullvested-sold,
			(fullvested-sold) * sell_value,
			partialvested, pending, nextvest
		)
		
