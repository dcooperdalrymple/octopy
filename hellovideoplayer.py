import os
from videoplayer import VideoPlayerProcess

class HelloVideoPlayer(VideoPlayerProcess):

    def __init__(self, settings = None):
        super().__init__(settings)

    def get_arguments(self):
        args = [self.get_command()]
        args.append('--loop')
        args.append(self.path)
        return args

    @staticmethod
    def get_name():
        return 'hello_video'

    @staticmethod
    def get_extensions(self):
        return ['h264']

    @staticmethod
    def get_command():
        return 'hello_video.bin'
