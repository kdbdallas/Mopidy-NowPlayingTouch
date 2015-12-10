# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

# TODO: Remove entirely if you don't register GStreamer elements below
#import pygst
#pygst.require('0.10')
#import gst
#import gobject

from mopidy import config, ext
from .touchClientFrontend import TouchClient

__version__ = '0.1.0'


class Extension(ext.Extension):

    dist_name = 'Mopidy-TouchClient'
    ext_name = 'touchclient'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['screen_width'] = config.Integer(minimum=1)
        schema['screen_height'] = config.Integer(minimum=1)
        schema['cursor'] = config.Boolean
        schema['cache_dir'] = config.String
        schema['gpio'] = config.Boolean
        schema['gpio_left'] = config.Integer(minimum=1)
        schema['gpio_right'] = config.Integer(minimum=1)
        schema['gpio_up'] = config.Integer(minimum=1)
        schema['gpio_down'] = config.Integer(minimum=1)
        schema['gpio_enter'] = config.Integer(minimum=1)
        schema['sdl_fbdev'] = config.String
        schema['sdl_mousdrv'] = config.String
        schema['sdl_mousedev'] = config.String
        schema['sdl_audiodriver'] = config.String
        schema['sdl_path_dsp'] = config.String

        return schema

    def setup(self, registry):
        # Register a frontend
        registry.add('frontend', TouchClient)
