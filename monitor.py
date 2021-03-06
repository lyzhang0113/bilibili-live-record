#!python
# -*- coding: UTF-8 -*-

import logging

from bilibili_api import live

"""
File: monitor.py
Author: Doby2333
Date Created: 2021/01/24
Last Edited: 2021/01/24
Description: Monitor Room Status
"""


class Monitor:

    def __init__(self, room_id):
        """
        Bilibili直播间监视器对象
        :param room_id: 房间号
        """
        self.log = logging.getLogger("main")
        self.room_id = room_id
        self.room = live.LiveDanmaku(room_display_id=room_id)
        room_info = live.get_room_info(room_real_id=room_id)
        uname = str(room_info['anchor_info']['base_info']['uname'])
        self.log.info("准备监控 [" + uname + "] 的直播间，房间号：" + str(room_id))
        self.isStreaming = room_info['room_info']['live_status'] == 1
        self.log.info("当前主播状态：" + "正在直播" if self.isStreaming else "未开播")

    def connect(self):
        """
        连接直播间进行监控
        """
        # 因为有可能在连接断开时下播，所以更新直播状态
        self.isStreaming = (live.get_room_info(self.room_id)['room_info']['live_status'] == 1)
        try:
            self.room.connect()
        except:
            # 有时候网络不稳定会导致掉线，尝试重连，无限循环
            self.room.disconnect()
            self.connect()
