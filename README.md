## heatbox - 热度走势图

### 依赖
* requests
* pymongo
* pyecharts

### MongoDB 配置
1. 开启 MongoDB 权限认证，创建管理员用户  
    可参考：http://gogs.yangyingming.com/windcode/my-db  
    假设创建的管理员账户为：
    
    ```
    user: admin
    password: admin123
    ```
2. 远程连接 MongoDB

    ```
    mongo mongodb://[your_ip]:27017
    ```
3. 运行如下代码可创建 heatbox 数据库用户

    ```
    use admin
    db.auth('admin','admin123')
    use heatbox			# 创建 heatbox 数据库
    db.createUser(
        {
        user:'admin',	# heatbox 数据库的操作用户
        pwd:'admin123',	# heatbox 数据库的用户密码
        roles:[{role:'readWrite',db:'heatbox'}] 	# 用户权限
        }
    )
    ```

### 游戏关键字
* 绝地求生
* 吃鸡

### 监控指标
* bilibili
	* 直播间数量
	* 直播总时长（从当天程序开始运行时计时，每隔一段时间检测一次）
	* ~~直播观看总人数~~

### 热度得分计算公式
```
直播间数量：live_num
曾出现过的最高直播间总数：top_live_num	# 这个值一旦出现变化，那么之前计算的所有得分都要重新计算一遍
当天的直播总时长（分钟）：live_time

当天的热度得分：heat_point = float(live_num) / top_live_num * 100 + float(live_time) / (24*60*60) * 100
```

### 参考资料
* python时间处理之datetime  
http://blog.csdn.net/wirelessqa/article/details/7973121