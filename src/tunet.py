#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import hashlib
import hmac
import json
import requests
import sys
import time
import urllib

from . import b64mod
from . import xxtea

import pprint

import logging
logger = logging.getLogger(__name__)

BASE_URL = 'https://auth4.tsinghua.edu.cn'
NET_STATUS_URL = 'https://net.tsinghua.edu.cn/cgi-bin/rad_user_info'

def get_challenge(username, ip='', double_stack=1, off_campus=True,
                  tm=time.time()):
    params = collections.OrderedDict([
        ('callback', '_'),
        ('username', username if off_campus else (username + '@tsinghua')),
        ('ip', ip),
        ('double_stack', double_stack),
        ('_', int(tm * 1000))
    ])
    r = requests.get(BASE_URL + '/cgi-bin/get_challenge', params=params).text
    r = json.loads(r[2:-1])
    try:
        assert r['error'] == 'ok'
    except AssertionError:
        logger.error(pprint.pformat(r))
        return None
    return r


def login(username, password, challenge, ip='', double_stack=1, ac_id=1,
          off_campus=True, tm=time.time()):
    challenge = challenge.encode()

    info = collections.OrderedDict([
        ('username', username if off_campus else (username + '@tsinghua')),
        ('password', password),
        ('ip', ip),
        ('acid', str(ac_id)),
        ("enc_ver", "srun_bx1")
    ])
    info_hash = b64mod.encode(xxtea.encode(
        json.dumps(info, separators=(',', ':')).encode(), challenge))

    checksum = hashlib.sha1(
        challenge +
        username.encode() + challenge +
        hmac.new(challenge).hexdigest().encode() + challenge +
        str(ac_id).encode() + challenge +
        ip.encode() + challenge +
        b'200' + challenge + b'1' + challenge +
        b'{SRBX1}' + info_hash
    ).hexdigest()

    params = collections.OrderedDict([
        ('callback', '_'),
        ('action', 'login'),
        ('username', username if off_campus else (username + '@tsinghua')),
        ('org_password', password),
        ('password', '{MD5}' + hmac.new(challenge).hexdigest()),
        ('ac_id', 1),
        ('ip', ip),
        ('double_stack', double_stack),
        ('info', b'{SRBX1}' + info_hash),
        ('chksum', checksum),
        ('n', 200),
        ('type', 1),
        ('_', int(tm * 1000))
    ])

    r = requests.get(BASE_URL + '/cgi-bin/srun_portal',
                    params=params).text
    r = json.loads(r[2:-1])
    try:
        assert r['error'] == 'ok'
    except AssertionError:
        logger.error(pprint.pformat(r))
        return None
    return r


def logout(username, challenge, ip='', double_stack=1, ac_id=1,
           off_campus=True, tm=time.time()):
    challenge = challenge.encode()

    info = collections.OrderedDict([
        ('username', username if off_campus else (username + '@tsinghua')),
        # ('password', password),
        ('ip', ip),
        ('acid', str(ac_id)),
        ("enc_ver", "srun_bx1")
    ])
    info_hash = b64mod.encode(xxtea.encode(
        json.dumps(info, separators=(',', ':')).encode(), challenge))

    checksum = hashlib.sha1(
        challenge +
        username.encode() + challenge +
        # hmac.new(challenge).hexdigest().encode() + challenge +
        str(ac_id).encode() + challenge +
        ip.encode() + challenge +
        b'200' + challenge + b'1' + challenge +
        b'{SRBX1}' + info_hash
    ).hexdigest()

    params = collections.OrderedDict([
        ('callback', '_'),
        ('action', 'logout'),
        ('username', username if off_campus else (username + '@tsinghua')),
        # ('org_password', password),
        # ('password', '{MD5}' + hmac.new(challenge).hexdigest()),
        ('ac_id', 1),
        ('ip', ip),
        ('double_stack', double_stack),
        ('info', b'{SRBX1}' + info_hash),
        ('chksum', checksum),
        ('n', 200),
        ('type', 1),
        ('_', int(tm * 1000))
    ])

    r = requests.get(BASE_URL + '/cgi-bin/srun_portal',
                    params=params).text
    r = json.loads(r[2:-1])
    try:
        assert r['error'] == 'ok'
    except AssertionError:
        logger.error(pprint.pformat(r))
        return None
    return r


def net_status():
    s = requests.get(NET_STATUS_URL).text
    if s:
        return tuple(x.strip() for x in s.split(','))
    else:
        return None 

def auth_status():
    r = requests.head(BASE_URL + '/srun_portal_pc.php')
    if r.next is None:
        return None
    else:
        args = urllib.parse.parse_qsl(urllib.parse.urlparse(r.next.url).query)
        username, = [x[1] for x in args if x[0] == 'username']
        return username
