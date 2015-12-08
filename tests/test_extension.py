#from __future__ import unicode_literals

import unittest

from mopidy_touchclient import Extension

#, frontend as frontend_lib


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        assert '[touchclient]' in config
        assert 'enabled = true' in config


    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        # Test the content of your config schema
        assert 'screen_width' in schema
        assert 'screen_height' in schema
