#coding=utf8
# from __future__ import unicode_literals
from common import *
import time
import base64
import pymongo
from datetime import datetime, timedelta
from pyecharts import Line, Grid, Page


def Init():
    # 初始化
    global live_time, top_watch_num, top_live_num, previous_time

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

    # 初始化 直播时间 和 上一个时间片段
    now = datetime.now()
    if mongo_data.count()==0:
        live_time = 0
        previous_time = now
    else:
        # 取出最后一条数据
        last_data = mongo_data.find().sort([('cur_time', pymongo.DESCENDING)]).limit(1)[0]
        # 更新今日直播时间 和 上一个时间记录的时刻
        # 上一个时间片段不存在 或者 不在同一天
        if not isSameDay(last_data['cur_time'],now):
            live_time = 0
            previous_time = now
        else:
            live_time = last_data['live_time']
            previous_time = last_data['cur_time']

    # 初始化 历史最高直播间数 和 当天的最高得分
    if mongo_global.count() == 0:
        data = {'top_live_num':0, 'top_watch_num':0}
    else:
        # 默认取出第一条数据(默认该集合中只有一条记录)
        data = mongo_global.find_one()
        # 初始化
        top_live_num = data['top_live_num'] if data.has_key('top_live_num') else 0
        top_watch_num = data['top_watch_num'] if data.has_key('top_watch_num') else 0

    mongo_global.save(data)


    return mongo_global, mongo_data


def updateHeatPoint(mongo_global, mongo_data):
    # 重新开始计算热度
    global live_num, watch_num, top_live_num, top_watch_num, previous_time, live_time, heat_point

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

    # 获得直播间总数 和 直播间观看人数
    live_dict = {}
    for k,v in live_list:
        live_dict[k] = int(v)
    live_num = len(live_dict)
    watch_num = reduce(lambda x,y:x+y,live_dict.values())


    # 获得直播间总时长
    cur_time = datetime.now()
    # 判断是否在同一天
    if not isSameDay(previous_time,cur_time):
        live_time = 0
    after_time = cur_time - previous_time
    previous_time = cur_time
    live_time += after_time.seconds * live_num


    # 更新直播间总数最高纪录
    if live_num > top_live_num:
        top_live_num = live_num
        # 数据库中同步更新
        data = mongo_global.find_one()    
        data['top_live_num'] = top_live_num
        mongo_global.save(data)

    # 更新观看直播总人数最高纪录
    if watch_num > top_watch_num:
        top_watch_num = watch_num
        # 数据库中同步更新
        data = mongo_global.find_one()    
        data['top_watch_num'] = top_watch_num
        mongo_global.save(data)


    # 上传当前数据到数据库
    data = {
        'cur_time' : cur_time,      # 当前时间
        'live_num' : live_num,      # 直播间数
        'watch_num' : watch_num,    # 观看直播总人数
        'live_time' : live_time     # 今日累计直播时长
    }
    mongo_data.insert(data)
    

    # 更新今天的热度得分
    heat_point = getHeatPoint(data, top_live_num, top_watch_num)


    printx('%s'%cur_time)
    printx('真实时间间隔：%s s'%after_time)
    printx('直播间总数：%d'%live_num)
    printx('观看直播总人数：%d'%watch_num)
    printx('直播总时长：%d s'%live_time)
    printx('当前热度得分：%f + %f + %f = %f'%(float(live_num) / top_live_num * 100, float(watch_num) / top_watch_num * 100, float(live_time) / (24*60*60*live_num) * 100, heat_point))


