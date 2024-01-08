import os
import time
from videoplayer import VideoPlayer

class PyVidPlayer2(VideoPlayer):

    def __init__(self, settings = None):
        self.vid = None
        super().__init__(settings)

    def load(self, path, size=None):
        if not super().load(path):
            return False

        try:
            from pyvidplayer2 import Video
        except ImportError as err:
            print("Could not load {} module.".format(err))
            raise SystemExit

        self.stop(False)
        self.vid = Video(self.path, use_pygame_audio=True)
        self.vid.resize(size)
        self.vid.play()
        self.vid.pause()
        self.vid.set_volume(0.0)
        self.vid.mute()

        return True

    def is_loaded(self):
        return super().is_loaded() and not self.vid is None

    def play(self):
        if not super().play():
            return False

        self.vid.restart()
        self.vid.resume()
        return True

    def update(self, surface=None):
        if not self.is_loaded():
            return False

        if surface is None:
            return False
        
        if self.vid.get_paused():
            return False
        
        self.vid.draw(surface, (0, 0), force_draw=False)
        return True

    def stop(self, clear=True):
        if not super().stop(clear):
            return False

        if self.vid is None:
            return False

        if clear:
            self.vid.close()
            self.vid = None
        else:
            self.vid.pause()

        return True

    @staticmethod
    def get_name():
        return 'pyvidplayer2'

    @staticmethod
    def get_extensions():
        return ['avi', 'mov', 'mkv', 'mp4', 'm4v']

    @staticmethod
    def exists():
        try:
            from pyvidplayer2 import Video
        except ImportError as err:
            return False
        return True
