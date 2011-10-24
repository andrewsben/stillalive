#!/usr/bin/env python

import re
import requests
import sys

# FIXME(ja): unsure how to set timeout in newer versions of requests
#requests.settings(timeout=5.0)

def dash(url, tenant='admin', user='admin', password='secrete'):
    session = requests.session()

    crsf_regex = re.compile("name='csrfmiddlewaretoken' value='([^']*)'")
    login_regex = re.compile("auth")
    error_regex = re.compile("Error")

    r = session.get(url+'/auth/login/')
    assert r.status_code == 200, 'unable to access login page'
    assert not re.match(error_regex, r.content), 'error displayed on login page'

    match = re.search(crsf_regex, r.content)
    assert match, 'Unable to find CRSF token'

    auth = {'csrfmiddlewaretoken': match.groups(1)[0],
            'method': 'Login',
            'username': user,
            'password': password}

    r = session.post(url+'/auth/login/', data=auth)
    assert r.status_code == 200, 'fail to send auth credentials'
    assert not re.search(error_regex, r.content), 'error displayed on auth'

    r = session.get(url+'/dash/')
    assert r.status_code == 200, 'fail to access user dash'
    assert not re.search(login_regex, r.url), 'user dash fail (redirected to login)'
    assert not re.search(error_regex, r.content), 'error displayed on user dash'

    r = session.get(url+'/dash/%s/images/' % tenant)
    assert r.status_code == 200, 'fail to access dash/images'
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
