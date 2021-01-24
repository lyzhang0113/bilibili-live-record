#!python
# -*- coding: UTF-8 -*-
import asyncio
import logging
import os
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from configparser import RawConfigParser

from monitor import Monitor
from recorder_v2 import Recorder
from thread_workers import RecordThread

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
monitor = Monitor(room_id=room_id)
recorder = Recorder(room_id=room_id, save_dir=save_dir)
recorder_thread = RecordThread(recorder=recorder)


@monitor.room.on("LIVE")  # 直播开始
async def on_live(msg):
    global recorder_thread
    log.info("********************【直播开始】********************")
    monitor.isStreaming = True
    # 开始录制线程
    safe_start_recording()
    pass


@monitor.room.on("PREPARING")  # 直播结束
async def on_prepare(msg):
    log.info("********************【直播结束】********************")
    monitor.isStreaming = False
    # 结束录制线程
    recorder_thread.stop()
    pass


def safe_start_recording():
    global recorder_thread
    if recorder_thread.isRecording():
        log.warning("下载线程已启动！不能重复启动！")
        return
    recorder_thread = RecordThread(recorder=recorder)
    recorder_thread.start()


async def ainput(prompt: str = ""):
    log.info("在控制台输入stop以停止下载，输入start以开始下载")
    with ThreadPoolExecutor(1, "AsyncInput", lambda x: print(x, end="", flush=True), (prompt,)) as executor:
        return (await asyncio.get_event_loop().run_in_executor(
            executor, sys.stdin.readline
        )).rstrip()


async def wait_for_stop():
    global recorder_thread
    while True:
        input_waited = await ainput()
        if input_waited == "stop":
            recorder_thread.stop()
        elif input_waited == "start":
            safe_start_recording()
        else:
            log.warning("无效输入！输入stop以停止下载，输入start以开始下载")


if __name__ == '__main__':
    # 持续接受控制台输入，收到输入就发送停止录制请求
    asyncio.get_event_loop().create_task(wait_for_stop())
    # 如果运行时就在直播，则启动录制线程
    if monitor.isStreaming:
        safe_start_recording()
    # 开启对直播间的监控，监听《直播开始》《直播结束》事件
    monitor.connect()
