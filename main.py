#!python
# -*- coding: UTF-8 -*-

import logging
import os
import sys
from configparser import RawConfigParser

import monitor
import recorder

"""
File: main.py
Author: Doby2333
Date Created: 2021/01/24
Last Edited: 2021/01/24
Description: Monitor and Start/Stop Recorder 
"""

# 读取配置
# 环境变量
log_level = os.environ.get('LOG_LEVEL')
room_id = os.environ.get('ROOM_ID')
save_dir = os.environ.get('SAVE_DIR')
# 配置文件
config = RawConfigParser()
config.read('config.ini', encoding='utf-8')
log_level = log_level if log_level is not None else config.get('Log', 'level')
room_id = int(room_id) if room_id is not None else config.getint('Bilibili', 'room')
save_dir = save_dir if save_dir is not None else config.get('Recording', 'save_dir')

# 日志
log = logging.getLogger("main")
log.setLevel(log_level)
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s]\t%(message)s'))
log.addHandler(log_handler)
log.info("当前日志记录等级：" + logging.getLevelName(log.level))

# Recorder 和 Monitor
recorder = recorder.Recorder(room_id=room_id, save_dir=save_dir)
monitor = monitor.Monitor(room_id)


@monitor.room.on("LIVE")  # 直播开始
async def on_live(msg):
    log.info("********************【直播开始】********************")
    monitor.isStreaming = True
    # 准备开始录制
    recorder.start()
    pass


@monitor.room.on("PREPARING")  # 直播结束
async def on_prepare(msg):
    log.info("********************【直播结束】********************")
    monitor.isStreaming = False
    # 结束录制，保存
    recorder.stop()
    pass


if __name__ == '__main__':
    if monitor.isStreaming:
        recorder.start()
    monitor.connect()
