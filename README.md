## Bangumi-api

**数据均来自于 https://hmacg.cn/bangumi ，此接口仅对其进行了处理**

Demo：

## API

  ```
  # 获取每周番剧
  /api/calendar/{年度}/{季度}
  
  请求示例：
  /api/calendar/2021/04  
  年份必须为4位，季度为 01、04、07、10 这四个之一，没做边界检查，请使用正确的方式调用！
  目前支持 2016/10-2021/04 
  ```



## Docker 安装

```bash
# 下载代码，进入代码目录
docker build -t bangumiapi:latest .

#启动方式一
docker run -itd --name bangumiapi -p 7000:8080 bangumiapi

#启动方式二（将容器挂载到代码目录 /root/Bangumi-api/ 方便更新代码
docker run -itd -e TZ="Asia/Shanghai" -v /root/Bangumi-api/:/app/ --name Bangumi-api -p 7000:8080 bangumiapi
```

## 其他操作
```bash
# 重启
docker restart bangumiapi

# 依赖文件
pip freeze > requirements.txt

```
