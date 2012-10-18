#!/usr/bin/env python

"""Library to handle filtering my mail via pycmail
"""

__author__ =	"William McVey"
__date__ = 	"6 April, 2006"
__revision__ =	"$Id:$"


import logging, os, sys
from itertools import chain


# Generic utility definitions
HomeDir = os.path.expanduser("~")
GenericDir = lambda *x: os.path.join(HomeDir, "Maildir", "Generic", *x)
CiscoDir = lambda *x: os.path.join(HomeDir, "Maildir", "Cisco", *x)
WamberDir = lambda *x: os.path.join(HomeDir, "Maildir", "Wamber", *x)


# Specific special folders
SpamFolder = GenericDir("SPAM")

def DefaultFolder(defines):
    if "CISCO" in defines:
        return CiscoDir("INBOX", "wam-default")
    else:
        return WamberDir("wamber-default")

JunkOriginators = set([
    "ip@ip.org.tr",
    "newsletter@jobseekerweekly.com",
    "info@mafruce.com",
    "wtc01@wasotraining.net",
    "lumiere@planet.tn",
    'bilgi@ip.org.tr',
    'info@bluesuninfo.com',
    'dci@dcionline.com.br',
    'info@lounge125.com',
    'vip@soundforceprod.com',
    'tjslist@aol.com',
    'tooluxe@edt02.net',
    'noreply@thefederalmarketplace.com',
    'feedback@einnews.com',
    'eda_news_letter@edacafe.com',
    'admin@rethinkmarkets.com',
    'harrahs@thepoolharrahs.com',
    'info@oilandgasonline.com',
    'NoReply@fivefourclub.com',
    # not really *spammers*, but close enough to get filtered out
    'dell_epp@dellhome.usa.dell.com',
    'dell@dellhome.usa.dell.com',
    'messages@guidestar.org',
])

