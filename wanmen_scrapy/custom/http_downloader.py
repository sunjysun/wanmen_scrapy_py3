# coding: utf-8

import requests
import os
import sys
import locale
from contextlib import closing

def write_file(response, path_with_filename, stream=True):
    with open(path_with_filename, 'wb')as f:
        if stream is True:
            for response_data in response.iter_content(1048576):  # 1024 * 1024
                f.write(response_data)
        else:
            f.write(response.content())

def download(url, params=None, path='.', filename=None, headers=None, data=None, stream=True):
    # GET请求的下载
    while True:
        try:
            if data is None:
                response = requests.get(url=url,params=params, headers=headers, stream=stream, timeout=60)
            elif isinstance(data, dict):
                response = requests.post(url=url, data=data, headers=headers, stream=stream, timeout=60)
            else:
                sys.stderr.write(u'data 格式错误，应该为dict')
        except Exception as e:
            print(e)
            continue
        break
    if filename is None:
        filename = url.rsplit('/', 1)[1]
        filename = filename.split('#', 1)[0].split('?', 1)[0]
    # 其实这里应该加过滤路径中不允许的字符，path和filename都得过滤
    if not os.path.isdir(path):
        os.makedirs(path)
    '''
    if isinstance(path, str):
        path = path.decode(locale.getpreferredencoding())
    if isinstance(filename, str):
        filename = filename.decode(locale.getpreferredencoding())
    '''
    path_with_filename = os.path.join(path, filename)
    with closing(response) as r:
        write_file(response=response, path_with_filename=path_with_filename)
    return path_with_filename