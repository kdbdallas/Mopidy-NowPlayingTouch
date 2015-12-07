import logging
import os
import traceback
from threading import Thread

from mopidy import core, exceptions

import pykka



logger = logging.getLogger(__name__)


class TouchClient(pykka.ThreadingActor, core.CoreListener):
    def __init__(self, config, core):
        super(TouchClient, self).__init__()
        self.core = core