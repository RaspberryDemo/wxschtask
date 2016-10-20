#!/usr/bin/python
#-*-coding:utf-8-*-
from soup import SoupX
from pymongo import *
import requests
import os

url = 'http://m.99mm.me/'
local_path = '/home/pi/www/wxpub/static/'

def downloadImageFile(imgUrl):  
    local_filename = imgUrl.split('/')[-1]  

    if os.path.isfile(local_path+local_filename):
        print "File alreay exist File=%s", local_filename
        return local_filename
    print "Download Image File=", local_filename  
    r = requests.get(imgUrl, stream=True) # here we need to set stream = True parameter  
    with open(local_path+local_filename, 'wb') as f:  
        for chunk in r.iter_content(chunk_size=1024):  
            if chunk: # filter out keep-alive new chunks  
                f.write(chunk)  
                f.flush()  
        f.close()  
    return local_filename  

def get_all_images(uri, myl, myalias):
    soup = SoupX(uri, 'utf-8').get()
    for link in soup.find_all("div", id="picbox"):
        img = link.img['src']
        alias = img.split('/')[-1]
        downloadImageFile(img)
        myl.append(img)
        myalias.append(alias)
        next = link.a['href']
        if 'url' in next:
            next_url = uri.split('?')[0]+'?'+next.split('?')[1]
            get_all_images(next_url, myl, myalias)
        else:
            return myl, myalias

def spider_web(page=1):
    soup = SoupX(url+'home/%d.html' %page, 'utf-8').get()
    stores = []
    for link in soup.find_all("ul", class_="piclist"):
        destpages = link.find_all("a")
        destpages = [d['href'] for d in destpages][0::2]
        
        imgs = link.find_all("img")
        idx = 0
        for img in imgs:
            next = url+destpages[idx if idx < len(destpages) else 0]
            all_images = []
            all_alias = []
            get_all_images(next,all_images,all_alias)
            
            info = {'alt': img['alt'], 'img': img['data-img'],
                    'next': next, 'images': all_images, 'alias': all_alias}
            stores.append(info)
            idx += 1
        return stores

def save_mongodb(stores):
    client = MongoClient("localhost", 27017)
    db = client.mmdb
    mmc = db.mmc
    for s in stores:
        if mmc.find({'img':s['img']}).count():
            continue
        mmc.insert(s)

def start_spider(page=1):
    stores = spider_web(page)
    save_mongodb(stores)
    
if __name__ == '__main__':
    for i in range(1,2):
        start_spider(i)