# These match on either recipients or sender (Mapped to lower case)
MailingListMappings = {
    # To WAM
    'wam':			CiscoDir("INBOX", "wam@cisco.com"),
    'wam@cisco.com':		CiscoDir("INBOX", "wam@cisco.com"),
    'group.rsmoak@cisco.com':	CiscoDir("INBOX", "wam@cisco.com"),
    'wam@wamber.net':		WamberDir("INBOX", "wam@wamber.net"),
    
    # Important projects/lists
    'srocollect@cisco.com':	CiscoDir("INBOX", "sro-collect"),
    'ai-minions@cisco.com':	CiscoDir("INBOX", "ai-minions"),

    # Topics
    'dns-security@cisco.com':	CiscoDir("Topic", "DNS-Security"),
    "vulnwatch@vulnwatch.org":	CiscoDir("Topic", "Bugs"),
    "full-disclosure@lists.grok.org.uk": CiscoDir("Topic", "Bugs"),
    "bugtraq@securityfocus.com":	CiscoDir("Topic", "Bugs", "BugTraq"),
    "sie-open-source-security@cisco.com": CiscoDir("Topic", "Bugs", "SIE-Open-Source"),
    "vuln-dev@securityfocus.com":	CiscoDir("Topic", "Bugs", "Vuln-dev"),
    "ipv6-deployment@cisco.com":	CiscoDir("Topic", "IPv6"),
    "ipv6-interest@cisco.com":	CiscoDir("Topic", "IPv6"),
    "attack-tools@cisco.com":	CiscoDir("Topic", "Tools"),
    "cool-tools@cisco.com":	CiscoDir("Topic", "Tools"),
    "oval-developer-list@lists.mitre.org": CiscoDir("Topic", "OVAL"),
    "oval-discussion-list@lists.mitre.org": CiscoDir("Topic", "OVAL"),
    "oval-board-list@lists.mitre.org": CiscoDir("Topic", "OVAL"),
    "spa-ops@cisco.com":		CiscoDir("Topic", "SPA"),
    "spadev@cisco.com":		CiscoDir("Topic", "SPA"),
    "spacvs-autospa@cisco.com":	CiscoDir("Topic", "SPA"),
    "stat@cisco.com": 		CiscoDir("Topic", "STAT"), 
    "sub-stat@cisco.com": 	CiscoDir("Topic", "STAT"), 
    "stat-tools-dev@cisco.com":	CiscoDir("Topic", "STAT"),
    "internal-security-announce@cisco.com": CiscoDir("Topic", "PSIRT"),
    "psirt-legal@cisco.com":	CiscoDir("Topic", "PSIRT"),
    "psirt-pr@cisco.com":	CiscoDir("Topic", "PSIRT"),
    "security-tiger-team@cisco.com": CiscoDir("Topic", "PSIRT"),
    "psirt@cisco.com":		CiscoDir("Topic", "PSIRT", "inbox"),
    "psirt-tta@cisco.com":	CiscoDir("Topic", "PSIRT", "psirt-tta"),
    "cdetsprod@cisco.com":	CiscoDir("Topic", "PSIRT", "cdetsprod"),
    "scapy.ml@secdev.org":	CiscoDir("Topic", "Scapy"), 
    "pycon-organizers@python.org":  CiscoDir("Topic", "PyCon"),

    # Troll lists
    "vim-trolls@cisco.com":	CiscoDir("Topic", "Trolls", "VIM-Trolls"),
    "ssh-trolls@cisco.com":	CiscoDir("Topic", "Trolls", "SSH-Trolls"), 
    "python-trolls@cisco.com":	CiscoDir("Topic", "Trolls", "Python-Trolls"), 

    # HR Related lists
    "group.gamoore@cisco.com":	CiscoDir("Topic", "Organizational"), 
    "group.welfrink@cisco.com":	CiscoDir("Topic", "Organizational"), 
    "group.pasethi@cisco.com":	CiscoDir("Topic", "Organizational"), 
    "group.chambers@cisco.com":	CiscoDir("Topic", "Organizational"), 

    # Mailing lists that fall outside of topics
    "intellishield-sources@cisco.com":	CiscoDir("Lists", "Intellishield-Sources"),
    "cs-security@cisco.com":	CiscoDir("Lists", "CS-Security"),
    "py-dev@codespeak.net":	CiscoDir("Lists", "Py-Dev-Codespeak"), 
    "service.plan.tool@cisco.com":	CiscoDir("Lists", "Service.Plan.Tool"),
    "attack-interest@cisco.com":	CiscoDir("Lists", "Attack-Interest"),
    "intelservices-discuss@cisco.com": CiscoDir("Lists", "Intelservices-discuss"),
    "it-flame@cisco.com":           CiscoDir("Lists", "it-flame"),
    "ciag-interest@cisco.com":	CiscoDir("Lists", "CIAG-Interest"),
    "xmleditor-support@xmlmind.com": CiscoDir("Lists", "XXE"), 
    "xep-support@renderx.com":	CiscoDir("Lists", "XEP"), 
    "sans-qualys@qualys.com":	CiscoDir("Lists", "SANS-Qualsys"), 
    "ms-secnews@securityfocus.com":	CiscoDir("Lists", "MS-SecNews"),
    "python-announce@python.org":	CiscoDir("Lists", "Python-Announce"), 
    "python-list@python.org":	CiscoDir("Lists", "Python-Announce"), 
    "python-announce-list@python.org": CiscoDir("Lists", "Python-Announce"),
    "comp-lang-python-announce@moderators.isc.org": CiscoDir("Lists", "Python-Announce"),
    "nessus@list.nessus.org":	CiscoDir("Lists", "Nessus"),
    "nessus-devel@list.nessus.org": CiscoDir("Lists", "Nessus"),
    "nmap-dev@insecure.org":	CiscoDir("Lists", "Nmap-dev"),
    "nmap-hackers@insecure.org":	CiscoDir("Lists", "Nmap-dev"),
    "pen-test@securityfocus.com":	CiscoDir("Lists", "PenTest"),
    "pen-test@securityfocus.org":	CiscoDir("Lists", "PenTest"),
    "pen-test@lists.securityfocus.com": CiscoDir("Lists", "PenTest"),
    "xml@gnome.org":		CiscoDir("Lists", "XML-GNOME"),
    "dailydave@lists.immunitysec.com": CiscoDir("Lists", "Daily-Dave"),
    "dailydave@lists.immunityinc.com": CiscoDir("Lists", "Daily-Dave"),

    # Mailing list and other traffic that can share with wamber.net
    "wam+sourceforge@wamber.net":	WamberDir("Topic", "SourceForge"),
    "shakeslist@lists.cc.utexas.edu": WamberDir("Lists", "ShakesList"),
    "wam+fool@wamber.net":		WamberDir("Lists", "MotleyFool"),
    "ctlug@ctlug.org":		WamberDir("Lists", "CTLUG"), 
    "linux@ctlug.org":		WamberDir("Lists", "CTLUG"), 
    "austinliberator@yahoogroups.com":
    WamberDir("Lists", "AustinLiberator"),
    "apl@wamber.net":		WamberDir("Topic", "Poker"),
    "autism-discussion@external.cisco.com":
    WamberDir("Topic", "Autism"),
    "wam-domains@wamber.net":	WamberDir("Topic", "domains"),
    "partypoker@wamber.net":	WamberDir("Topic", "Poker"),
    "nvnews.net@wamber.net":	WamberDir("Membership", "nvidia-news-forum"),
    "server-coop@yahoogroups.com":	WamberDir("Lists", "Server-COOP"),
    "straightrazorplace@yahoogroups.com": 
    WamberDir("Lists", "StraightRazorPlace"),

    # - Wamber vendors
    "nerdbooks-dot-com@wamber.net":	WamberDir("Vendors", "NerdBooks.com"),
    "wam-wholelattelove@wamber.net": WamberDir("Vendors", "WholeLatteLove.com"),
    "rei@wamber.net":		WamberDir("Vendors", "REI.com"),
    "walgreens@wamber.net":		WamberDir("Vendors", "Walgreens.com"),
    "discovercard@wamber.net":	WamberDir("Vendors", "Discovercard.com"),
    "citibank@wamber.net":		WamberDir("Vendors", "CitiBank.com"),
    "amazon@wamber.net":		WamberDir("Vendors", "Amazon.com"),
    "wam-borders@wamber.net":	WamberDir("Vendors", "Borders"),
    "wam-amazon-com@wamber.net":	WamberDir("Vendors", "Amazon.com"),
    "ebay@wamber.net":		WamberDir("Vendors", "ebay-com"),
    "wam-ebay@wamber.net":		WamberDir("Vendors", "ebay-com"),
    "wam-netflix@wamber.net":	WamberDir("Vendors", "netflix"),
    "wam+classicshaving@wamber.net": WamberDir("Vendors", "ClassicShaving.com"),
    "hilton@wamber.net":		WamberDir("Vendors", "Hilton.com"),
    "genealogy@wamber.net":		WamberDir("Vendors", "Genealogy.com"),
    "aa-com@wamber.net":		WamberDir("Vendors", "AA.com-AAdvantage"),
    "upromise@wamber.net":		WamberDir("Vendors", "U-Promise"),
    "mytreo@wamber.net":		WamberDir("Vendors", "MyTreo.net"),
    "snapus-spam@wamber.net":	WamberDir("Vendors", "snapus.org"),
    "openmag@wamber.net":		WamberDir("Vendors", "openmag.org"),
    "taxcut@wamber.net":		WamberDir("Vendors", "TaxCut"),
    "tivo@wamber.net":		WamberDir("Vendors", "TiVo"),
    "wam+mwave@wamber.net":		WamberDir("Vendors", "MWave.com"),
}


