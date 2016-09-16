#!/usr/bin/python
#-*-coding:utf-8-*-
import requests

APP_ID = 'wx77c7e8f88bf6119e'
APP_SECRET = '2756751687b1adffb01c930af86e7fc0'

class WxAPI():
    def __init__(self, app_id=APP_ID, app_secret=APP_SECRET):
        self.app_id = app_id
        self.app_secret = app_secret
    
    def get_access_token(self):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' \
                % (self.app_id, self.app_secret)
        resp = requests.get(url)
        return resp.json()['access_token']
    
    def get_user_list(self, token):
        url = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s' % token
        resp = requests.get(url)
        return resp.json()['data']['openid']

    def post_template_msg(self, token, body):
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % token
        resp = requests.post(url, data=body)
        print resp.json()

if __name__ == '__main__':
    client = WxAPI(APP_ID, APP_SECRET)
    token =  client.get_access_token()
    print client.get_user_list(token)
