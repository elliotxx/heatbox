#coding=utf8
import sys
from datetime import datetime


# 设置
keys = ['绝地求生','吃鸡']   # 监控的关键词
watch_interval = 5          # 默认监控时间间隔，单位为秒
table_interval = 30 * 60    # x 轴的时间间隔，单位为秒
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
