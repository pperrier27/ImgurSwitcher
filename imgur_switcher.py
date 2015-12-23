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

# Import the common libraries
from threading import Thread
import config as cfg 
import imgur_callbacks as callbacks

_platform = cfg.platform

# Windows-specific imports
if _platform == "Windows":
    import pyHook as hook
    import pythoncom as com
    from os import _exit # fugly but it works to exit

elif _platform == "Darwin":
    pass

elif _platform == "Linux":
    pass

class Worker(Thread):
    """Class that does the invoking of the queued callbacks to avoid blocking the main thread."""

    def run(self):
        while True:
            fcn = event_queue.get()
            if fcn[1]:
                fcn[1]()  # the event queue contains tuples; the callback is the second item
                event_queue.task_done()
            else:
                # This means that the user wants to quit the program, since only quit should pass a None callback
                break
                
        exit_program()

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
            event_queue.put((cfg.HIGH_PRIORITY, None), False, cfg.queue_op_timeout) # None is reserved for quitting

        return False

    return True

def exit_program():
    """Does cleanup and exits the program in a platform-appropriate way."""
    
    # Common, every platform needs to call this
    cfg.on_quit()

    if _platform == "Windows":
        _exit(0) # TODO: refactor this to exit "properly", though this works since we have no cleanup left to do
                 # This would probably involve using ctypes and the win32api to get a WM_QUIT to the main thread,
                 # which is what PumpMessages quits on.

    elif _platform == "Darwin":
        pass
    
    elif _platform == "Linux":
        pass
    
    else:
        # Should NEVER get here: if platform was not determined we should have shut down
        # looooong before this.
        print("How did you even get here?")
        _exit(42)

# Common parts
event_queue = cfg.event_queue
workThread = Worker()
workThread.daemon = True
workThread.start()

# Windows-specific
if _platform == "Windows": 
    hookManager = hook.HookManager()
    hookManager.KeyDown = on_keyboard_event
    hookManager.HookKeyboard()
    com.PumpMessages()

# OSX-specific
elif _platform == "Darwin":
    pass

# Linux-specific
elif _platform == "Linux":
    pass

# Default to catch obscure error cases
else:
    # Should NEVER get here: if platform was not determined we should have shut down
    # looooong before this.
    print("How did you even get here?")