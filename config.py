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

# File contains config information for imgurswitcher/global variables it uses.
# TODO: Make a proper docstring/improve the wording of this comment.

import queue

# Arbitrary (constant) limit to the size of the event queue/timeout for events.
MAX_QUEUE_SIZE = 200
QUEUE_OP_TIMEOUT = 10  # seconds

# Queue priorities
LOW_PRIORITY = 10
MED_PRIORITY = 5
HIGH_PRIORITY = 1
URGENT_PRIORITY = 0 

# Ideally shouldn't be global, but will do for now. TODO: refactor?
# Queues up the callbacks that should be executed as the user pushes keys.
eventQueue = queue.PriorityQueue(MAX_QUEUE_SIZE) 

# OAuth2 tokens
OAUTH2_CLIENT_ID = "XXX"
OAUTH2_CLIENT_SECRET = "YYY"