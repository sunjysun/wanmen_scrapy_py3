# coding: utf-8

import json
import locale

def get_m3u8_url(pathfilename_json=None, json_content=None):
    if pathfilename_json:
        with open(pathfilename_json, 'r') as f:
            string = f.read()
    elif json_content:
        string = json_content
    else:
        return
    dic = json.loads(string)

    lst = ['pcHigh', 'mobileHigh', 'pcMid', 'mobileMid', 'pcLow', 'mobileLow']
    for itm in lst:
        try:
            ret = dic['hls'][itm]
        except KeyError:
            try:
                ret = dic['video']['hls'][itm]
            except KeyError:
                continue
        # print ret
        return ret
        
def get_quiz_pack_id(pathfilename_json=None, json_content=None):
    if pathfilename_json:
        with open(pathfilename_json, 'r') as f:
            string = f.read()
    elif json_content:
        string = json_content
    else:
        return
    dic = json.loads(string)
    
    if dic['assetType'] == 'quiz':
        return dic['quizStatus']['quiz_pack_id']