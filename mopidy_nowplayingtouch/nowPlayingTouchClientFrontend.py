# -*- coding: utf-8 -*-

import logging
import os
import traceback
from threading import Thread
from ft5406 import Touchscreen
from gui import Button, render_widgets, touchscreen_event

from mopidy import core, exceptions

import pygame

import pykka

from .screenManager import ScreenManager


logger = logging.getLogger(__name__)


class NowPlayingTouch(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(NowPlayingTouch, self).__init__()
        self.core = core
        self.running = False
        self.cursor = config['nowplayingtouch']['cursor']
        self.cache_dir = config['nowplayingtouch']['cache_dir']

        # The way the LCD's work we have to put the height value first.
        # We do it here so the user doesnt have to do anything strange.
        self.screen_size = (config['nowplayingtouch']['screen_height'], config['nowplayingtouch']['screen_width'])
        self.resolution_factor = (config['nowplayingtouch']['resolution_factor'])

        if config['nowplayingtouch']['sdl_fbdev'].lower() != "none":
            os.environ["SDL_FBDEV"] = config['nowplayingtouch']['sdl_fbdev']

        if config['nowplayingtouch']['sdl_mousdrv'].lower() != "none":
            os.environ["SDL_MOUSEDRV"] = (config['nowplayingtouch']['sdl_mousdrv'])

        if config['nowplayingtouch']['sdl_mousedev'].lower() != "none":
            os.environ["SDL_MOUSEDEV"] = config['nowplayingtouch']['sdl_mousedev']

        if config['nowplayingtouch']['sdl_audiodriver'].lower() != "none":
            os.environ["SDL_AUDIODRIVER"] = (config['nowplayingtouch']['sdl_audiodriver'])

        os.environ["SDL_PATH_DSP"] = config['nowplayingtouch']['sdl_path_dsp']

        pygame.init()
        pygame.display.set_caption("Mopidy-NowPlayingTouch")

        self.get_display_surface(self.screen_size)
        pygame.mouse.set_visible(self.cursor)

        self.screenManager = ScreenManager(self.screen_size,
                                            self.core,
                                            self.cache_dir,
                                            self.resolution_factor)

        # Raspberry pi GPIO
        self.gpio = config['nowplayingtouch']['gpio']

        if self.gpio:

            from .input import GPIOManager

            pins = {}
            pins['left'] = config['nowplayingtouch']['gpio_left']
            pins['right'] = config['nowplayingtouch']['gpio_right']
            pins['up'] = config['nowplayingtouch']['gpio_up']
            pins['down'] = config['nowplayingtouch']['gpio_down']
            pins['enter'] = config['nowplayingtouch']['gpio_enter']

            self.gpio_manager = GPIOManager(pins)

        ts = Touchscreen()

        for touch in ts.touches:
            touch.on_press = touchscreen_event
            touch.on_release = touchscreen_event
            touch.on_move = touchscreen_event

        Button(
                label="My Button",
                color=(255, 0, 0),
                position=(300, 190),
                size=(200, 100),
                action=None)

        ts.run()

    def get_display_surface(self, size):
        try:
            self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
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

            render_widgets(self.screen)
            pygame.time.sleep(0.01)

        ts = Touchscreen()
        ts.stop()
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
        self.screenManager.playlists()

    def stream_title_changed(self, title):
        self.screenManager.stream_title_changed(title)