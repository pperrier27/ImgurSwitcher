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

block_input = False # Used to block adding to the event queue in certain situations.

logger = logging.getLogger(__name__)

def block():
    """Used to block input to the event queue and execution of things in it."""
    global block_input
    block_input = True

def unblock():
    """Used to unblock input to the event queue/resume execution of things in it."""
    global block_input
    block_input = False

def is_blocked():
    """Returns whether or not the event queue is blocked."""
    return block_input


def set_queue_timeout(timeout):
    global queue_op_timeout
    queue_op_timeout = timeout
    logger.debug("Event queue operation timeout set to %i", queue_op_timeout)

def set_max_queue_size(size):
    global max_queue_size
    max_queue_size = size
    logger.debug("Event queue size set to %i", max_queue_size)

def init():
    """Initializes the event queue."""
    global event_queue
    event_queue = queue.PriorityQueue(max_queue_size)
    logger.info("Event queue initialized with size %i", max_queue_size)

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

event_queue = None