import os
from videoplayer import VideoPlayerProcess

class FFmpegPlayer(VideoPlayerProcess):

    def __init__(self, settings = None):
        super().__init__(settings)

    def get_arguments(self):
        args = [self.get_command()]
        args.append('-fs') # Fullscreen
        args.append('-an') # Disable audio
        args.append('-sn') # Disable subtitles
        args.append('-noborder') # Borderless window
        args.append('-exitonkeydown')
        args.extend(['-loop', '0']) # Loop forever
        args.extend(['-loglevel', 'quiet']) # Disable verbose output
        args.append(self.path)
        return args

    @staticmethod
    def get_name():
        return 'FFmpeg'

    @staticmethod
    def get_extensions():
        return ['avi', 'mov', 'mkv', 'mp4', 'm4v']

    @staticmethod
    def get_command():
        return 'ffplay'
