#!/usr/bin/env python
"""Downloads and executes an executable provided as a parameter
"""

__author__ =   "William McVey <wam@cisco.com>"
__date__ =     "10/27/2009"
__revision__ = "0.0.1"


import socket
import urllib2
import urlparse
import BaseHTTPServer
from subprocess import Popen
import os
import sys
import logging

DEFAULT_USER_AGENT='Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
MAX_DL_SIZE = 5*1024*1024         # 5 meg should be good enough, per craiwill

def http_code_to_error(code):
    """Given an HTTP error code, return a text string explaining it
    """
    return BaseHTTPServer.BaseHTTPRequestHandler.responses.get(
        code, (None, "Unknown error code"))[1]
    

def fetch_executable(url, destdir, user_agent=None, timeout=None, 
                        max_size=MAX_DL_SIZE):
    """Fetches contents of URL into a specified directory
    
    If content is non executable (e.g. mime-type of 'text' or 'image')
    None is returned. Otherwise, filename of downloaded executable is 
    returned.
    """
    log = logging.getLogger("fetcher")
    socket.setdefaulttimeout(timeout)
    if not user_agent:
        user_agent = DEFAULT_USER_AGENT
    headers = { 'User-Agent' : user_agent }
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    base = os.path.basename(path)
    if not base:
        base = "untitled.exe"
    dest_filename = os.path.join(destdir, base)
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    actual_url = response.geturl()
    if actual_url != url:
        log.warn("Requested %r but received content from %r (redirected)", url, actual_url)
    info = response.info()
    if info.maintype in ("text", "image"):
        log.warn("URL returned a doc with mime-type of %r", info.type)
        return None
    dest = open(dest_filename, "wb")
    # protect against pulling an "executable" of infinite (or excessive) size
    content_length = info.get('Content-Length', None)
    if content_length and content_length < max_size:
        # urllib2 raises error in read() if actual contents > Content-length
        dest.write(response.read())
    else:
        log.warn("URL %r returned a content length of %r. (trunicating to "
                 "%s bytes)", url, content_length, max_size)
        dest.write(response.read(max_size))
    dest.close()
    return dest_filename


def setup_logging(debug=False, verbose=False, logfile=None):
    """set up logging environment
    """
    root_log = logging.getLogger()          # grab the root logger
    if debug:
        root_log.setLevel(logging.DEBUG)
    elif verbose:
        root_log.setLevel(logging.INFO)
    else:
        root_log.setLevel(logging.WARN)
    handler = logging.StreamHandler()
    if logfile:
        handler = logging.FileHandler(logfile) 
        logformat = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
        handler.setFormatter(logging.Formatter(logformat))
        root_log.addHandler(handler)
    logformat = "%(name)s: %(levelname)s: %(message)s"
    handler.setFormatter(logging.Formatter(logformat))
    root_log.addHandler(handler)
    return root_log


def main(argv=sys.argv, Progname=None):
    from optparse import OptionParser, SUPPRESS_HELP       # aka Optik

    # set up commandline arguments
    if not Progname:
        Progname=os.path.basename(argv[0])
    Usage="\n%prog usage: [-A USER_AGENT] [-O OUTPUT_DIR] URL [...]\n" \
          "%prog usage: -h\n" \
          "%prog usage: -V" 
    optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
    optparser.remove_option("--version")    # we add our own that knows -V
    optparser.add_option("-V", "--version", action="version",
                         help="show program's version number and exit")
    optparser.add_option("-d", "--debug", dest = "debug", 
                         action="store_true", help=SUPPRESS_HELP)
    optparser.add_option("-A", "--user-agent", dest = "user_agent", 
                         action="store", default=None,
                         help="HTTP User Agent to claim to be (default: %r)" % DEFAULT_USER_AGENT)
    optparser.add_option("-O", "--output-dir", dest = "output_dir", 
                         action="store", default=".",
                         help="Directory in which to save and run the executable")
    optparser.add_option("-t", "--timeout", dest = "timeout", action="store",
                         default=None, help="Socket timeout (default: system default/unlimited)")
    optparser.add_option("-v", "--verbose", dest = "verbose",
                         action="store_true", help="be verbose")
    #optparser.add_option("-N", "--name", dest="var_n", 
    # action= "store|append|store_true|store_false" 
    # type = "int", default=, metavar=, help=)
    
    (options, params) = optparser.parse_args(argv[1:])
    setup_logging(options.debug, options.verbose, logfile=None)
    log = logging.getLogger(Progname)

    for url in params:
        try:
            pathname = fetch_executable(url, destdir=options.output_dir, 
                                        user_agent=options.user_agent,
                                        timeout=options.timeout)
        except urllib2.HTTPError, e:
            log.error("HTTP Error %d (%s): %s: %s", 
                      e.code, url, http_code_to_error(e.code), e.msg)
            continue
        except urllib2.URLError, e:
            log.error("URL Error (%s): %r", url, e.reason)
            continue
        if not pathname:
            continue
        try:
            stderr_file = open("%s-stderr" % pathname, "w")
            stdout_file = open("%s-stdout" % pathname, "w")
            p = Popen(pathname, stdout=stdout_file, stderr=stderr_file, 
                      cwd=options.output_dir)
            p.wait()
        except:
            (exc_type, exc_value, exc_tb) = sys.exc_info()
            log.error("Execution error (%s): %s: %s", url, exc_type.__name__, exc_value)


if __name__ == '__main__':
    progname=os.path.basename(sys.argv[0])
    try:
        main()
    except Exception:
        (exc_type, exc_value, exc_tb) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_tb)	# if debugging
        sys.exit("%s: %s: %s" % (progname, exc_type.__name__, exc_value))
    except:
        # catches SystemExit and KeyboardInterrupt
        (exc_type, exc_value, exc_tb) = sys.exc_info()
        sys.exit(exc_value)
    sys.exit(0)