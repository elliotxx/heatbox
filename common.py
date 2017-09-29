#coding=utf8
import re
import sys
import requests
from datetime import datetime


# 设置
keys = ['绝地求生','吃鸡']   # 监控的关键词
watch_interval = 5          # 默认监控时间间隔，单位为秒
# table_interval = 30 * 60    # x 轴的时间间隔，单位为秒
table_interval = 10    # x 轴的时间间隔，单位为秒
max_axisx_num = 10           # x 轴显示刻度数

# 数据库配置
mongo_dbname = 'heatbox'
mongo_host = '123.56.8.91'          # mongodb 主机地址
mongo_port = 27017                  # mongodb 主机端口
mongo_user = 'admin'                  # mongodb 登陆用户
mongo_pwd  = 'admin123'   # mongodb 用户密码

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

def isSameDay(day_a,day_b):
    # 判断是否是同一天
    if day_a.strftime('%Y-%m-%d') == day_b.strftime('%Y-%m-%d'):
        return True
    else:
        return False

def Parse(url,pattern):
    # 根据模式串 pattern 解析 url 页面源码
    response = requests.get(url)
    html = response.content
    pattern = re.compile(pattern,re.S)
    items = re.findall(pattern,html)
    return items

def getLivePageSum(key):
    # 获取某关键字的直播间总页数
    url = 'https://search.bilibili.com/live?keyword=%s'%key.decode('utf8')
    LivePageSum_pattern = r'data-num_pages="(.*?)"'

    # 匹配直播间总数
    items = Parse(url, LivePageSum_pattern)
    if len(items) == 0:
        raise Exception,'获取某关键字的直播间总页数失败'
    return int(items[0])

def getCurLiveNo(key,page):
    # 获取当前页面的直播间列表
    url = 'https://search.bilibili.com/live?keyword=%s&page=%d&type=all&order=online&coverType=user_cover'%(key.decode('utf8'),page)
    LiveNo_pattern = r'<li class="room-item">.*?live\.bilibili\.com/(.*?)\?'

    # 匹配当前页面的所有直播间号
    items = Parse(url, LiveNo_pattern)
    # if len(items) == 0:
    #     raise Exception,'获取第 %d 页直播间列表失败'%page
    return items

def getHeatPoint(live_num, live_time, top_live_num):
    # 热度得分计算公式
    return float(live_num) / top_live_num * 100 + float(live_time) / (24*60*60*live_num) * 100