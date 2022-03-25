# coding: utf-8

import re

def extract_ts(m3u8_filepathname, prefix=None):
    reg = re.compile(r'^.+?\.ts$')
    with open(m3u8_filepathname, 'r') as f:
        lines = f.readlines()
    lst_ts = list()
    for line in lines:
        lst = reg.findall(line)
        lst_ts.extend(lst)
    if isinstance(prefix, str):
        lst_ts = [prefix + ele for ele in lst_ts]
    return lst_ts