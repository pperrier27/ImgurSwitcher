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

"""Module contains config information for imgurswitcher/global variables it uses.

The configuration values for the maximum buffer queue size, the queue operation timeout,
and the URL to the Imgur album to pull images from are all read from the file named in
CONFIG_FILE_NAME, which should be in the same directory as this module. If the file is not
found or an error occurs, the default values (hardcoded into this module) are used.
"""

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
event_queue = None

imgur_album_url = "http://imgur.com/gallery/wCBYO" # default album

# Is in this file because this is the "global" file, so every other file can access this.
class ImgurSwitcherException(Exception):
    """Simple general exception class to use if something goes wrong with this program."""
    def __init__(self, msg=None):
        self.message = msg

def verify_url(url):
    """Determines if url is valid; sets album_id and returns True if it is, returns False if it isn't.

    Specifically, "valid" in this case means "points to an actual Imgur album". The album_id variable is
    the unique album ID value from the URL, which is used to fetch the images from it later. It is set here
    because this function should be called before doing any work with imgur_album_url (since this is what makes sure
    it's actually valid), so we only have to run the regular expression on the URL once. If this function returns False,
    the caller should immediately do some error handling (probably exit the program).
    """
    match = re.match("(https?)\:\/\/(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", imgur_album_url)
    global album_id
    if match:
        album_id = match.group(4) # the piece that is the album's unique ID
        return True
    else:
        album_id = "" # Don't bother setting this to anything useful because the program should be about to fail out
        return False

def parse_cfg_file():
    """Parses the config file and sets configuration variables.

    Specifically, this function parses the file named in CONFIG_FILE_NAME and
    sets max_queue_size, queue_op_timeout, and imgur_album_url based on the matching values in
    the configuration file. If errors occur (e.g. there is no configuration file, file I/O errors,
    a configuration value is not specified...) then default values are used.
    """
    with open(CONFIG_FILE_NAME, 'r') as cfg_file:
        lines = cfg_file.read()
        size_match = re.match("size:(?: )*(.*)", lines)
        timeout_match = re.match("timeout:(?: )*(.*)", lines)
        url_match = re.match("url:(?: )*(.*)", lines)

        # Set the values; if anything fails then defaults will be used.
        if size_match:
            try:
                max_queue_size = int(size_match.group(1)) 
            except:
                pass

            global event_queue 
            event_queue = queue.PriorityQueue(max_queue_size) 
        
        if timeout_match:
            try:
                queue_op_timeout = int(timeout_match.group(1))
            except:
                pass

        if url_match:
            if verify_url(url_match.group(1)):
                imgur_album_url = url_match.group(1)
            elif not verify_url(imgur_album_url):
                # This checks the default URL, and also is needed so that the album_key variable is set properly.
                # If this is hit, then someone messed with the default value of imgur_album_url and broke it. Go fix it.
                raise ImgurSwitcherException("You changed the default value of imgur_album_url in config.py and broke the program,"
                    " because it is no longer a valid Imgur URL. Go fix it!")