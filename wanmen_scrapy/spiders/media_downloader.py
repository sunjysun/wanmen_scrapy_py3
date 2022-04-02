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

    # down_type: ts pdf doc quiz
    def __init__(self, root_path='wanmen', down_type='all'):
        self.root_path = root_path
        self.down_type = down_type
        
    def start_requests(self):
        walker = os.walk(self.root_path)
        while True:
            try:
                cur_dir, dirs, files = next(walker)
                for fn in files:
                    if fn.lower().endswith('.m3u8'):
                        if 'all' == self.down_type or 'ts' == self.down_type:
                            gnr = self.download_ts(cur_dir, fn)
                            while True:
                                try:
                                    yield next(gnr)
                                    continue
                                except StopIteration:
                                    pass
                                break
                    elif fn.lower() == 'info.json':
                        if 'all' == self.down_type or 'doc' == self.down_type:
                            # self.download_docs(cur_dir, fn)
                            gnr = self.download_docs(cur_dir, fn)
                            while True:
                                try:
                                    yield next(gnr)
                                    continue
                                except StopIteration:
                                    pass
                                break
                    elif fn.lower() == 'letctures.json':
                        pass
                    elif fn.lower().endswith('.json'):
                        if 'all' == self.down_type or 'pdf' == self.down_type:
                            # self.download_docs(cur_dir, fn)
                            gnr = self.download_pdf(cur_dir, fn)
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
                
    ## 以下方法正在建设中
    def download_pdf(self, cur_dir, fn):
        with open(os.path.join(cur_dir, fn), encoding='utf-8') as f:
            s = f.read()
        dic = json.loads(s)
        dic_pdf = dic.get('pdf')
        url_pdf = None
        if dic_pdf:
            url_pdf = dic_pdf.get('url')
            name_pdf = dic_pdf.get('name')
        if url_pdf:
            if name_pdf:
                pass
            else:
                name_pdf = url_pdf.rsplit('/', 1)[-1].split('?', 1)[0]
            name_pdf = self.folder_name_filter([name_pdf])[0]
            pathfn = os.path.join(cur_dir, name_pdf)
            hdrs = dict(self.headers)
            hdrs['sec-ch-ua'] = '" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"'
            yield scrapy.Request(url_pdf, headers=hdrs, meta={'pathfn': pathfn, 'handle_httpstatus_list': [200, 401]}, callback=self.parse)
        
    def parse(self, response):
        pathfn = response.meta['pathfn']
        with open(pathfn, 'wb') as f:
            f.write(response.body)
        logging.info(f'已下载 - HTTP_Code {response.status} : {pathfn}: {response.url}')

    @staticmethod
    def folder_name_filter(folder_name_lst):
        ret_lst = list()
        for folder_name in folder_name_lst:
            folder_name = folder_name.strip()
            folder_name = folder_name.replace('/', u'／')\
                                     .replace('\\', u'、')\
                                     .replace(':', u'：')\
                                     .replace('*', u'·')\
                                     .replace('?', u'？') \
                                     .replace('"', u'“') \
                                     .replace('<', u'《')\
                                     .replace('>', u'》')\
                                     .replace('|', u'¦')\
                                     .replace('\b', '')
            ret_lst.append(folder_name)
        if isinstance(folder_name_lst, str):
            ret_lst = ''.join(ret_lst)
        return ret_lst