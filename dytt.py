#!/usr/bin/python
#-*-coding:utf-8-*-
from bs4 import BeautifulSoup
import requests
import re
import time
from pymongo import *
from tinylog import glog

logger = glog(__name__, './dytt.log')

#headers = {'User-Agent': 'curl/7.38.0', 'Host': 'www.dytt8.net', 'Accept': '*/*'}
headers = {'User-Agent': 'curl/7.38.0'}
timeout = 10

def get_latest_url():
    url = 'http://www.dytt8.net/index.htm'
    r = requests.get(url, timeout=timeout, headers=headers)
    r.encoding = 'gb2312'
    html_doc = r.text.replace('.[', '').replace(']','')
    soup = BeautifulSoup(html_doc, 'html.parser')

    links = soup.find_all('a', string=re.compile(u'最新电影下载'))
    return ['http://www.dytt8.net'+link.next_element.next_element['href'] for link in links]

def get_movie_detail(url):
    r = requests.get(url, timeout=timeout, headers=headers)
    r.encoding = 'gb2312'
    html_doc = r.text.replace(u'简　　介<br /><br />', u'简　　介').replace(u'简　　介 <br /><br />', u'简　　介')
    soup = BeautifulSoup(html_doc, 'html.parser')

    movie = {}    
    img = soup.find_all('img', border='0')
    movie['cover'] = img[1]['src']

    t = soup.find_all(string=re.compile(u'◎译'))
    if not t:
        t = soup.find_all(string=re.compile(u'◎片'))
    movie['title'] = t[0].split(u'　')[-1].split('/')[0]

    t = soup.find_all(string=re.compile(u'◎国'))
    movie['country'] = t[0].split(u'　')[-1]
    t = soup.find_all(string=re.compile(u'◎年'))
    movie['time'] = t[0].split(u'　')[-1]
    t = soup.find_all(string=re.compile(u'◎类'))
    movie['catalog'] = t[0].split(u'　')[-1]
    t = soup.find_all(string=re.compile(u'◎语'))
    movie['lang'] = t[0].split(u'　')[-1]
    t = soup.find_all(string=re.compile(u'◎导'))
    movie['director'] = t[0].split(u'　')[-1]
    t = soup.find_all(string=re.compile(u'◎主'))
    movie['star'] = t[0].split(u'　')[-1]
    t = soup.find_all(string=re.compile(u'◎简'))
    movie['brief'] = t[0].split(u'　')[-1]
    movie['timestamp'] = time.time()
    return movie

def save_mongodb(movie):
    client = MongoClient("localhost", 27017)
    db = client.dydb
    cols = db.cols
    find = cols.find({'cover': movie['cover']}).count()
    if not find:
        cols.insert(movie)
        print "movie %s saved" %(movie['cover'])
        logger.info("movie %s saved" %(movie['cover']))

def start_grasp():
    try:
        links = get_latest_url()
        links.reverse()
        for url in links:
            movie = get_movie_detail(url)
            save_mongodb(movie)
    except Exception, e:
        logger.info("get movies failed %s" % e)
    logger.info('job scheduled...')

if __name__ == '__main__':
    start_grasp()

