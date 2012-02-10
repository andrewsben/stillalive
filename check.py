#!/usr/bin/env python

import re
import requests
import sys

# FIXME(ja): unsure how to set timeout in newer versions of requests
#requests.settings(timeout=5.0)

def dash(url, tenant='admin', user='admin', password='secrete'):
    session = requests.session()
    region = 'http://127.0.0.1:5000/v2.0'

    crsf_regex = re.compile("name='csrfmiddlewaretoken' value='([^']*)'")
    login_regex = re.compile("auth")
    error_regex = re.compile("Error")

    r = session.get(url+'/')
    assert r.status_code == 200, 'unable to access login page'
    assert not re.match(error_regex, r.content), 'error displayed on login page'

    match = re.search(crsf_regex, r.content)
    csrf = match.groups(1)[0]
    assert match, 'Unable to find CRSF token'

    auth = {'csrfmiddlewaretoken': csrf,
            'method': 'Login',
            'username': user,
            'password': password,
            'region': region}

    r = session.post(url+'/', data=auth)
    assert r.status_code/100 in (2,3), 'fail to send auth credentials'
    assert not re.search(error_regex, r.content), 'error displayed on auth'

    r = session.get(url+'/nova/')
    assert r.status_code == 200, 'fail to access user dash'
    assert not re.search(login_regex, r.url), 'user dash fail (redirected to login)'
    assert not re.search(error_regex, r.content), 'error displayed on user dash'

    r = session.get(url+'/nova/images_and_snapshots/')
    assert r.status_code == 200, 'fail to access images'
    assert not re.search(login_regex, r.url), 'images fail (redirected to login)'
    assert not re.search(error_regex, r.content), '(glance?) error displayed'

    r = session.get(url+'/syspanel/')
    assert r.status_code == 200, 'fail to access syspanel'
    assert not re.search(login_regex, r.url), 'syspanel fail (redirected to login)'
    assert not re.search(error_regex, r.content), 'error displayed on syspanel'


if __name__ == '__main__':
    host = sys.argv[1]
    url = 'http://' + host
    tenant = user = password = None
    if len(sys.argv) >= 2:
        tenant = sys.argv[2]
    if len(sys.argv) >= 3:
        user = sys.argv[3]
    if len(sys.argv) >= 4:
        password = sys.argv[4]

    dash(url, tenant, user, password)
    print "success"
