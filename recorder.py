#!python
# -*- coding: UTF-8 -*-

import logging

from live_recorder import you_live

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
        self.args = {
            'save_folder': save_dir,
            'flv_save_folder': None,
            'delete_origin_file': True,
            'check_flv': True,
            'file_name_format': '{name}-{shortId} 的{liver}直播{startTime}-{endTime}',
            'time_format': '%Y%m%d_%H-%M',
            'cookies': None,
            'debug': False
        }
        self.recorder = you_live.Recorder.createRecorder('bili', self.room_id, **self.args)
        self.recorder.check_flv = True
        self.download_thread = None
        self.monitor_thread = None

    def start(self):
        self.log.info("开始录制直播间" + str(self.room_id) + "！")
        self.download_thread = you_live.DownloadThread(self.recorder)
        self.monitor_thread = you_live.MonitoringThread(self.recorder)
        self.download_thread.start()
        self.monitor_thread.start()

    def stop(self):
        self.log.info("结束录制" + str(self.room_id) + "！")
        self.recorder.downloadFlag = False
