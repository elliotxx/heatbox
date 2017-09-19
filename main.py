#coding=utf8
from common import *
import re
import time
import requests
from datetime import datetime

'''
def getHTML(url):
    # 获取html页面
    response = requests.get(url)
    return response.content
'''

live_num = None            # 当前直播间总数
live_time = None           # 当前直播总时长
top_live_num = None        # 曾出现过的最高直播间总数
today_heat_point = None    # 今天的最高得分
previous_time = None       # 一个时间间隔开始的时间

def Init():
    # 初始化
    global live_num, live_time, top_live_num, previous_time
    # 从数据库中取出曾经的最高直播总数
    top_live_num = 0
    today_heat_point = 0
    live_num = 0
    live_time = 0
    previous_time = datetime.now()

def Parse(url,pattern):
    # 根据模式串 pattern 解析 url 页面源码
    response = requests.get(url)
    html = response.content
    pattern = re.compile(pattern,re.S)
    items = re.findall(pattern,html)
    return items


def getLivePageSum(key):
    # 获取某关键字的直播间总页数
    url = 'https://search.bilibili.com/live?keyword=%s'%key
    LivePageSum_pattern = r'data-num_pages="(.*?)"'

    # 匹配直播间总数
    items = Parse(url, LivePageSum_pattern)
    if len(items) == 0:
        raise Exception,'获取某关键字的直播间总页数失败'
    return int(items[0])

def getCurLiveNo(key,page):
    # 获取当前页面的直播间列表
    url = 'https://search.bilibili.com/live?keyword=%s&page=%d&type=all&order=online&coverType=user_cover'%(key,page)
    LiveNo_pattern = r'<li class="room-item">.*?live\.bilibili\.com/(.*?)\?'

    # 匹配当前页面的所有直播间号
    items = Parse(url, LiveNo_pattern)
    # if len(items) == 0:
    #     raise Exception,'获取第 %d 页直播间列表失败'%page
    return items

def getHeatPoint():
    # 热度得分计算公式
    return float(live_num) / top_live_num * 100 + float(live_time) / (24*60*60) * 100

def updateHeatPoint():
    # 重新开始计算热度
    global live_num, top_live_num, previous_time, live_time, today_heat_point

    # 获得当前直播间总数
    # 直播间号列表
    live_list = []
    # 获取全部关键字的所有直播间号
    for key in keys:
        # 该关键字的直播间总页数
        pageSum = getLivePageSum(key)
        # 遍历所有页面
        for page in range(1,pageSum+1):
            # 获取当前页面的直播间号列表
            live_list += getCurLiveNo(key,page)

    # 直播间号列表去重
    live_list = list(set(live_list))
    live_num = len(live_list)


    # 获得直播间总时长
    # 遍历所有直播间
    cur_time = datetime.now()
    after_time = cur_time - previous_time
    previous_time = cur_time
    live_time += after_time.seconds * live_num

    # 更新直播间总数最高纪录
    if live_num > top_live_num:
        top_live_num = live_num

    # 计算热度得分
    if top_live_num == 0:
        top_live_num = live_num
    heat_point = getHeatPoint()

    # 更新今天的热度得分
    if heat_point > today_heat_point:
        today_heat_point = heat_point


    print '%s'%cur_time
    print '真实时间间隔：%s s'%after_time
    print '直播间总数：%d'%live_num
    print '直播总时长：%d s'%live_time
    print '当前热度得分：%f + %f = %f'%(float(live_num) / top_live_num * 100, float(live_time) / (24*60*60) * 100, heat_point)
    print '今日热度得分：%f'%today_heat_point





def main():
    # 主函数

    # 初始化
    Init()

    while True:
        # 更新当前热度数据
        updateHeatPoint()
        # 休眠一会
        time.sleep(watch_interval)




if __name__ == '__main__':
    main()



