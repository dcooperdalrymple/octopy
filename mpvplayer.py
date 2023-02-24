import os
from videoplayer import VideoPlayerProcess

class MPVPlayer(VideoPlayerProcess):

    def __init__(self, settings = None):
        super().__init__(settings)

    def get_arguments(self):
        args = [self.get_command()]
        args.append('--no-config') # Prevent loading local config
        args.append('--fs') # Fullscreen
        args.append('--fs-screen=all') # Disable on all screens
        args.append('--no-audio') # Remove audio
        args.append('--no-terminal') # Disable terminal output
        #args.append('--ontop') # Force on top
        args.append('--no-input-default-bindings') # Disable keyboard bindings
        args.append('--input-vo-keyboard=no')
        args.append('--no-osc') # Disable On-Screen Controller
        args.append('--no-osd-bar') # Disable On-Screen Display
        args.append('--loop')
        args.append(self.path)
        return args

    @staticmethod
    def get_name():
        return 'MPV'

    @staticmethod
    def get_extensions():
        return ['avi', 'mov', 'mkv', 'mp4', 'm4v']

    @staticmethod
    def get_command():
        return 'mpv'