def Render(mongo_data):
    # 渲染图表
    ## 准备数据 
    # 初始化
    # x轴：时刻
    axisx = []
    # y轴-1：热度得分
    axisy = []
    # y轴-2：直播间数
    axisy2 = []
    # y轴-3：观看直播总人数
    axisy3 = []
    # y轴-4：直播总时间
    axisy4 = []
    # x轴刻度最大显示数量
    axisx_num = max_axisx_num 
    # 时间间隔
    delta = timedelta(0,table_interval)

    # 从数据库中取出最近数据
    last_data = mongo_data.find().sort([('cur_time', pymongo.DESCENDING)])  
    cur_data = last_data[0]

    # 遍历最近数据
    # 初始化累加变量
    heatsum_per_table_interval = 0
    livesum_per_table_interval = 0
    watchsum_per_table_interval = 0
    livetime_per_table_interval = 0
    count_per_table_interval = 0
    for data in last_data:
        if axisx_num <= 0:             
            break
        # 找个每个应该显示的点，计算该点对应的值
        if data['cur_time'] <= cur_data['cur_time']:
            axisx.append(str(data['cur_time'].strftime('%Y-%m-%d\n%H:%M:%S')))
            # 如果时间间隔大于等于一天，那么就计算平均值
            if table_interval >= 24 * 60 * 60 and axisx_num != max_axisx_num:
                axisy.append(heatsum_per_table_interval / count_per_table_interval)
                axisy2.append(livesum_per_table_interval / count_per_table_interval)
                axisy3.append(watchsum_per_table_interval / count_per_table_interval)
                axisy4.append(livetime_per_table_interval)
            elif table_interval < 24 * 60 * 60:
                axisy.append(getHeatPoint(data, top_live_num, top_watch_num))
                axisy2.append(data['live_num'] if data.has_key('live_num') else 0)
                axisy3.append(data['watch_num'] if data.has_key('watch_num') else 0)
                axisy4.append(data['live_time'] if data.has_key('live_time') else 0)
            # 下一个时间锚点
            cur_data['cur_time'] = data['cur_time'] - delta
            axisx_num -= 1
            heatsum_per_table_interval = 0
            livesum_per_table_interval = 0
            watchsum_per_table_interval = 0
            livetime_per_table_interval = 0
            count_per_table_interval = 0
        # 累加
        heatsum_per_table_interval += getHeatPoint(data, top_live_num, top_watch_num)
        livesum_per_table_interval += data['live_num'] if data.has_key('live_num') else 0
        watchsum_per_table_interval += data['watch_num'] if data.has_key('watch_num') else 0
        livetime_per_table_interval = data['live_time'] if data['live_time'] > livetime_per_table_interval else livetime_per_table_interval if data.has_key('live_time') else 0
        count_per_table_interval += 1

    if table_interval >= 24 * 60 * 60:
        axisy.append(heatsum_per_table_interval / count_per_table_interval)
        axisy2.append(livesum_per_table_interval / count_per_table_interval)   
        axisy3.append(watchsum_per_table_interval / count_per_table_interval)
        axisy4.append(livetime_per_table_interval)

        
    # 列表逆序 和 降低精度处理
    axisx = axisx[::-1]     
    axisy = axisy[::-1] 
    axisy2 = axisy2[::-1]
    axisy3 = axisy3[::-1]
    axisy4 = axisy4[::-1]
    axisy = map(lambda x:round(x,2),axisy)

    # 输出测试
    print axisx
    print axisy
    print axisy2
    print axisy3
    print axisy4


    ## 开始渲染
    page_title = "HeatBox - \"%s\" 热度分析"%('"、"'.join(keys))
    page = Page(page_title = page_title.decode('utf8'))

    # line
    line = Line(title = "热度趋势图")
    line.add("热度", axisx, axisy, xaxis_interval = 0, xaxis_rotate = -30, xaxis_margin = 16, is_xaxislabel_align = True, is_fill=True, area_color='#FF0000', area_opacity=0.3, mark_line=["average"], mark_point=["max", "min"])
    page.add(line)

    line2 = Line(title = "\"%s\" Bilibili 直播间数"%('"、"'.join(keys)))
    line2.add("直播间数", axisx, axisy2, xaxis_interval = 0, xaxis_rotate = -30, xaxis_margin = 16, is_xaxislabel_align = True, is_fill=True, area_color='#000000', area_opacity=0.3, mark_line=["average"], mark_point=["max", "min"])
    page.add(line2)

    line3 = Line(title = "\"%s\" Bilibili 观看直播人数"%('"、"'.join(keys)))
    line3.add("观看直播人数", axisx, axisy3, xaxis_interval = 0, xaxis_rotate = -30, xaxis_margin = 16, is_xaxislabel_align = True, is_fill=True, area_color='#00FF00', area_opacity=0.3, mark_line=["average"], mark_point=["max", "min"])
    page.add(line3)

    line4 = Line(title = "\"%s\" Bilibili 直播总时间"%('"、"'.join(keys)))
    line4.add("直播总时间", axisx, axisy4, xaxis_interval = 0, xaxis_rotate = -30, xaxis_margin = 16, is_xaxislabel_align = True, is_fill=True, area_color='#0000FF', area_opacity=0.3, mark_line=["average"], mark_point=["max", "min"])
    page.add(line4)


    page.render()


def main():
    # 主函数

    # 初始化
    printx('正在初始化……')
    mongo_global, mongo_data = Init()

    printx('开始监控 "%s" 的热度变化……\n'%('"、"'.join(keys)))
    while True:
        # 更新当前热度数据
        updateHeatPoint(mongo_global, mongo_data)

        # 渲染图表
        Render(mongo_data)

        print ''

        # 休眠一会
        time.sleep(watch_interval)




if __name__ == '__main__':
    main()
    '''
    while True:
        try:
            main()
        except Exception as e:
            printx(str(e))
    '''

