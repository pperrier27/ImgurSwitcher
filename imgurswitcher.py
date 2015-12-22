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


# Don't let people import this
if __name__ != "__main__":
    print("Importing this module (imgurswitcher) is not allowed.")
    quit()

from threading import Thread
import pyHook as Hook
import pythoncom as Com
import config as cfg
from imgur_callbacks import ImgurCallbacks

eventQueue = cfg.eventQueue

class Worker(Thread):
    """ Class that does the invoking of the queued callbacks
        to avoid blocking the main thread
    """

    def run(self):
        while True:
            fcn = eventQueue.get()
            fcn[1]()  # the event queue contains tuples; the callback is the second item
            eventQueue.task_done()

def on_keyboard_event(event):
    """ TODO: Make a better docstring, including what different key combos should do
    """

    if(event.IsAlt()):
        keyPressed = event.GetKey()
        if(keyPressed == "D"):
            eventQueue.put((cfg.LOW_PRIORITY, ImgurCallbacks.next_image), False, cfg.QUEUE_OP_TIMEOUT)
        elif(keyPressed == "A"):
            eventQueue.put((cfg.LOW_PRIORITY, ImgurCallbacks.prev_image), False, cfg.QUEUE_OP_TIMEOUT)
        elif(keyPressed == "S"):
            eventQueue.put((cfg.HIGH_PRIORITY, ImgurCallbacks.save_image), False, cfg.QUEUE_OP_TIMEOUT)
        elif(keyPressed == "U"):
            eventQueue.put((cfg.HIGH_PRIORITY, ImgurCallbacks.change_url), False, cfg.QUEUE_OP_TIMEOUT)
        elif(keyPressed == "Q"):
            eventQueue.put((cfg.HIGH_PRIORITY, ImgurCallbacks.quit), False, cfg.QUEUE_OP_TIMEOUT)

        return False

    return True


workThread = Worker()
workThread.daemon = True # allow exit to work properly and terminate everything
workThread.start()
hookManager = Hook.HookManager()
hookManager.KeyDown = on_keyboard_event
hookManager.HookKeyboard()
Com.PumpMessages()