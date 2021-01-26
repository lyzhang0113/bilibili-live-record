#!python
# -*- coding: UTF-8 -*-
import gc
import logging
import os
import re
import time

import requests
from bilibili_api import live
from bilibili_api import utils
from live_recorder.you_live import Flv

"""
File: recorder_v2.py
Author: Doby2333
Date Created: 2021/01/24
Last Edited: 2021/01/24
Description: Does the recording thing.
Note: Only for Bilibili live, 部分内容摘抄自you-live项目
"""


class Recorder:

    def __init__(self, room_id, save_dir='./download'):
        """
        初始化Recorder，设定参数
        :param room_id: 要录制的房间号
        :param save_dir: 录制文件保存路径
        """
        self._log = logging.getLogger("main")
        self._room_id = int(room_id)
        # download_flag对外只可读，避免错误
        self._download_flag = None
        # 视频流链接和清晰度等开始录制了再获取，避免过时无法访问
        self._play_qn = ""
        self._play_url = ""
        self._save_dir = save_dir
        self._file_path = save_dir
        self.filename_format = '{name}-{roomId}的直播{startTime}-{endTime}'
        self.time_format = '%Y%m%d_%H-%M'
        self._downloaded = 0

    def start(self):
        """
        请求开始录制
        :return: None
        """
        try:
            # assert 已经开播，如果未开播抛出异常
            assert live.get_room_info(self._room_id)['room_info']['live_status'] == 1, \
                "直播间" + str(self._room_id) + "没有开播！"

            self._download_flag = True

            self._log.info("开始录制直播间" + str(self._room_id) + "！")
            # 获取直播视频流地址和清晰度
            result = live.get_room_play_url(room_real_id=self._room_id)
            self._play_qn = result['current_qn']
            self._play_url = str(result['durl'][0]['url']).replace("https://", "http://")

            # 拼接、生成文件名
            room_info = live.get_room_info(room_real_id=self._room_id)
            filename = self.filename_format.replace("{name}", str(room_info['anchor_info']['base_info']['uname']))
            filename = filename.replace("{roomId}", str(room_info['room_info']['room_id']))
            filename = filename.replace("{startTime}", time.strftime(self.time_format, time.localtime()))
            filename = re.sub(r"[\/\\\:\?\"\<\>\|']", '_', filename) + '.flv'

            # 获取保存路径
            if not os.path.exists(self._save_dir):
                os.makedirs(self._save_dir)
            self._file_path = os.path.join(os.path.abspath(self._save_dir), filename)

        except AssertionError as e:
            self._log.warning(e)
        except Exception as e:
            self._log.warning("准备录制时发生错误！正在重试！" + str(e))
            self._download_flag = False
            self.start()

        try:
            # 下载并保存流
            self._save_stream()
        except Exception as e:
            self._log.error("录制时错误！" + str(e))
        finally:
            self._download_flag = False
            # 重命名结果、校准时间轴
            self._clean_up()

    def _save_stream(self):
        """
        保存视频流
        :return: None
        """
        try:
            response = requests.get(self._play_url, stream=True, headers=utils.DEFAULT_HEADERS, timeout=180)
            file = open(self._file_path, "ab")
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not self._download_flag:
                    break
                if chunk:
                    file.write(chunk)
                    self._downloaded += len(chunk)
                if self._downloaded >= 1024 * 1024 * 32:
                    gc.collect()
                    self._downloaded = 0
            response.close()
            file.close()
        except Exception as e:
            self._log.warning("流断开，重新连接，可能造成视频文件卡顿" + str(e))
            self._play_url = str(live.get_room_play_url(room_real_id=self._room_id)['durl'][0]['url']).replace(
                "https://", "http://")
            self._save_stream()

    def _clean_up(self):
        """
        下载任务结束时，对结果文件的处理
        :return: None
        """
        try:
            # 重命名结束时间
            if '{endTime}' in self._file_path:
                curr_time = time.strftime(self.time_format, time.localtime())
                new_file_path = self._file_path.replace("{endTime}", curr_time)
                while os.path.exists(new_file_path):
                    new_file_path = str(new_file_path).replace('.flv', '_.flv')
                os.rename(self._file_path, new_file_path)
                self._file_path = new_file_path
            # 检查flv时间轴
            self._log.info("校准时间轴")
            flv = Flv(self._file_path, self._save_dir, False)
            flv.check()
            os.remove(self._file_path)
        except Exception as e:
            self._log.error("结束录制时文件处理错误！可能导致文件时间轴错误！" + str(e))

    def stop(self):
        """
        请求停止下载
        :return: None
        """
        if not self._download_flag:
            self._log.warning("当前并没有在录制！无效停止")
        else:
            self._log.info("结束录制" + str(self._room_id) + "！")
            self._download_flag = False

    def is_downloading(self):
        """
        获取下载状态
        :return: 是否正在下载
        """
        return self._download_flag
