import logging
import threading

from recorder_v2 import Recorder


class RecordThread(threading.Thread):

    def __init__(self, recorder: Recorder):
        threading.Thread.__init__(self, name='recording')
        self.recorder = recorder
        self.log = logging.getLogger("main")

    def run(self):
        self.recorder.start()
        self.log.warning("下载线程结束")

    def stop(self):
        self.recorder.stop()

    def isRecording(self):
        return self.recorder.download_flag
