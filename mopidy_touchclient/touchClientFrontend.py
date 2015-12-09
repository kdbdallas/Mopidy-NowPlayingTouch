# -*- coding: utf-8 -*-

import logging
import os
import traceback
from threading import Thread

from mopidy import core, exceptions

import pygame

import pykka

from .screenManager import ScreenManager


logger = logging.getLogger(__name__)


class TouchClient(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(TouchClient, self).__init__()
        self.core = core
        self.running = False
        self.cursor = config['touchclient']['cursor']
        self.cache_dir = config['touchclient']['cache_dir']
        self.screen_size = (config['touchclient']['screen_width'], config['touchclient']['screen_height'])
        self.resolution_factor = (config['touchclient']['resolution_factor'])

        if config['touchclient']['sdl_fbdev'].lower() != "none":
            os.environ["SDL_FBDEV"] = config['touchclient']['sdl_fbdev']

        if config['touchclient']['sdl_mousdrv'].lower() != "none":
            os.environ["SDL_MOUSEDRV"] = (config['touchclient']['sdl_mousdrv'])

        if config['touchclient']['sdl_mousedev'].lower() != "none":
            os.environ["SDL_MOUSEDEV"] = config['touchclient']['sdl_mousedev']

        if config['touchclient']['sdl_audiodriver'].lower() != "none":
            os.environ["SDL_AUDIODRIVER"] = (config['touchclient']['sdl_audiodriver'])

        os.environ["SDL_PATH_DSP"] = config['touchclient']['sdl_path_dsp']

        pygame.init()
        pygame.display.set_caption("Mopidy-Touchscreen")
        pygame.mouse.set_visible(self.cursor)

        self.get_display_surface(self.screen_size)

        self.screenManager = ScreenManager(self.screen_size,
                                            self.core,
                                            self.cache_dir,
                                            self.resolution_factor)

        # Raspberry pi GPIO
        self.gpio = config['touchclient']['gpio']

        if self.gpio:

            from .input import GPIOManager

            pins = {}
            pins['left'] = config['touchclient']['gpio_left']
            pins['right'] = config['touchclient']['gpio_right']
            pins['up'] = config['touchclient']['gpio_up']
            pins['down'] = config['touchclient']['gpio_down']
            pins['enter'] = config['touchclient']['gpio_enter']

            self.gpio_manager = GPIOManager(pins)

    def get_display_surface(self, size):
        try:
            if self.fullscreen:
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        except Exception:
            raise exceptions.FrontendError("Error on display init:\n" + traceback.format_exc())

    def start_thread(self):
        clock = pygame.time.Clock()
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        while self.running:
            clock.tick(12)
            self.screenManager.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os.system("pkill mopidy")
                elif event.type == pygame.VIDEORESIZE:
                    self.get_display_surface(event.size)
                    self.screenManager.resize(event)
                else:
                    self.screenManager.event(event)
        pygame.quit()

    def on_start(self):
        try:
            self.running = True
            thread = Thread(target=self.start_thread)
            thread.start()
        except:
            traceback.print_exc()

    def on_stop(self):
        self.running = False

    def track_playback_started(self, tl_track):
        try:
            self.screenManager.track_started(tl_track)
        except:
            traceback.print_exc()

    def volume_changed(self, volume):
        self.screenManager.volume_changed(volume)

    def playback_state_changed(self, old_state, new_state):
        self.screenManager.playback_state_changed(old_state, new_state)

    def tracklist_changed(self):
        try:
            self.screenManager.tracklist_changed()
        except:
            traceback.print_exc()

    def track_playback_ended(self, tl_track, time_position):
        self.screenManager.track_playback_ended(tl_track, time_position)

    def options_changed(self):
        try:
            self.screenManager.options_changed()
        except:
            traceback.print_exc()

    def playlists_loaded(self):
        self.screenManager.playlists_loaded()

    def stream_title_changed(self, title):
        self.screenManager.stream_title_changed(title)