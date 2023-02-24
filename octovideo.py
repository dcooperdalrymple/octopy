import os
import time
import threading
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from omxplayer import OMXPlayer
from mpvplayer import MPVPlayer
from ffmpegplayer import FFmpegPlayer
from hellovideoplayer import HelloVideoPlayer

class OctoVideo():
    def __init__(self, settings):
        self.settings = settings

        # Set parameters
        self.bgcolor = self.settings.get_videobgcolor()

    def init(self):
        if not self.is_enabled():
            if self.settings.get_verbose():
                print("Video player not enabled.")
            return False

        if OMXPlayer.exists():
            self.player = OMXPlayer(self.settings)
        elif MPVPlayer.exists():
            self.player = MPVPlayer(self.settings)
        elif FFmpegPlayer.exists():
            self.player = FFmpegPlayer(self.settings)
        elif HelloPlayer.exists():
            self.player = HelloVideoPlayer(self.settings)
        else:
            if self.settings.get_verbose():
                print("Could not locate compatible video player.")
            return False

        # Initialize pygame
        pygame.display.init()
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN | pygame.NOFRAME)
        self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.bgimage = self.load_bgimage() # tuple with pyimage, xpos, ypos
        self.clear_screen()

        return True

    def close(self):
        if not self.is_enabled():
            return False
        self.stop()
        pygame.quit()
        return True

    def is_enabled(self):
        return self.settings.get_videoenabled()

    def valid_path(self, path):
        if not path or path == "" or not os.path.isfile(path):
            return False
        return True

    def load_bgimage(self):
        path = self.settings.get_videobgimage()
        if not self.valid_path(path):
            return False

        image = pygame.image.load(path)
        image_x = 0
        image_y = 0

        screen_w, screen_h = self.size
        image_w, image_h = image.get_size()

        screen_aspect_ratio = screen_w / screen_h
        image_aspect_ratio = image_w / image_h

        if screen_aspect_ratio < image_aspect_ratio: # Width is binding
            image_w = screen_w
            image_h = int(image_w / image_aspect_ratio)
            image = pygame.transform.scale(image, (image_w, image_h))
            image_y = (screen_h - image_h) // 2

        elif screen_aspect_ratio > image_aspect_ratio: # Height is binding
            image_h = screen_h
            image_w = int(image_h * image_aspect_ratio)
            image = pygame.transform.scale(image, (image_w, image_h))
            image_x = (screen_w - image_w) // 2

        else: # Same aspect ratio
            image = pygame.transform.scale(image, (screen_w, screen_h))

        return (image, image_x, image_y)

    def clear_screen(self):
        self.screen.fill(self.bgcolor)
        if self.bgimage != False and self.bgimage[0] is not None:
            self.screen.blit(self.bgimage[0], (self.bgimage[1], self.bgimage[2]))
        pygame.display.flip()

    def load(self, path):
        if not self.is_enabled():
            return False
        if not self.valid_path(path):
            return False
        self.player.load(path)
        return True

    def is_loaded(self):
        return self.player.is_loaded()

    def play(self):
        return self.player.play()

    def stop(self):
        if self.player is None:
            return False
        if not self.player.is_playing():
            return False
        self.player.stop()
        return True
