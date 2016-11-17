#!/usr/bin/python
#-*-coding:utf-8-*-
from soup import SoupX
from pymongo import *
import requests
import os
import re
from tinylog import glog

logger = glog(__name__, './mmjpg.log')

url = 'http://www.mmjpg.com/'
local_path = '/home/pi/www/wxpub/static/mmjpg/'

def get_local_filename(link):
    local_filename = '-'.join(link.split('/')[-3:])
    return local_filename

def downloadImageFile(imgUrl):  
    local_filename = get_local_filename(imgUrl) 

    if os.path.isfile(local_path+local_filename):
        return local_filename
    logger.info("Download Image File=%s" % local_filename)
    r = requests.get(imgUrl, stream=True) # here we need to set stream = True parameter  
    with open(local_path+local_filename, 'wb') as f:  
        for chunk in r.iter_content(chunk_size=1024):  
            if chunk: # filter out keep-alive new chunks  
                f.write(chunk)  
                f.flush()  
        f.close()  
    return local_filename  

def run_mmjpg(page=1):
    soup = SoupX(url+'home/%d' %page, 'utf-8').get()
    stores = []
    for link in soup.find_all("span", class_="title"):
        destpages = link.find_all("a")

        findings = [{'alt': d.string, 'uri': d['href']} for d in destpages]
        stores = []
        for f in findings:
            soup = SoupX(f['uri'], 'utf-8').get()
            infostr = soup.find_all(string=re.compile('var picinfo ='))
            infostr = infostr[0].replace(';','').replace(' ','').replace('[','').replace(']','').split('=')[1]
            picinfo = infostr.split(',')
            print picinfo

            all_alias = []
            for p in range(1, int(picinfo[2])+1):
                imgUrl = 'http://img.mmjpg.com/%s/%s/%s.jpg' % (picinfo[0], picinfo[1], p)
                local_filename = downloadImageFile(imgUrl)
                all_alias.append('mmjpg/'+local_filename)            
            info = {'alt': f['alt'], 'img': f['uri'], 'next': '', 'images': [], 'alias': all_alias, 'source': 'mmjpg'}
        
            stores.append(info)
    return stores

def save_mongodb(stores):
    client = MongoClient("localhost", 27017)
    db = client.mmdb
    mmc = db.mmc
    for s in stores:
        if mmc.find({'img':s['img']}).count():
            continue
        mmc.insert(s)

def start_mmjpg(page=1):
    findings = run_mmjpg(page)
    save_mongodb(findings)
    
if __name__ == '__main__':
    for i in range(1,2):
        start_mmjpg(i)
