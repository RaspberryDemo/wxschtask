#!/usr/bin/python
#-*-coding:utf-8-*-
from soup import SoupX
from pymongo import *

url = 'http://m.99mm.me/'

def get_all_images(uri, myl):
    soup = SoupX(uri, 'utf-8').get()
    for link in soup.find_all("div", id="picbox"):
        img = link.img['src']
        myl.append(img)
        next = link.a['href']
        if 'url' in next:
            next_url = uri.split('?')[0]+'?'+next.split('?')[1]
            get_all_images(next_url, myl)
        else:
            return myl

def spider_web():
    soup = SoupX(url, 'utf-8').get()
    stores = []
    for link in soup.find_all("ul", class_="piclist"):
        destpages = link.find_all("a")
        destpages = [d['href'] for d in destpages][0::2]
        
        imgs = link.find_all("img")
        idx = 0
        for img in imgs:
            next = url+destpages[idx if idx < len(destpages) else 0]
            all_images = []
            get_all_images(next,all_images)
            
            info = {'alt': img['alt'], 'img': img['data-img'],
                    'next': next, 'images': all_images}
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

def start_spider():
    stores = spider_web()
    print stores
    save_mongodb(stores)
    
if __name__ == '__main__':
    start_spider()
