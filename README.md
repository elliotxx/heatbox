## heatbox - 热度走势图

### 特性
* 自定义 x 轴刻度个数
* 自定义 x 轴时间间隔
* 代理池

### 安装依赖
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
    use heatbox			// 创建 heatbox 数据库
    db.createUser(
        {
        user:'admin',	// heatbox 数据库的操作用户
        pwd:'admin123',	// heatbox 数据库的用户密码
        roles:[{role:'readWrite',db:'heatbox'}] 	// 用户权限
        }
    )
    ```

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
    * server.sh：启动/停止/重启/查看 heatbox 服务，用法：  
    ```
    Usages: sh server.sh [start|stop|restart|status]
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