def AddrToFolder(addr):
    """Returns the folder the address should get deposited in, or None
    if there was no match
    """
    return MailingListMappings.get(addr.lower(), None)


def filter_mail(to, cc, from_addr, msg, defines=[]):
    log = logging.getLogger("pycmail.filter_mail")
    log.debug("to=%r, cc=%r, from_addr=%r, msg=%r, defines=%r", 
              to, cc, from_addr, msg, defines)

    #if msg.has_key('X-Spam-Flag'):
    #	log.info("From=%s, To=%s, Cc=%s, Subject=%s, Filtered=%s",
    #		 from_addr, to, cc, `msg.get('Subject', "")`,
    #		 SpamFolder)
    #	return [SpamFolder]
    dests= set()
    for addr in chain(to, cc):
        folder = AddrToFolder(addr)
        if folder:
            dests.add(folder)
    if from_addr:
        folder = None
        from_addr=from_addr.lower()
        if from_addr in JunkOriginators:
            # if it's from a junker, just junk it
            dests = set([CiscoDir("INBOX", "Junk")])
        elif from_addr == "cdetsprod@cisco.com" and \
             "psirt@cisco.com" in cc:
            # I hate special casing this, but I don't have enough
            # special cases to warrent a more general solution 
            # right now.
            # ignore the recipients on the mesg and store one copy
            dests = set([AddrToFolder(from_addr)])
        elif from_addr != "wam@cisco.com":
            folder = AddrToFolder(from_addr)
            if folder:
                dests.add(folder)
    if not dests:
        dests.add(DefaultFolder(defines))
    log.info("From=%r, To=%r, Cc=%r, Subject=%r, Filtered=%r",
             from_addr, to, cc, msg.get('Subject', ""), ", ".join(dests))
    return dests



