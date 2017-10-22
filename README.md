## heatbox - 热度走势图

### 演示地址
[http://heatbox.yangyingming.com](http://heatbox.yangyingming.com)

### 特性
* 自定义 x 轴刻度个数
* 自定义 x 轴时间间隔
* 代理池

### 安装依赖
* requests
* pymongo
* pyecharts

### MongoDB 配置
1. 开启 MongoDB 权限认证：**在配置文件中加入 auth = true**

2. 创建管理员用户（如果你是第一次使用 MongoDB）  
```
use admin
db.createUser({user:"admin",pwd:"admin123",roles:["userAdminAnyDatabase"]})
```
管理员用户用来创建其他数据库和用户

3. 使用管理员账户远程登录
```
C:\Users\cs>mongo [your_ip]:27017
> use admin
switched to db admin
> db.auth('admin','admin123')
1
```

4. 创建 heatbox 数据库，以及操作该数据库的用户
```
use heatbox         // 创建 iHealth 数据库，并作为认证数据库
db.createUser({
    user:'admin',   // 用户名
    pwd:'admin123', // 用户密码
    roles:[{role:'readWrite',db:'heatbox'}]     // 为该用户赋予数据库的读写权限
})
```

5. 使用该用户远程登录 heatbox 数据库
```
C:\Users\cs>mongo [your_ip]:27017
> use heatbox
switched to db heatbox
> db.auth('admin','admin123')
1
> db.getCollectionNames()
[ ]
```
数据库刚刚创建，所以没有数据


### 启动说明
1. 安装环境：Python 环境和依赖 + MongoDB 配置

2. 配置 common.py 中的数据库信息
```
# 数据库配置
mongo_dbname = 'heatbox'
mongo_host = 'your_ip'          # mongodb 主机地址
mongo_port = 27017              # mongodb 主机端口
mongo_user = 'your_user'        # mongodb 登陆用户
mongo_pwd  = 'your_password'    # mongodb 用户密码
```

3. 运行
    * Windows :  
    ```
    python heatbox.py
    ```  
    * Linux :  
    ```
    sh server.sh start
    ```

4. 测试
    * Windows :  
    在浏览器中打开生成的 render.html 
    * Linux :  
    运行脚本 start-webserver.sh，然后用本地浏览器访问 http://[your_vps_ip]:8010/render.html
    * 等待一会即可看到渲染结果

### 注意
* 脚本功能：
    * start-webserver.sh：启动临时 http 服务器（linux）
    * server.sh：启动/停止/重启/查看状态/查看日志 heatbox 服务，用法：  
    ```
    Usages: sh server.sh [start|stop|restart|status|log]
    ```

### 游戏关键字
* 绝地求生
* 吃鸡

### 监控指标
* Bilibili
	* 直播间数量
	* 直播总时长（从当天程序开始运行时计时，每隔一段时间检测一次）
	* 观看直播总人数

### 热度得分计算公式
```
直播间数量：live_num
观看直播总人数：watch_num
曾出现过的最高直播间总数：top_live_num	# 这个值一旦出现变化，那么之前计算的所有得分都要重新计算一遍
曾出现过的最高观看直播人数：top_watch_num
当天的直播总时长（分钟）：live_time

当天的热度得分：heat_point = float(live_num) / top_live_num * 100 + float(watch_num) / top_watch_num * 100 + float(live_time) / (24*60*60*live_num) * 100
```

### 关于代理
* bilibili 只能用 http 协议的代理IP，使用 https 代理会请求失败

### 参考资料
* python时间处理之datetime  
http://blog.csdn.net/wirelessqa/article/details/7973121
