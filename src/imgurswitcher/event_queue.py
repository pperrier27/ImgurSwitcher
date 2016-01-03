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

"""Event queue module.

This module holds the logic for ImgurSwitcher's event queue (that processes the invoked
callbacks). Import as many times as you like, but DON'T TOUCH _event_queue DIRECTLY: use the
module's put and get_and_exec methods instead (go read them for further info). This allows
for proper event blocking management and proper argument validation, since the queue expects a 
specific input format.
"""

import queue
import logging

# Queue priorities
LOW_PRIORITY = 10
MED_PRIORITY = 5
HIGH_PRIORITY = 1
URGENT_PRIORITY = 0 

# Arbitrary (constant) limit to the size of the event queue/timeout for events.
max_queue_size = 200
queue_op_timeout = 10  # seconds

_event_queue = None
_blocked = False # Used to block adding to the event queue in certain situations.
_reset_flag = False

logger = logging.getLogger(__name__)

def set_queue_timeout(timeout):
    global queue_op_timeout
    queue_op_timeout = timeout
    logger.debug("Event queue operation timeout set to %i", queue_op_timeout)

def set_max_queue_size(size):
    global max_queue_size
    max_queue_size = size
    logger.debug("Event queue size set to %i", max_queue_size)

def put(trip: tuple):
    """Puts a triple trip of types (priority, callable, bool) in the queue, only if the queue is not blocked.

    trip: a triple with an integer as the first item, a callable object as the second (e.g. a function), and a bool as the third:
    (int, callable, bool).

    Internally, this adds the triple trip to the queue if _blocked is False.
    If triple[2] is True, then _blocked is set to True so that no more items can be added until get_and_exec
    unblocks the queue.
    """
    global _blocked, _event_queue
    if not _blocked:
        try:
            _event_queue.put(trip, False, queue_op_timeout)
        except queue.Full:
            logger.error("Insertion of (%i, %s, %s) into event queue failed: queue full!", trip[0], trip[1], trip[2])
            return

        if not _blocked and trip[2]:
            _blocked = True
            logger.debug("Input queue blocked ")
    else:
        logger.debug("Blocking insertion of (%i, %s, %s) into event queue", trip[0], trip[1], trip[2])

def get_and_exec():
    """Gets the next item from the queue and calls the callable.

    Internally, this function gets the next triple from the event queue 
    (which should have been added using this module's put function) and calls the
    callable. It also unblocks the queue (allows it to receive further input) if
    recovered_triple[2] is True.

    Also calls _reset if the _reset_flag was set by an operation, since this should be 
    done when the execution of that operation is complete.
    """


    global _blocked, _event_queue
    triple = _event_queue.get()
    logger.debug("Executing callback: %s", triple[1].__name__)
    triple[1]()
    _event_queue.task_done()
    logger.debug("Done executing callback: %s", triple[1].__name__)
    
    # See if we need to reset the queue. If yes then reset and return
    if _reset_flag:
        # Block queue temporarily to prevent more items being loaded
        # while we're trying to change things
        _blocked = True
        _reset()
        _blocked = False
        return

    # If triple[2] is true then this means that this item has blocked the queue,
    # so unblock it
    if _blocked and triple[2]:
        _blocked = False 

def init():
    """Initializes the event queue."""
    global _event_queue
    _event_queue = queue.PriorityQueue(max_queue_size)
    logger.info("Event queue initialized with size %i", max_queue_size)

def reset():
    """Resets the value of the event queue.

    Works by setting a flag that the event queue needs to be reset
    at the end of the operation currently being processed. Done this way
    because replacing the event queue in the middle of an operation causes
    errors with task_done()."""
    global _reset_flag
    _reset_flag = True
    logger.info("Event queue reset triggered. Will be executed after current item is processed")

def _reset():
    """Actually does the resetting of the event queue. Internal use only."""

    global _reset_flag
    if _reset_flag:
        global _event_queue
        _event_queue = queue.PriorityQueue(max_queue_size)
        logger.info("Event queue reset with size %i", max_queue_size)
        _reset_flag = False

# Need this because the priority queue sometimes
# throws exceptions when we try and compare two tuples
# that have the same first value (because it then tries to compare
# two functions and fails). Use this as a decorator class to fix this
# problem.
class TupleSortingOn0(tuple):
    def __lt__(self, rhs):
        return self[0] < rhs[0]
    def __gt__(self, rhs):
        return self[0] > rhs[0]
    def __le__(self, rhs):
        return self[0] <= rhs[0]
    def __ge__(self, rhs):
        return self[0] >= rhs[0]