def main(argv=sys.argv, Progname=None):
    from optparse import OptionParser       # aka Optik

    # set up commandline arguments
    if not Progname:
        Progname=os.path.basename(argv[0])
    Usage="%prog usage: [-f] files_or_email_addrs [...]\n" \
        "%prog usage: -h\n" \
        "%prog usage: -V" 
    optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
    optparser.remove_option("--version")    # we add our own that knows -V
    optparser.add_option("-V", "--version", action="version",
                         help="show program's version number and exit")
    optparser.add_option("-d", "--debug", dest = "debug", 
                         action="store_true", help="log debugging messages")
    optparser.add_option("-f", "--file", dest = "file", 
                         action="store_true", help="evaluate files, not email addresses")
    (options, params) = optparser.parse_args(argv[1:])

    # set up logging environment
    root_log = logging.getLogger()          # grab the root logger
    root_log.setLevel((logging.INFO, logging.DEBUG)[options.debug == True])
    handler = logging.StreamHandler()
    logformat = "%(name)s: %(levelname)s: %(message)s"
    handler.setFormatter(logging.Formatter(logformat))
    root_log.addHandler(handler)
    log = logging.getLogger(Progname)

    for param in params:
        if options.file:
            mailmsg = rfc822.Message(file(param))
            folders = filter_mail(
                to= [addr for n, addr in mailmsg.getaddrlist('To')],
                cc= [addr for n, addr in mailmsg.getaddrlist('Cc')],
                from_addr = mailmsg.getaddr('From')[1], 
                msg= mailmsg)
            print "%s => %s" % (param, folders)
        else:
            print "%s => %s" % (param, AddrToFolder(param))

if __name__ == '__main__':
    import rfc822

    progname=os.path.basename(sys.argv[0])
    try:
        main()
    except SystemExit, value:
        sys.exit(value)
    except:
        (exc_type, exc_value, exc_tb) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_tb)	# if debugging
        sys.exit("%s: %s: %s" % (progname, exc_type.__name__, exc_value))
    sys.exit(0)
    progname=os.path.basename(sys.argv[0])