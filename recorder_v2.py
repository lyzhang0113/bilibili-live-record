#!python
# -*- coding: UTF-8 -*-

import logging
import os
import re
import time

import requests
from bilibili_api import live
from bilibili_api import utils
from live_recorder.you_live.flv_checker import Flv

"""
File: recorder.py
Author: Doby2333
Date Created: 2021/01/24
Last Edited: 2021/01/24
Description: Does the recording thing.
Note: Only for Bilibili live
"""


class Recorder:

    def __init__(self, room_id, save_dir='./download'):
        """
        初始化Recorder，设定参数
        :param room_id: 要录制的房间号
        :param save_dir: 录制文件保存路径
        """
        self.log = logging.getLogger("main")
        self.room_id = int(room_id)
        result = live.get_room_play_url(room_real_id=room_id)
        self.download_flag = True
        self.play_qn = result['current_qn']
        self.play_url = str(result['durl'][0]['url']).replace("https://", "http://")
        self.save_dir = save_dir
        self.file_path = save_dir
        self.filename_format = '{name}-{roomId} 的直播{startTime}-{endTime}'
        self.time_format = '%Y%m%d_%H-%M'
        self.downloaded = 0

    def start(self):
        try:
            self.download_flag = True
            assert live.get_room_info(self.room_id)['room_info']['live_status'] == 1
            self.log.info("开始录制直播间" + str(self.room_id) + "！")
            result = live.get_room_play_url(room_real_id=self.room_id)
            self.play_qn = result['current_qn']
            self.play_url = result['durl'][0]['url']

            # 拼接文件名
            room_info = live.get_room_info(room_real_id=self.room_id)
            filename = self.filename_format.replace("{name}", str(room_info['anchor_info']['base_info']['uname']))
            filename = filename.replace("{roomId}", str(room_info['room_info']['room_id']))
            curr_time = time.strftime(self.time_format, time.localtime())
            filename = filename.replace("{startTime}", curr_time)
            filename = re.sub(r"[\/\\\:\?\"\<\>\|']", '_', filename)
            filename = filename + ".flv"

            # 获取保存路径
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
            self.file_path = os.path.join(os.path.abspath(self.save_dir), filename)

            # 保存流
            self.save_stream()

            self.clean_up()

            self.download_flag = False

        except Exception as e:
            self.log.error("录制错误，重试开始" + str(e))
            self.clean_up()
            self.download_flag = False
            self.start()

    def save_stream(self):
        try:
            with open(self.file_path, "wb") as file:
                response = requests.get(self.play_url, stream=True, headers=utils.DEFAULT_HEADERS, timeout=180)
                for data in response.iter_content(chunk_size=1024 * 1024):
                    if not self.download_flag:
                        break
                    file.write(data)
                    self.downloaded += len(data)
                response.close()
        except:
            self.log.warning("流断开，重新连接")
            self.play_url = str(live.get_room_play_url(room_real_id=self.room_id)['durl'][0]['url']).replace("https://",
                                                                                                             "http://")
            self.save_stream()

    def clean_up(self):
        # 重命名
        if '{endTime}' in self.file_path:
            curr_time = time.strftime(self.time_format, time.localtime())
            new_file_path = self.file_path.replace("{endTime}", curr_time)
            os.rename(self.file_path, new_file_path)
            self.file_path = new_file_path

        # 检查flv时间轴
        self.log.info("校准时间轴")
        flv = Flv(self.file_path, self.save_dir, False)
        flv.check()

    def stop(self):
        self.log.info("结束录制" + str(self.room_id) + "！")
        self.download_flag = False
