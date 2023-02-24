import os
from videoplayer import VideoPlayerProcess

class OMXPlayer(VideoPlayerProcess):

    def __init__(self, settings = None):
        super().__init__(settings)

    def get_arguments(self):
        args = [self.get_command()]
        args.append('--loop')
        args.append('--no-keys')
        args.append(self.path)
        return args

    @staticmethod
    def get_name():
        return 'OMX'

    @staticmethod
    def get_extensions(self):
        return ['avi', 'mov', 'mkv', 'mp4', 'm4v']

    @staticmethod
    def get_command():
        return 'omxplayer'
