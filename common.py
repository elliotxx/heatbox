#coding=utf8
import sys
from datetime import datetime


# 设置
keys = ['绝地求生','吃鸡']    # 监控的关键词

watch_interval = 5        # 默认监控时间间隔，单位为秒


# 编码信息
input_encoding = sys.stdin.encoding
output_encoding = sys.stdout.encoding
file_encoding = 'utf8'


def printx(s, end = '\n'):
    '''通用输出'''
    '''可输出 str、dict 类型'''
    '''可自动转换编码'''
    if output_encoding == None:
        sys.stdout.write(s)
        sys.stdout.write('\n')
    elif isinstance(s,str):
        s = s.decode(file_encoding)
        s += end
        s = s.encode(output_encoding)
        sys.stdout.write(s)
    elif isinstance(s,dict):
        s = json.dumps(s, indent=4, ensure_ascii=False)
        s += end
        s = s.encode(output_encoding)
        sys.stdout.write(s)
    else:
        print s