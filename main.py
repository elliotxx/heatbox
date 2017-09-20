#coding=utf8
from __future__ import unicode_literals
from common import *
import re
import time
import base64
import pymongo
import requests
from datetime import datetime
from pyecharts import Line, Grid, Page

'''
def getHTML(url):
    # 获取html页面
    response = requests.get(url)
    return response.content
'''

live_num = None            # 当前直播间总数
live_time = None           # 当前直播总时长
top_live_num = None        # 曾出现过的最高直播间总数
heat_point = None          # 当前热度得分
today_heat_point = None    # 今天的最高得分
previous_time = None       # 一个时间间隔开始的时间

def Init():
    # 初始化
    global live_time, top_live_num, previous_time

    # 初始化：数据库、socket 超时时间
    # 连接 mongo 数据库
    mongo_client = pymongo.MongoClient('mongodb://%s:%s@%s:%d/%s'%(mongo_user,mongo_pwd,mongo_host,mongo_port,mongo_dbname))

    # 切换 mongo 数据库
    mongo_db = mongo_client[mongo_dbname]

    # 获取 mongo 数据库中的集合
    mongo_global = mongo_db['global']
    mongo_data = mongo_db['data']

    # 创建集合 peoples 的索引
    # if mongo_data.count() == 0:
    #     CreateIndex(mongo_data)

    # 从数据库中取出 历史最高直播间数 和 当天的最高得分
    top_live_num = mongo_global.find_one('top_live_num')
    today_heat_point = mongo_global.find_one('today_heat_point')
    top_live_num = 0 if top_live_num == None else top_live_num
    today_heat_point = 0 if today_heat_point == None else today_heat_point

    # 从数据库中取出 最近一条时间记录保存的数据
    last_data = mongo_data.find().sort([('cur_time', pymongo.DESCENDING)]).limit(1)[0]
    live_time = 0 if last_data == None else last_data['live_time']
    previous_time = datetime.now() if last_data == None else last_data['cur_time']

    # print top_live_num, today_heat_point, live_time, previous_time

    return mongo_global, mongo_data


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

def getHeatPoint():
    # 热度得分计算公式
    return float(live_num) / top_live_num * 100 + float(live_time) / (24*60*60) * 100

def updateHeatPoint(mongo_global, mongo_data):
    # 重新开始计算热度
    global live_num, top_live_num, previous_time, live_time, today_heat_point, heat_point

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
    cur_time = datetime.now()
    after_time = cur_time - previous_time
    previous_time = cur_time
    live_time += after_time.seconds * live_num

    # 更新直播间总数最高纪录
    if live_num > top_live_num:
        top_live_num = live_num

    # 计算热度得分
    heat_point = getHeatPoint()

    # 更新今天的热度得分
    if heat_point > today_heat_point:
        today_heat_point = heat_point


    # 上传数据到数据库
    data = {
        'cur_time' : cur_time,      # 当前时间
        'live_num' : live_num,      # 直播间数
        'live_time' : live_time    # 今日累计直播时长
    }
    mongo_data.insert(data)




    print '%s'%cur_time
    print '真实时间间隔：%s s'%after_time
    print '直播间总数：%d'%live_num
    print '直播总时长：%d s'%live_time
    print '当前热度得分：%f + %f = %f'%(float(live_num) / top_live_num * 100, float(live_time) / (24*60*60) * 100, heat_point)
    print '今日热度得分：%f'%today_heat_point


def Render(axisx, axisy, axisy2):
    # 渲染图表
    max_axisx_num = 6

    # 维护 x、y 轴数据
    if len(axisx) >= max_axisx_num:
        del axisx[0]
        del axisy[0]
        del axisy2[0]
    axisx.append(str(previous_time.strftime('%Y-%m-%d\n%H:%M:%S')))
    axisy.append(heat_point)
    axisy2.append(live_num)
    print axisx
    print axisy
    print axisy2


    page = Page(page_title = 'HeatBox')

    # line*2
    line = Line(title = "热度得分趋势图")
    line.add("热度得分", axisx, axisy, is_xaxislabel_align = True, is_fill=True, area_color='#FF0000', area_opacity=0.3, mark_line=["max"])
    page.add(line)

    line2 = Line(title = "直播间数趋势图")
    line2.add("直播间数", axisx, axisy2, is_xaxislabel_align = True, is_fill=True, area_color='#000000', area_opacity=0.3, mark_line=["max"])
    page.add(line2)

    page.render()



def main():
    # 主函数

    # 初始化
    mongo_global, mongo_data = Init()

    axisx = []
    axisy = []
    axisy2 = []
    while True:
        # 更新当前热度数据
        updateHeatPoint(mongo_global, mongo_data)

        # 渲染图表
        Render(axisx, axisy, axisy2)

        print ''

        # 休眠一会
        time.sleep(watch_interval)




if __name__ == '__main__':
    main()



