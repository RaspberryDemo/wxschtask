#!/usr/bin/python
#-*-coding:utf-8-*-
from bs4 import BeautifulSoup
import requests

class SoupX():
    def __init__(self, url, charset):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        r = requests.get(url, headers=headers)

        r.encoding = charset
        html = r.text
        html = html.replace('<span>', '').replace('</span>', '').replace('<br/>', '') 
        self.soup = BeautifulSoup(html, 'html.parser')

    def get(self):
        return self.soup
