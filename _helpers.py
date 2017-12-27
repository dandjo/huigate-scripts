import base64
import hashlib
import re
import requests
import time
import json
import os
import xml.etree.ElementTree as ET


def login(sess):
    root = _parse_xml_root('credentials.xml')
    username = root.find('username').text
    password = root.find('password').text
    def grep_csrf(html):
        pat = re.compile(r".*meta name=\"csrf_token\" content=\"(.*)\"", re.I)
        matches = (pat.match(line) for line in html.splitlines())
        return [m.group(1) for m in matches if m][1]
    csrf_token = grep_csrf(sess.get(parse_conf()['baseuri'] + '/home/home.html').text)
    sess.headers['Accept-Language'] = 'en-US'
    sess.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    sess.headers['X-Requested-With'] = 'XMLHttpRequest'
    sess.headers['__RequestVerificationToken'] = csrf_token
    sess.headers['Cache-Control'] = 'no-cache'
    sess.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9'
    def encrypt(text):
        m = hashlib.sha256()
        m.update(text)
        return base64.b64encode(m.hexdigest())
    password_hash = encrypt(username + encrypt(password) + csrf_token)

    root = _parse_xml_root('api/user/login.xml')
    resp = sess.post(parse_conf()['baseuri'] + root.find('uri').text,
                     data=ET.tostring(root.find('request')) % (username, password_hash))
    sess.headers.update({'__RequestVerificationToken': resp.headers["__requestverificationtokenone"]})
    return resp


def logout(sess):
    return post(sess, 'api/user/logout.xml')


def post(sess, xml_file):
    root = _parse_xml_root(xml_file)
    return sess.post(parse_conf()['baseuri'] + root.find('uri').text,
                     data=ET.tostring(root.find('request')))


def get(sess, xml_file):
    root = _parse_xml_root(xml_file)
    return sess.get(parse_conf()['baseuri'] +  root.find('uri').text)


def parse_conf():
    root = _parse_xml_root('config.xml')
    return {'baseuri': root.find('baseuri').text}


def parse_response(resp):
    return resp.text.decode('utf-8').encode('ascii').strip()


def _get_xml(xml_file):
    return ''.join((os.path.dirname(os.path.realpath(__file__)), os.sep, xml_file))

def _parse_xml_root(xml_file):
    return ET.parse(_get_xml(xml_file)).getroot()
