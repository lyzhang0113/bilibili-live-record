import logging
import threading

from recorder_v2 import Recorder

"""
File: record_thread.py
Author: Doby2333
Date Created: 2021/01/24
Last Edited: 2021/01/24
Description: 起一个线程负责录制
"""


class RecordThread(threading.Thread):

    def __init__(self, recorder: Recorder):
        threading.Thread.__init__(self, name='recording')
        self.recorder = recorder
        self.log = logging.getLogger("main")

    def run(self):
        self.recorder.start()
        self.log.warning("录制线程结束")

    def stop(self):
        self.recorder.stop()

    def isRecording(self):
        return self.recorder.is_downloading()
