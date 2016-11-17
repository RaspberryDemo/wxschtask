#!/usr/bin/python
#-*-coding:utf-8-*-
from wx import WxAPI
import requests
import os
import time
from runonce import start_spider
from dytt import start_grasp
from xyy import run_xyy
from mmjpg import start_mmjpg
from apscheduler.schedulers.background import BackgroundScheduler

def get_oneday_text():
    url = 'http://open.iciba.com/dsapi'
    resp = requests.get(url)
    return {'en': resp.json()['content'], 'ch': resp.json()['note'], 'img': resp.json()['picture']}

def post_iciba_template_msg():
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

    scheduler = BackgroundScheduler()

    scheduler.add_job(post_iciba_template_msg, 'cron', hour=12)
    scheduler.add_job(start_spider, 'cron', minute='*/30')
    scheduler.add_job(start_mmjpg, 'cron', minute='*/30')
    scheduler.add_job(start_grasp, 'cron', minute='*/20')
    scheduler.add_job(run_xyy, 'cron', minute='*/15')
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
