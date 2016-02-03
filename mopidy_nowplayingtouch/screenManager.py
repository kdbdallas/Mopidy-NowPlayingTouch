# -*- coding: utf-8 -*-

import logging
import traceback

import sys

from graphic_utils import DynamicBackground, \
    ScreenObjectsManager, TouchAndTextItem
from input import InputManager

import mopidy

from pkg_resources import Requirement, resource_filename

import pygame
#import pdb

# StreamsScreen, SystemScreen, NowPlayingScreen
from screens import BaseScreen, Keyboard, BrowseScreen, MainScreen,\
    PlaylistScreen, QueueScreen, SearchScreen, MenuScreen


logger = logging.getLogger(__name__)


mainScreenIndex = 0
#nowPlayingIndex = 1
#queueIndex = 2
#playlistsIndex = 3
#browseIndex = 4
#streamsIndex = 5
#searchIndex = 6
#SystemIndex = 7
#MenuIndex = 8

#queueIndex = 1
#playlistsIndex = 2
#browseIndex = 3
#searchIndex = 4
#MenuIndex = 5

MenuIndex = 1

class ScreenManager():

    def __init__(self, size, core, cache, resolution_factor):
        self.core = core
        self.cache = cache
        self.fonts = {}
        self.background = None
        self.currentScreen = mainScreenIndex

        # Init variables in init
        self.baseSize = None
        self.size = None
        self.screens = None
        self.track = None
        self.input_manager = InputManager(size)
        self.down_bar_objects = ScreenObjectsManager()
        self.down_bar = None
        self.keyboard = None
        self.updateType = BaseScreen.update_all

        self.resolution_factor = resolution_factor
        self.init_manager(size)

    def init_manager(self, size):
        self.size = size
        self.baseSize = self.size[1] / self.resolution_factor
        self.background = DynamicBackground(self.size)

        font = resource_filename(Requirement.parse("mopidy-nowplayingtouch"), "mopidy_nowplayingtouch/FontAwesome.otf")

        self.fonts['base'] = pygame.font.SysFont("arial", int(self.baseSize*0.9))
        self.fonts['icon'] = pygame.font.Font(font, int(self.baseSize*0.9))
        #pdb.set_trace()
        try:
            self.screens = [
                MainScreen(size, self.baseSize, self, self.fonts, self.cache, self.core, self.background),
                MenuScreen(size, self.baseSize, self, self.fonts, self.core)]
            #pdb.set_trace()
        except:
            traceback.print_exc()
        #pdb.set_trace()
        self.track = None

        # Menu buttons

        button_size = (self.size[0] / 6, self.baseSize)

        # Main button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue001",
                                  (0, self.size[1] - self.baseSize),
                                  button_size, center=True)
        self.down_bar_objects.set_touch_object("menu_0", button)
        x = button.get_right_pos()

        # Search button
        button = TouchAndTextItem(self.fonts['icon'], u" \ue002",
                                  (x, self.size[1] - self.baseSize),
                                  button_size, center=True)

        self.down_bar_objects.set_touch_object("menu_1", button)
        x = button.get_right_pos()
        #pdb.set_trace()
        self.options_changed()
        self.mute_changed(self.core.playback.mute.get())
        playback_state = self.core.playback.state.get()
        self.playback_state_changed(playback_state, playback_state)
        self.screens[MenuIndex].check_connection()

        self.change_screen(self.currentScreen)

        self.updateType = BaseScreen.update_all

    def get_update_type(self):
        if self.updateType == BaseScreen.update_all:
            self.updateType = BaseScreen.no_update
            return BaseScreen.update_all
        else:
            if self.keyboard:
                return BaseScreen.no_update
            else:
                if self.background.should_update():
                    return BaseScreen.update_all
                else:
                    if self.screens[self.currentScreen].should_update():
                        return BaseScreen.update_partial
                    else:
                        return BaseScreen.no_update

    def update(self, screen):
        update_type = self.get_update_type()
        if update_type != BaseScreen.no_update:
            rects = []
            surface = self.background.draw_background()
            if self.keyboard:
                self.keyboard.update(surface)
            else:
                self.screens[self.currentScreen].update(surface, update_type, rects)
                surface.blit(self.down_bar, (0, self.size[1] - self.baseSize))
                self.down_bar_objects.render(surface)

            if update_type == BaseScreen.update_all or len(rects) < 1:
                screen.blit(surface, (0, 0))
                pygame.display.flip()
            else:
                for rect in rects:
                    screen.blit(surface, rect, area=rect)
                pygame.display.update(rects)

    def track_started(self, track):
        self.track = track
        self.screens[mainScreenIndex].track_started(track.track)
        self.screens[nowPlayingIndex].track_started(track)

    def track_playback_ended(self, tl_track, time_position):
        self.screens[mainScreenIndex].track_playback_ended(tl_track, time_position)

    def event(self, event):
        event = self.input_manager.event(event)

        if event is not None:
            if self.keyboard is not None:
                self.keyboard.touch_event(event)
            elif not self.manage_event(event):
                self.screens[self.currentScreen].touch_event(event)
            self.updateType = BaseScreen.update_all

    def manage_event(self, event):
        if event.type == InputManager.click:
            objects = self.down_bar_objects.get_touch_objects_in_pos(event.current_pos)
            return self.click_on_objects(objects, event)
        else:
            if event.type == InputManager.key and not event.longpress:
                dir = event.direction
                if dir == InputManager.right or dir == InputManager.left:
                    if not self.screens[self.currentScreen]\
                            .change_screen(dir):
                        if dir == InputManager.right:
                            self.change_screen(self.currentScreen+1)
                        else:
                            self.change_screen(self.currentScreen-1)
                    return True
                elif event.unicode is not None:
                    if event.unicode == "n":
                        self.core.playback.next()
                    elif event.unicode == "p":
                        self.core.playback.previous()
                    elif event.unicode == "+":
                        volume = self.core.playback.volume.get() + 10
                        if volume > 100:
                            volume = 100
                        self.core.mixer.set_volume(volume)
                    elif event.unicode == "-":
                        volume = self.core.playback.volume.get() - 10
                        if volume < 0:
                            volume = 0
                        self.core.mixer.set_volume(volume)
                    elif event.unicode == " ":
                        if self.core.playback.get_state().get() == \
                                mopidy.core.PlaybackState.PLAYING:
                            self.core.playback.pause()
                        else:
                            self.core.playback.play()
            return False

    def volume_changed(self, volume):
        self.screens[mainScreenIndex].volume_changed(volume)
        self.updateType = BaseScreen.update_all

    def playback_state_changed(self, old_state, new_state):
        self.screens[mainScreenIndex].playback_state_changed(old_state, new_state)
        self.updateType = BaseScreen.update_all

    def mute_changed(self, mute):
        self.screens[mainScreenIndex].mute_changed(mute)
        self.updateType = BaseScreen.update_all

    def resize(self, event):
        self.init_manager(event.size)
        self.updateType = BaseScreen.update_all

    def tracklist_changed(self):
        self.screens[nowPlayingIndex].tracklist_changed()
        self.updateType = BaseScreen.update_all

    def options_changed(self):
        #pdb.set_trace()
        menuScreen = self.screens[MenuIndex]
        #pdb.set_trace()
        #self.screens[MenuIndex].options_changed()
        menuScreen.options_changed()
        self.updateType = BaseScreen.update_all

    def change_screen(self, new_screen):
        if new_screen > -1 and new_screen < len(self.screens):
            self.down_bar_objects.get_touch_object(
                "menu_" + str(self.currentScreen)).set_active(False)
            self.currentScreen = new_screen
            self.down_bar_objects.get_touch_object(
                "menu_" + str(new_screen)).set_active(True)
        self.updateType = BaseScreen.update_all

    def click_on_objects(self, objects, event):
        if objects is not None:
            for key in objects:
                if key[:-1] == "menu_":
                    self.change_screen(int(key[-1:]))
                    return True
        return False

    def nowPlaying(self):
        self.screens[nowPlayingIndex].nowPlaying_changed()
        self.updateType = BaseScreen.update_all

    def queue(self):
        self.screens[queueIndex].queue_changed()
        self.updateType = BaseScreen.update_all

    def playlists(self):
        self.screens[playlistsIndex].playlists_changed()
        self.updateType = BaseScreen.update_all

    def browse(self):
        self.screens[browseIndex].browse_changed()
        self.updateType = BaseScreen.update_all

    def stream(self):
        self.screens[streamsIndex].streams_changed()
        self.updateType = BaseScreen.update_all

    def stream_title_changed(self, title):
        self.screens[mainScreenIndex].stream_title_changed(title)
        self.updateType = BaseScreen.update_all

    def search(self, query, mode):
        self.screens[searchIndex].search(query, mode)
        self.updateType = BaseScreen.update_all

    def system(self):
        self.screens[SystemIndex].system_changed()
        self.updateType = BaseScreen.update_all

    def open_keyboard(self, input_listener):
        self.keyboard = Keyboard(self.size, self.baseSize, self,
                                 self.fonts, input_listener)
        self.updateType = BaseScreen.update_all

    def close_keyboard(self):
        self.keyboard = None
        self.updateType = BaseScreen.update_all
