#!/usr/bin/env python
'''
Created on Oct 22, 2011

@author: arefaey
'''
from httplib2 import Http
from md5 import md5
import re
from urllib import urlencode

URL = 'http://10.0.0.2/login'
output = '/tmp/login.html'
salt_pattern = '\\\\\d*'
h = Http()

def truncate_file(file):
    f = open(file, 'w+')
    for line in f.readlines():
        line = line.replace(line, '')
        f.writelines(line)
        f.flush()
    print 'file: "%s" truncated' % f.name
    
def extract_salt(file):
    f = open(file, 'r')
    li = ''
    for line in f.readlines():
        if line.find('hexMD5') != -1:
            li = line
            break
    r = re.compile("\\\\\d*")
    salt = r.findall(li)
    if not salt:
        print 'seems to be already logged in'
        exit()
    x = chr(int(salt[0][1:], 8))
    rest = salt[1:]
    y = ''.join(chr(int(d[1:], 8)) for d in rest)
    return x, y

def login(username, password):
    data = {'username':username, 'password':password, 'dst':'', 'popup':'true'}
    payload = urlencode(data)
    headers = {}
    headers.update({'Content-Type':'application/x-www-form-urlencoded'})
    response, _ = h.request(URL, method='POST', body=payload, headers=headers)
    assert(response.status==200)
    try:
        response['set-cookie']
        response['set-cookie']
    except KeyError:
        raise Exception('Login Failed')

def main():
    import sys
    argz = sys.argv[1:]
    try:
        username = argz[0]
        password = argz[1]
    except Exception:
        print 'could not parse arguments\nusage: python main.py username password'
        exit()
    response, content = h.request(URL)
    assert(response.status==200)
    truncate_file(output)
    f = open(output, 'w')
    f.write(content)
    f.flush()
    x, y = extract_salt(output)
    salted = x + password + y
    print 'salted password: %s' % salted
    hashed_password = md5(salted)
    hex_hash_password = hashed_password.hexdigest()
    print 'hashed password: %s' % hex_hash_password
    login(username, hex_hash_password)
    print 'Successfully logged in ;)'
    
if __name__ == '__main__':
    main()