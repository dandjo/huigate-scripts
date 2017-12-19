#!/usr/bin/env python

import requests
import sys
from optparse import OptionParser
from _helpers import parse_response, login, logout, get


parser = OptionParser(usage='Usage: %prog <xml file>')
(options, args) = parser.parse_args()
if len(args) == 0:
    parser.print_usage()
    sys.exit(0)
xml_alias = args[0]


with requests.Session() as sess:
    login(sess)
    print parse_response(get(sess, args[0]))
    logout(sess)
