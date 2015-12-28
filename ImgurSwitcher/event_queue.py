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

# Queue priorities
LOW_PRIORITY = 10
MED_PRIORITY = 5
HIGH_PRIORITY = 1
URGENT_PRIORITY = 0 

# Arbitrary (constant) limit to the size of the event queue/timeout for events.
max_queue_size = 200
queue_op_timeout = 10  # seconds

def set_queue_timeout(timeout):
    global queue_op_timeout
    queue_op_timeout = timeout

def set_max_queue_size(size):
    global max_queue_size
    max_queue_size = size

def init():
    """Initializes the event queue."""
    global event_queue
    event_queue = queue.PriorityQueue(max_queue_size)

event_queue = None