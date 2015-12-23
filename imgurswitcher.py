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

"""Main ImgurSwitcher module.

Should not be imported from elsewhere (though there's no reason why you couldn't,
ImgurSwitcher simply doesn't require it so it's disabled.)
"""

# Don't let people import this
if __name__ != "__main__":
    print("Importing this module (imgurswitcher) is not allowed.")
    quit()

from threading import Thread
import pyHook as hook
import pythoncom as com
import config as cfg
import imgur_callbacks as callbacks # This conveniently calls cfg.parse_config_file() so we don't need to do it again here. TODO: refactor this to be not terrible.

class Worker(Thread):
    """Class that does the invoking of the queued callbacks to avoid blocking the main thread."""

    def run(self):
        while True:
            fcn = event_queue.get()
            fcn[1]()  # the event queue contains tuples; the callback is the second item
            event_queue.task_done()

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

    if(event.IsAlt()):
        keyPressed = event.GetKey()
        if(keyPressed == "D"):
            event_queue.put((cfg.LOW_PRIORITY, callbacks.ImgurCallbacks.next_image), False, cfg.queue_op_timeout)
        elif(keyPressed == "A"):
            event_queue.put((cfg.LOW_PRIORITY, callbacks.ImgurCallbacks.prev_image), False, cfg.queue_op_timeout)
        elif(keyPressed == "R"):
            event_queue.put((cfg.LOW_PRIORITY, callbacks.ImgurCallbacks.random_image), False, cfg.queue_op_timeout)
        elif(keyPressed == "S"):
            event_queue.put((cfg.HIGH_PRIORITY, callbacks.ImgurCallbacks.save_image), False, cfg.queue_op_timeout)
        elif(keyPressed == "U"):
            event_queue.put((cfg.HIGH_PRIORITY, callbacks.ImgurCallbacks.change_url), False, cfg.queue_op_timeout)
        elif(keyPressed == "Q"):
            event_queue.put((cfg.HIGH_PRIORITY, callbacks.ImgurCallbacks.quit), False, cfg.queue_op_timeout)

        return False

    return True


event_queue = cfg.event_queue
workThread = Worker()
workThread.daemon = True # allow exit to work properly and terminate everything
workThread.start()
hookManager = hook.HookManager()
hookManager.KeyDown = on_keyboard_event
hookManager.HookKeyboard()
com.PumpMessages()