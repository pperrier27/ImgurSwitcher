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
import re

# Name of the config file. Expected to be in the same directory as this script
CONFIG_FILE_NAME = "config.cfg"

# Arbitrary (constant) limit to the size of the event queue/timeout for events.
max_queue_size = 200
queue_op_timeout = 10  # seconds

# Queue priorities
LOW_PRIORITY = 10
MED_PRIORITY = 5
HIGH_PRIORITY = 1
URGENT_PRIORITY = 0 

# Ideally shouldn't be global, but will do for now. TODO: refactor?
# Queues up the callbacks that should be executed as the user pushes keys.
# Set in parse_cfg_file, so that MUST be called before using this variable.
eventQueue = None

imgur_album_url = "http://imgur.com/gallery/wCBYO" # default album

def verify_url(url):
    """ Makes sure that the passed in URL actually valid
        (i.e. it points to imgur). Returns True if the URL is valid, False otherwise.
    """
    return re.match("(https?)\:\/\/(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", imgur_album_url) != None

def parse_cfg_file():
    """ Parses the config file and sets the values of
        MAX_QUEUE_SIZE, QUEUE_OP_TIMEOUT, and IMGUR_ALBUM_URL
        based on its contents (or leaves the default if not valid/errors occur)
    """
    with open(CONFIG_FILE_NAME, 'r') as cfgFile:
        lines = cfgFile.read()
        sizeMatch = re.match("size:(?: )*(.*)", lines)
        timeoutMatch = re.match("timeout:(?: )*(.*)", lines)
        urlMatch = re.match("url:(?: )*(.*)", lines)

        # Set the values; if anything fails then defaults will be used.
        if sizeMatch:
            try:
                max_queue_size = int(sizeMatch.group(1)) 
            except:
                pass

            global eventQueue 
            eventQueue = queue.PriorityQueue(max_queue_size) 
        
        if timeoutMatch:
            try:
                queue_op_timeout = int(timeoutMatch.group(1))
            except:
                pass

        if urlMatch:
            if verify_url(urlMatch.group(1)):
                imgur_album_url = urlMatch.group(1)
