import os
from videoplayer import VideoPlayerProcess

class MPVPlayer(VideoPlayerProcess):

    def __init__(self, settings = None):
        super().__init__(settings)

    def get_arguments(self):
        args = [self.get_command()]
        args.append('--fs') # Fullscreen
        args.append('--fs-screen=all') # Disable on all screens
        args.append('--no-audio') # Remove audio
        args.append('--no-terminal') # Disable terminal output
        #args.append('--ontop') # Force on top
        args.append('--input-vo-keyboard=no')
        args.append('--no-input-default-bindings')
        args.append('--no-config')
        args.append('--no-osd-bar')
        args.append('--no-osc')
        args.append(self.path)
        return args

    @staticmethod
    def get_extensions(self):
        return ['avi', 'mov', 'mkv', 'mp4', 'm4v']

    @staticmethod
    def get_command():
        return 'mpv'
