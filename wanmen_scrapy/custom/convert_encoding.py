# coding: utf-8

def convert_to_unicode(str_or_uni):
    if not isinstance(str_or_uni, str):
        try:
            ret_uni = str_or_uni.decode('utf-8')
        except UnicodeDecodeError:
            ret_uni = str_or_uni.decode('gbk')
    else:
        try:
            b = str_or_uni.encode('utf-8')
            b = str_or_uni.encode('gbk')
            ret_uni = str_or_uni
        except UnicodeEncodeError:
            b = str_or_uni.encode('ISO-8859-1')
            ret_uni = convert_to_unicode(b)
    return ret_uni
