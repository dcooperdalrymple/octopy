import os
import time
import threading
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from pvplayer2 import PyVidPlayer2
from omxplayer import OMXPlayer
from mpvplayer import MPVPlayer
from ffmpegplayer import FFmpegPlayer
from hellovideoplayer import HelloVideoPlayer

class OctoVideo():
    def __init__(self, settings):
        self.settings = settings
        self.player = None
        self.clock = pygame.time.Clock()

        # Set parameters
        self.bgcolor = self.settings.get_videobgcolor()
        self.screenargs = pygame.FULLSCREEN | pygame.NOFRAME
        self.screendepth = 32

    def init(self):
        if not self.is_enabled():
            if self.settings.get_verbose():
                print("Video player not enabled.\n")
            return False

        self.player = None

        # Available video players (in order of preference)
        players = [
            PyVidPlayer2,
            OMXPlayer,
            MPVPlayer,
            FFmpegPlayer,
            HelloVideoPlayer
        ]

        # List available video players
        if self.settings.get_verbose():
            print("Available Video Players:")
            i = 0
            for player in players:
                if player.exists():
                    i += 1
                    print("  {:d}: {}".format(i, player.get_name()))

        # Get desired video player first if available
        if self.settings.get_videoplayer() != '':
            print("Desired Video Player: {}".format(self.settings.get_videoplayer()))
            for player in players:
                if player.get_name().lower().strip() == self.settings.get_videoplayer().lower().strip() and player.exists():
                    self.player = player(self.settings)
                    break

        # Get first available video player
        if self.player is None:
            for player in players:
                if player.exists():
                    self.player = player(self.settings)
                    break

        if self.player is None:
            if self.settings.get_verbose():
                print("Could not locate compatible video player.\n")
            return False
        else:
            print("Selected Video Player: {}".format(self.player.get_name()))

        # Initialize pygame
        pygame.display.init()
        pygame.mouse.set_visible(False)

        # Initialize screen
        self.screenrect = pygame.Rect(0, 0, pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screendepth = pygame.display.mode_ok(self.screenrect.size, self.screenargs, self.screendepth)
        self.screen = pygame.display.set_mode(self.screenrect.size, self.screenargs, self.screendepth)

        self.bgimage = self.load_bgimage() # tuple with pyimage, xpos, ypos
        self.clear_screen()

        return True

    def update(self):
        self.clock.tick(60) # Frame rate

        if self.player is None:
            return False

        if not self.player.update(self.screen):
            return False

        pygame.display.update()
        return True

    def close(self):
        if not self.is_enabled():
            return False
        self.stop()
        pygame.quit()
        return True

    def is_enabled(self):
        return self.settings.get_videoenabled()
    
    def sanitize_path(self, path):
        if not path or path == "":
            return ""
        return os.path.abspath(os.path.expanduser(path))

    def valid_path(self, path):
        if not path or path == "" or not os.path.isfile(path):
            return False
        return True

    def load_bgimage(self):
        path = self.settings.get_videobgimage()
        if self.settings.get_verbose():
            print("Loading video background image: {}".format(path))
        path = self.sanitize_path(path)
        if not self.valid_path(path):
            if self.settings.get_verbose():
                print("Unable to load video background image.")
            return False

        image = pygame.image.load(path)
        image_x = 0
        image_y = 0

        screen_w, screen_h = self.screenrect.size
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

        if self.settings.get_verbose():
            print("Successfully loaded video background image!")

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
        if self.player is None:
            return False
        self.player.load(path, self.screenrect.size)
        return True

    def is_loaded(self):
        return not self.player is None and self.player.is_loaded()

    def play(self):
        return not self.player is None and self.player.play()

    def stop(self):
        if self.player is None:
            return False
        if not self.player.is_playing():
            return False
        self.player.stop()
        self.clear_screen()
        return True
