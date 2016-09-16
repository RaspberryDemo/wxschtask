#!/usr/bin/python
#-*-coding:utf-8-*-
from wx import WxAPI
import requests
import os
import time
import schedule
import json

def get_oneday_text():
    url = 'http://open.iciba.com/dsapi'
    resp = requests.get(url)
    return {'en': resp.json()['content'], 'ch': resp.json()['note'], 'img': resp.json()['picture']}

def sch_post_template_msg():
    client = WxAPI()
    token = client.get_access_token()
    users = client.get_user_list(token)
    r = get_oneday_text()

    for u in users:
        body = '''
        {
            "touser":"%s",
            "template_id":"vmk8rT72FHcPeMDK3Zbo6LSXzm3qAuw4CNXxFsxokeg",
            "url": "%s",
            "topcolor":"#FF0000",
            "data":{
                "en": {
                        "value": "%s",
                        "color":"#173177"
                },
                "ch": {
                        "value": "%s",
                        "color":"#173177"
                }
            }
        }
        ''' % (u, r['img'], r['en'], r['ch'])
        client.post_template_msg(token, body.encode('utf-8'))

if __name__ == '__main__':
    print 'Background task is running now...'
    j = get_random_joke()

    schedule.every().day.at("12:00").do(sch_post_template_msg)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    while True:
        schedule.run_pending()
        time.sleep(1)
