#!/usr/bin/env python
import xlrd
import os
import sys


# Pulled from http://gizmojo.org/software/excelmailer/
# Inspiration: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/483742
class readexcel(object):
    """ Simple OS-independent class for extracting data from an Excel File.
    
    Uses the xlrd module (version 0.5.2 or later), supporting Excel versions:
    2004, 2002, XP, 2000, 97, 95, 5, 4, 3
    
    Data is extracted via iterators that return one row at a time -- either 
    as a dict or as a list. The dict generator assumes that the worksheet is 
    in tabular format with the first "data" row containing the variable names
    and all subsequent rows containing values. 
        
    Extracted data is represented fairly logically. By default dates are 
    returned as strings in "yyyy/mm/dd" format or "yyyy/mm/dd hh:mm:ss", as 
    appropriate. However, when specifying date_as_tuple=True, dates will be 
    returned as a (Year, Month, Day, Hour, Min, Second) tuple, for usage with 
    mxDateTime or DateTime. Numbers are returned as either INT or FLOAT, 
    whichever is needed to support the data. Text, booleans, and error codes 
    are also returned as appropriate representations. Quick Example:
    
        xls = readexcel('testdata.xls')
        for sname in xls.book.sheet_names():
            for row in xls.iter_dict(sname):
                print row
    """ 
    def __init__(self, *args, **kwargs):
        """ Wraps an XLRD book """
        self.book = xlrd.open_workbook(*args, **kwargs)
        self.sheet_keys = {}
    def is_data_row(self, sheet, i):
        values = sheet.row_values(i)
        if isinstance(values[0], basestring) and values[0].startswith('#'):
            return False # ignorable comment row
        for v in values:
            if bool(v):
                return True #+ row full of (valid) False values?
        return False
    def _parse_row(self, sheet, row_index, date_as_tuple):
        """ Sanitize incoming excel data """
        # Data Type Codes:
        #  EMPTY 0
        #  TEXT 1 a Unicode string 
        #  NUMBER 2 float 
        #  DATE 3 float 
        #  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE 
        #  ERROR 5 
        values = []
        for type, value in zip(
                sheet.row_types(row_index), sheet.row_values(row_index)):
            if type == 2:
                if value == int(value):
                    value = int(value)
            elif type == 3:
                datetuple = xlrd.xldate_as_tuple(value, self.book.datemode)
                if date_as_tuple:
                    value = datetuple
                else:
                    # time only no date component
                    if datetuple[0] == 0 and datetuple[1] == 0 and \
                       datetuple[2] == 0: 
                        value = "%02d:%02d:%02d" % datetuple[3:]
                    # date only, no time
                    elif datetuple[3] == 0 and datetuple[4] == 0 and \
                         datetuple[5] == 0:
                        value = "%04d/%02d/%02d" % datetuple[:3]
                    else: # full date
                        value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
            elif type == 5:
                value = xlrd.error_text_from_code[value]
            values.append(value)
        return values
    def iter_dict(self, sname, date_as_tuple=False):
        """ Iterator for the worksheet's rows as dicts """
        sheet = self.book.sheet_by_name(sname) # XLRDError
        # parse first row, set dict keys & first_row_index
        keys = []
        first_row_index = None
        for i in range(sheet.nrows):
            if self.is_data_row(sheet, i): 
                headings = self._parse_row(sheet, i, False)
                for j, var in enumerate(headings):
                    # replace duplicate headings with "F#".
                    if not var or var in keys:
                        var = u'F%s' % (j)
                    keys.append(var.strip())
                first_row_index = i + 1
                break
        self.sheet_keys[sname] = keys
        # generate a dict per data row 
        if first_row_index is not None:
            for i in range(first_row_index, sheet.nrows):
                if self.is_data_row(sheet, i): 
                    yield dict(map(None, keys, 
                            self._parse_row(sheet, i, date_as_tuple)))
    def iter_list(self, sname, date_as_tuple=False):
        """ Iterator for the worksheet's rows as lists """
        sheet = self.book.sheet_by_name(sname) # XLRDError
        for i in range(sheet.nrows):
            if self.is_data_row(sheet, i): 
                yield self._parse_row(sheet, i, date_as_tuple)



def main(argv=sys.argv, Progname=None):
    from optparse import OptionParser, SUPPRESS_HELP       # aka Optik
    import csv
    import logging

    # set up commandline arguments
    if not Progname:
        Progname=os.path.basename(argv[0])
    Usage="%prog usage: [-l] [-S SHEET_NAME|-s SHEET_IDX|-a] Excel_File\n" \
          "%prog usage: -h\n" \
          "%prog usage: -V" 
    optparser = OptionParser(usage=Usage, version="%prog: $Id:$" )
    optparser.remove_option("--version")    # we add our own that knows -V
    optparser.add_option("-V", "--version", action="version",
      help="show program's version number and exit")
    optparser.add_option("-d", "--debug", dest = "debug", 
      action="store_true", help=SUPPRESS_HELP)
    optparser.add_option("-v", "--verbose", dest = "verbose",
      action="store_true", help="be verbose")
    optparser.add_option("-a", dest = "all_sheets",
      action="store_true", help="Dump all sheets")
    optparser.add_option("-s", "--sheet-num", dest = "sheet_num",
      action="store", type="int", default=0,
      help="sheet number to dump (first sheet is 0)")
    optparser.add_option("-S", "--sheet-name", dest = "sheet_name",
      action="store", help="sheet name to dump")
    optparser.add_option("-l", "--list", dest = "list_sheets",
      action="store_true", help="list sheets in the file")
    #optparser.add_option("-N", "--name", dest="var_n", 
    # action= "store" | "append" | "store_true" | "store_false" 
    # type = "int"
    # default="foo", metavar="SOME_STRING", help="store a string")
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
    # handler = logging.FileHandler(options.logfile) 
    logformat = "%(name)s: %(levelname)s: %(message)s"
    handler.setFormatter(logging.Formatter(logformat))
    # logformat = "%(asctime)s %(levelname)s:%(name)s:%(message)s"
    #handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
    root_log.addHandler(handler)
    log = logging.getLogger(Progname)

    if len(params) != 1:
        log.error("Must provide a filename to an Excel document to read from")
        sys.exit(1)
    xls = readexcel(params[0])

    writer = csv.writer(sys.stdout)

    sheet_names = xls.book.sheet_names()
    if options.list_sheets:
        print "\n".join(["%d. %s" % x for x in enumerate(sheet_names)])
        sys.exit(0)
    if options.all_sheets:
    	for sheet_name in sheet_names:
          for row in xls.iter_list(sheet_name):
              try:
                writer.writerow(row)
              except:
                pass
        sys.exit(0)
    if options.sheet_name:
        sheet_name = options.sheet_name
    elif options.sheet_num:
        sheet_name = sheet_names[options.sheet_num]
    else:
    	log.error("Must specify a sheet name (-S), number (-s) or -a option to dump all")
	sys.exit(1)
    for row in xls.iter_list(sheet_name):
        writer.writerow(row)

if __name__ == '__main__':
    progname=os.path.basename(sys.argv[0])
    try:
        main()
    except SystemExit, value:
        sys.exit(value)
    except:
        (exc_type, exc_value, exc_tb) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_tb) # if debugging
        sys.exit("%s: %s: %s" % (progname, exc_type.__name__, exc_value))
    sys.exit(0)
