from sepmachine.capture.base import BaseCapture

import typing
import time
import ffmpeg
import tempfile
import os
from loguru import logger
from minadb import ADBDevice


class AdbCapture(BaseCapture):
    def __init__(self, serial_no: str, fps: int = 60):
        # args
        self.serial_no: str = serial_no
        self.fps: int = fps

        # others
        self.device: ADBDevice = ADBDevice(self.serial_no)
        self.record_stop: typing.Optional[typing.Callable] = None
        self.video_path: str = ""
        logger.info(f"config: {self.__dict__}")

    def start(self, video_path: str) -> bool:
        self.record_stop = self.device.screen_record()
        self.video_path = video_path
        return True

    def operate(self) -> bool:
        time.sleep(5)
        return True

    def end(self) -> bool:
        assert self.record_stop and self.video_path

        # save to temp file
        temp_video = tempfile.NamedTemporaryFile(mode="wb+", suffix=".mp4", delete=False)
        temp_video_path = temp_video.name
        self.record_stop(temp_video_path)
        logger.info(f"video saved to {temp_video_path}")

        try:
            # ffmpeg converter
            stream = ffmpeg.input(temp_video_path)
            stream = ffmpeg.filter(stream, 'fps', fps=self.fps)
            stream = ffmpeg.output(stream, self.video_path)
            ffmpeg.run(stream, overwrite_output=True)
        except FileNotFoundError:
            logger.warning("no ffmpeg installation found")
            logger.warning("skip fps converter")
        logger.info(f"video convert finished. fps: {self.fps}")

        # remove temp file
        os.remove(temp_video_path)
        logger.debug(f"removed: {temp_video_path}")

        return True
