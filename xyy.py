#!/usr/bin/python
#-*-coding:utf-8-*-
from bs4 import BeautifulSoup
import requests
import re
from pymongo import *
from tinylog import glog
import time

ip = '204.152.220.23'
url = 'http://%s/forum.php?mod=forumdisplay&fid=883&filter=typeid&typeid=1096' % ip

logger = glog(__name__, './xyy.log')

headers = {'User-Agent': 'curl/7.38.0'}
timeout = 10

def retry_requests(url, timeout=timeout, headers=headers):
    retries = 0
    while retries < timeout:
        try:
            r = requests.get(url, timeout=timeout, headers=headers)
            return r
        except:
            logger.info('retries %d...' %retries)
            retries = retries + 1
            time.sleep(1)
    return None
    

def get_latest_url():
    r = retry_requests(url, timeout=timeout, headers=headers)
    if not r:
        return []
    r.encoding = 'gbk'
    html_doc = r.text.replace('[', '').replace(']', '')
    soup = BeautifulSoup(html_doc, 'html.parser')
    links = soup.find_all('a', string=re.compile(u'综合信息'))
    findings = []
    for link in links[1:]:
        title = link.next_element.next_element.next_element.string
        uri = link.next_element.next_element.next_element['href']
        findings.append({'title':title, 'uri':'http://%s/' % ip + uri})
    return findings

def get_content(uri):
    r = retry_requests(uri, timeout=timeout, headers=headers)
    if not r:
        return None
    r.encoding = 'gbk'
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    links = soup.find_all(string=re.compile(u'【'))
    links = [link for link in links if 'by' not in link]
    if links:
        return ''.join(links)

def save_mongodb(title, content):
    client = MongoClient("localhost", 27017)
    db = client.xyydb
    cols = db.cols
    find = cols.find({'title': title}).count()
    if not find:
        cols.insert({'title': title, 'content': content})
        print "%s saved" % title
        logger.info("%s saved" %(title))
    else:
        print 'skip %s' % title
        logger.info("%s skipped" %(title))

def run_xyy():
    try:
        findings = get_latest_url()
        findings.reverse()
        time.sleep(2)
        for f in findings:
            uri = f['uri']
            content = get_content(uri)
            if not content:
                continue
            save_mongodb(f['title'], content)
            time.sleep(2)
    except Exception, e:
        logger.info("get article failed - " + e.message)
    logger.info('job scheduled...')

if __name__ == '__main__':
    run_xyy()

