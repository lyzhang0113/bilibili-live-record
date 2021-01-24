# Bilibili 直播间录制工具

## Intro 介绍
这是一个用Python写的实时监控直播间，开播后自动录制，下播自动保存录屏的程序。
本意是可以将这个项目打包为docker镜像，挂在服务器长期运行。

本项目使用了的第三方库：

- [bilibili-api](https://github.com/Passkou/bilibili_api) 
调用Bilibili各种API的库
- [you-live](https://github.com/nICEnnnnnnnLee/LiveRecorder) 
录制直播

特别感谢上述库的作者，库很好用！

## Config 配置

### 本地运行
配置文件存储在**config.ini**
**需要存在配置文件且字段正确，程序才能运行！**

### Docker
docker run时配置环境变量
```
LOG_LEVEL=INFO
ROOM_ID=12345
SAVE_DIR=./download
```
环境变量会覆盖config.ini的配置！

## QuickStart 快速开始
### Docker
1. 打包自己的docker镜像
```
docker build doby2333/live_recorder .
```
2. 运行docker镜像
不添加环境变量： （修改config.ini)
```
docker run --name live_recorder -d doby2333/live_recorder
```
使用环境变量：
```
docker run --name live_recorder --env LOG_LEVEL=INFO --env ROOM_ID=12345 -- SAVE_DIR=./download -d doby2333/live_recorder
```