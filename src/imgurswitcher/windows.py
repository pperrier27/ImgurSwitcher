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
import pyHook as hook
import pythoncom as com
import win32api
import win32con
from . import event_queue as eq
from . import imgur_callbacks as callbacks

logger.debug("Successful import of all modules in Windows-specific module")

# Hold the main thread ID to allow for nice quitting
_main_thread_id = win32api.GetCurrentThreadId()
logger.debug("Current main thread id is %i", _main_thread_id)

def set_as_background(url):
    logger.debug("Attempting to set Windows background...")
    SPI_SETDESKWALLPAPER = 20 
    return ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, url, 3)


def exit_program():
    logger.info("Exiting program (Windows)...")
    win32api.PostThreadMessage(_main_thread_id, win32con.WM_QUIT, 0, 0)

def on_keyboard_event(event):
    """ Callback that is called whenever a key on the keyboard is hit.

    Only certain key combinations actually matter to this program, and they are listed below:

    ALT+D: Get the next image in the album and set it as the background picture.
    ALT+A: Get the previous image in the album and set it as the background picture.
    ALT+R: Get a random image in the album and set it as the background picture.
    ALT+S: Save the current image to the user's computer (i.e. copy it so it's not deleted when the image changes)
    ALT+U: Change the Imgur album that pictures are pulled from (by changing the URL in the config file).
    ALT+Q: Quit this program.
    """

    callback_dict = {
        # Format: 
        # Key: eq.TupleSortingOn0((priority in event queue, callback to call, block event queue until processed?))
        "D": eq.TupleSortingOn0((eq.LOW_PRIORITY, callbacks.ImgurCallbacks.next_image, False)),
        "A": eq.TupleSortingOn0((eq.LOW_PRIORITY, callbacks.ImgurCallbacks.prev_image, False)),
        "R": eq.TupleSortingOn0((eq.LOW_PRIORITY, callbacks.ImgurCallbacks.random_image, False)),
        "S": eq.TupleSortingOn0((eq.HIGH_PRIORITY, callbacks.ImgurCallbacks.save_image, True)),
        "U": eq.TupleSortingOn0((eq.HIGH_PRIORITY, callbacks.ImgurCallbacks.change_url, True)),
        "Q": eq.TupleSortingOn0((eq.HIGH_PRIORITY, callbacks.ImgurCallbacks.quit_program, True))
    }

    if(event.IsAlt()):
        keyPressed = event.GetKey()
        block = True # True lets the event through
        if keyPressed in callback_dict:
            eq.put(callback_dict[keyPressed])
            logger.debug("Loaded callback: " + callback_dict[keyPressed][1].__name__ + " into event queue")
            block = False
            
        return block

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
    logger.debug("Starting message pump...")
    hookManager.UnhookKeyboard()
    logger.debug("Message pumping ended, done Windows main")