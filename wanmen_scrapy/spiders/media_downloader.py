import scrapy
import logging
import os
import json
from distutils.util import strtobool
from wanmen_scrapy.custom.parse_m3u8 import extract_ts
from wanmen_scrapy.custom.http_downloader import download


class MediaDownloaderSpider(scrapy.Spider):
    name = 'media_downloader'
    allowed_domains = ['media.wanmen.org']
    start_urls = ['https://media.wanmen.org/', 'https://media-oversea-q1.wanmen.org/']
    headers = {
        'Origin': 'https://www.wanmen.org',
        'Referer': 'https://www.wanmen.org/',
        'content-type': 'application/json',
    }

    def __init__(self, root_path='wanmen', docs='True', ts='True'):
        self.root_path = root_path
        self.down_docs = docs
        self.down_ts = ts
        
    def start_requests(self):
        walker = os.walk(self.root_path)
        while True:
            try:
                cur_dir, dirs, files = next(walker)
                for fn in files:
                    if strtobool(self.down_ts) and fn.lower().endswith('.m3u8'):
                        gnr = self.download_ts(cur_dir, fn)
                        while True:
                            try:
                                yield next(gnr)
                                continue
                            except StopIteration:
                                pass
                            break
                    elif strtobool(self.down_docs) and fn.lower() == 'info.json':
                        # self.download_docs(cur_dir, fn)
                        gnr = self.download_docs(cur_dir, fn)
                        while True:
                            try:
                                yield next(gnr)
                                continue
                            except StopIteration:
                                pass
                            break
                continue
            except StopIteration:
                pass
            break
            
    def download_ts(self, cur_dir, fn):
        lst_urls = extract_ts(os.path.join(cur_dir, fn), prefix=self.start_urls[0])
        for u in lst_urls:
            fn = u.rsplit('/', 1)[1]
            pathfn = os.path.join(cur_dir, fn)
            if os.path.isfile(pathfn):
                logging.info(f'已存在: {pathfn}')
            else:
                yield scrapy.Request(u, meta={'pathfn': pathfn}, headers=self.headers, callback=self.parse)
        
    def download_docs(self, cur_dir, fn):
        with open(os.path.join(cur_dir, fn), encoding='utf-8') as f:
            s = f.read()
        dic = json.loads(s)
        lst_docs = dic['documents']
        for dic_doc in lst_docs:
            u = dic_doc['url']
            fn = u.rsplit('/', 1)[1]
            pathfn = os.path.join(cur_dir, fn)
            if os.path.isfile(pathfn):
                logging.info(f'已存在: {pathfn}')
            else:
                yield scrapy.Request(u, meta={'pathfn': pathfn}, headers=self.headers, callback=self.parse)
                '''while True:
                    try:
                        path_filename_doc = download(u, path=cur_dir)
                    except Exception as e:
                        logging.warn(e)
                        continue
                    break
                logging.info(f'已下载: {path_filename_doc}')'''
                
    def parse(self, response):
        pathfn = response.meta['pathfn']
        with open(pathfn, 'wb') as f:
            f.write(response.body)
