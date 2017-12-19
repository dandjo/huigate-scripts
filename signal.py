#!/usr/bin/env python

import json
import os
import re
import requests
import signal
import sys
import time
from lxml import objectify
from datetime import datetime


def avg(vals):
    if len(vals) == 0:
        return 0
    return float(sum(vals)) / len(vals)


def parse_int(val):
    return float(re.sub('[^0-9\-]+', '', str(val)))


def login(sess):
    sess.get('http://homerouter.cpe/home/home.html')


def calc_rsrq_level(rsrq):
    level_scale = 8    # the amount of steps to be broken down
    level_min = -20    # the maximum possible level
    level_max = -3     # the minimum possible level
    return round((1.0 + (rsrq - level_max) / (level_max - level_min)) * level_scale)


def handle_exit(*args, **kwargs):
    with open(backupfile, 'w') as b:
        json.dump({prop: {'avg': avg(avgs[prop]),
            'len': len(avgs[prop])} for prop in props}, b)
    sys.exit(0)


def read_avgs():
    try:
        with open(backupfile) as b:
            d = json.load(b)
            return {prop: [d[prop]['avg']] * d[prop]['len'] for prop in props}
    except IOError:
        return {prop: [] for prop in props}


signal.signal(signal.SIGINT, handle_exit)
    
backupfile = os.path.expanduser('~') + os.sep + '.huigate-signal'
statsfile = os.path.expanduser('~') + os.sep + '.huigate-signal-stats'

props = {'rsrp': None, 'rssi': None, 'sinr': None, 'rsrq': None}
avgs = read_avgs()

with requests.Session() as sess:
    login(sess)
    iterations = 0
    while True:
        try:
            resp = sess.get('http://homerouter.cpe/api/device/signal')
            x = objectify.fromstring(resp.text.decode('utf-8').encode('ascii'))
            if x.tag == 'error' and hasattr(x, 'code') and x.code == '125002':
                time.sleep(1)
                login(sess)
            for prop in [p for p in props if hasattr(x, p)]:
                props[prop] = parse_int(getattr(x, prop))
                avgs[prop].append(props[prop])
            format_s = '%s | CELLID: %s | RSRP: %s (%7.2f) | RSSI: %8s (%7.2f) | '\
                       'SINR: %6s (%5.2f) | RSRQ: %5s [%-8s] (%6.2f [%-8s])\n'
            sys.stdout.write(format_s % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                x.cell_id,
                x.rsrp, avg(avgs['rsrp']),
                x.rssi, avg(avgs['rssi']),
                x.sinr, avg(avgs['sinr']),
                x.rsrq, '*' * int(calc_rsrq_level(props['rsrq'])),
                avg(avgs['rsrq']), '*' * int(calc_rsrq_level(avg(avgs['rsrq'])))))
            sys.stdout.flush()
            time.sleep(0.0)
            iterations = iterations + 1
            iter_limit = 50
            if iterations > iter_limit:
                with open(statsfile, 'a') as s:
                    format_s = '%s | CELLID: %s | RSRP: %7.2f | RSSI: %7.2f | '\
                               'SINR: %5.2f | RSRQ: %6.2f [%-8s]\n'
                    s.write(format_s % (
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        x.cell_id,
                        avg(avgs['rsrp'][-iter_limit:]),
                        avg(avgs['rssi'][-iter_limit:]),
                        avg(avgs['sinr'][-iter_limit:]),
                        avg(avgs['rsrq'][-iter_limit:]),
                        '*' * int(calc_rsrq_level(avg(avgs['rsrq'][-iter_limit:])))))
                iterations = 0
        except Exception as e:
            sys.stderr.write('%s\n' % e)
            sys.stderr.flush()
            time.sleep(1)
            login(sess)
