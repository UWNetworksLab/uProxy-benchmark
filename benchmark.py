#!/usr/bin/env python

import hashlib
import os
import socks
import socket
import time
import urllib, urllib2


socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "localhost", 9999)
straight_socket = socket.socket
socket.socket = socks.socksocket

def http_get(url):
  request = urllib2.Request(url)
  request.add_header('Cache-Control','max-age=0')
  response = urllib2.urlopen(request)
  # print response.read()
  return True

WGET_CMD_OPTIONS = '--adjust-extension --span-hosts --convert-links --backup-converted --page-requisites '

def http_wholepage_url_list_wget(url):
  m = hashlib.md5()
  m.update(url)
  m.digest()
  list_name = 'url_list_' + m.hexdigest()

  cmd = 'wget %s %s  2>&1 | grep \'Saving to:\' > %s' % (WGET_CMD_OPTIONS, url, list_name)
  os.system(cmd)
  return list_name

def measure(function, args):
  start = time.time()
  if not function(*args):
    return -1
  end = time.time()
  return end - start

def measure_one_round(method, url):
  socket.socket = straight_socket
  if measure(method, [url]) > 0:
    baseline = measure(method, [url])
    socket.socket = socks.socksocket
    perf = measure(method, [url])
    print '%s\tbaseline=%s\tperf=%s' % (url, baseline, perf)

def measure_one_round_whole_page(method, url):
  list_filename = http_wholepage_url_list_wget(url)
  url_list = []
  for item in open(list_filename):
    url_list.append('http://' + item[12:-2])

  start = time.time()
  socket.socket = straight_socket
  http_get(url_list[1])
  for u in url_list:
    try:
      http_get(u)
    except:
      pass

  end = time.time()
  baseline = end - start
  start = time.time()
  socket.socket = socks.socksocket
  for u in url_list:
    try:
      http_get(u)
    except:
      pass
  end = time.time()
  perf = end - start
  print '%s\tbaseline=%s\tperf=%s' % (url, baseline, perf)


def main():
  site_list = [
    'http://www.google.com',
    'http://www.cnn.com',
    'http://www.epochtimes.com'
    ]

  for url in site_list:
    # measure_one_round(http_get, url)
    measure_one_round_whole_page(measure_one_round_whole_page, url)

if __name__ == '__main__':
  main()
 
