# Copyright Patrick Perrier, 2015

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Module contains Windows-specific functionality.

Specifically, module contains the Windows-specific functions for setting
an image as the desktop background, showing dialog boxes (e.g. to select where to
save images or to warn the user), and hooking into keyboard presses.
"""

import logging
logger = logging.getLogger(__name__)

import ctypes
from os import _exit # fugly but it works to exit
import pyHook as hook
import pythoncom as com
from . import event_queue as eq
from . import imgur_callbacks as callbacks

logger.debug("Successful import of all modules in Windows-specific module")

def set_as_background(url):
    logger.debug("Attempting to set Windows background...")
    SPI_SETDESKWALLPAPER = 20 
    return ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, url, 3)


def exit_program():
    logger.info("Exiting program (Windows)...")
    _exit(0)

def on_keyboard_event(event):
    """ Callback that is called whenever a key on the keyboard is hit.

    Only certain key combinations actually matter to this program, and they are listed below:

    ALT+D: Get the next image in the album and set it as the background picture.
    ALT+A: Get the previous image in the album and set it as the background picture.
    ALT+R: Get a random image in the album and set it as the background picture.
    ALT+S: Save the current image to the user's computer (i.e. copy it so it's not deleted when the image changes)
    ALT+U: Change the Imgur album that pictures are pulled from (by changing the URL in the config file).
    ALT+Q: Quit this program.

    Note that a None value is currently reserved as the "quit callback".
    """
    if(event.IsAlt() and not eq.is_blocked()):
        keyPressed = event.GetKey()
        if(keyPressed == "D"):
            eq.event_queue.put((eq.LOW_PRIORITY, callbacks.ImgurCallbacks.next_image), False, eq.queue_op_timeout)
            logger.debug("Loaded callback: " + callbacks.ImgurCallbacks.next_image.__name__ + " into event queue")
        elif(keyPressed == "A"):
            eq.event_queue.put((eq.LOW_PRIORITY, callbacks.ImgurCallbacks.prev_image), False, eq.queue_op_timeout)
            logger.debug("Loaded callback: " + callbacks.ImgurCallbacks.prev_image.__name__ + " into event queue")
        elif(keyPressed == "R"):
            eq.event_queue.put((eq.LOW_PRIORITY, callbacks.ImgurCallbacks.random_image), False, eq.queue_op_timeout)
            logger.debug("Loaded callback: " + callbacks.ImgurCallbacks.random_image.__name__ + " into event queue")
        elif(keyPressed == "S"):
            eq.event_queue.put((eq.HIGH_PRIORITY, callbacks.ImgurCallbacks.save_image), False, eq.queue_op_timeout)
            logger.debug("Loaded callback: " + callbacks.ImgurCallbacks.save_image.__name__ + " into event queue")
        elif(keyPressed == "U"):
            eq.event_queue.put((eq.HIGH_PRIORITY, callbacks.ImgurCallbacks.change_url), False, eq.queue_op_timeout)
            logger.debug("Loaded callback: " + callbacks.ImgurCallbacks.change_url.__name__ + " into event queue")
        elif(keyPressed == "Q"):
            eq.event_queue.put((eq.HIGH_PRIORITY, None), False, eq.queue_op_timeout) # None is reserved for quitting
            logger.debug("Loaded quit command into event queue")
        return False

    return True

def main():
    """Windows-specific main function.

    Hooks into the message pipe to look for keyboard events.
    """

    logger.info("Starting Windows main...")
    hookManager = hook.HookManager()
    hookManager.KeyDown = on_keyboard_event
    hookManager.HookKeyboard()
    com.PumpMessages()