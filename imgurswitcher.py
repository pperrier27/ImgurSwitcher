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

import pyHook as Hook
import pythoncom as Com
import threading
import queue
import imgur_callbacks as callbacks

# Arbitrary (constant) limit to the size of the event queue/timeout for events.
MAX_QUEUE_SIZE = 200
QUEUE_OP_TIMEOUT = 10  # seconds

# Queue priorities
LOW_PRIORITY = 10
MED_PRIORITY = 5
HIGH_PRIORITY = 1

# Ideally shouldn't be global, but will do for now. TODO: refactor?
# Queues up the callbacks that should be executed as the user pushes keys.
eventQueue = queue.PriorityQueue(MAX_QUEUE_SIZE) 




def on_keyboard_event(event):
    """ TODO: Make a better docstring
    """
    # For ease of testing, remove later
    if event.GetKey() == "Q":
    	quit()

    if(event.IsAlt()):
        keyPressed = event.GetKey()
        if(keyPressed == "D"):
            eventQueue.put((LOW_PRIORITY, callbacks.next_image_callback), False, QUEUE_OP_TIMEOUT)
        elif(keyPressed == "A"):
            eventQueue.put(LOW_PRIORITY, callbacks.prev_image_callback, False, QUEUE_OP_TIMEOUT)
        elif(keyPressed == "S"):
            eventQueue.put((HIGH_PRIORITY, callbacks.save_image_callback), False, QUEUE_OP_TIMEOUT)


        return False

    return True



hookManager = Hook.HookManager()
hookManager.KeyDown = on_keyboard_event
hookManager.HookKeyboard()
Com.PumpMessages()