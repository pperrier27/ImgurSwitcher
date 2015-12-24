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

"""Module contains config/platform information for imgurswitcher/global variables it uses/
assorted config-related functionality.

The configuration values for the maximum buffer queue size, the queue operation timeout,
and the URL to the Imgur album to pull images from are all read from the file named in
CONFIG_FILE_NAME, which should be in the same directory as this module. If the file is not
found or an error occurs, the default values (hardcoded into this module) are used.

"""

import queue
import re
import platform as _platform
import logging

# Name of the config file. Expected to be in the same directory as this script
CONFIG_FILE_NAME = "config.cfg"

# Name of the log file. Will be created in the same directory as this script.
LOG_FILE_NAME = "imgur_switcher_log.txt"
# Arbitrary (constant) limit to the size of the event queue/timeout for events.
max_queue_size = 200
queue_op_timeout = 10  # seconds

# Ideally shouldn't be global, but will do for now. TODO: refactor?
# Queues up the callbacks that should be executed as the user pushes keys.
# Set in parse_cfg_file, so that MUST be called before using this variable.
event_queue = None
imgur_album_url = "http://imgur.com/gallery/wCBYO" # default album
album_pos = 0 # default position in album (1-indexed). This is the image we are currently on. 
              # 0 means no image (i.e. it's kind of like None)

# Queue priorities
LOW_PRIORITY = 10
MED_PRIORITY = 5
HIGH_PRIORITY = 1
URGENT_PRIORITY = 0 


# Is in this module because this is the "global" file, so every other file can access this.
# If this project ever gets more varied custom exceptions, move to a separate exceptions.py module.
class ImgurSwitcherException(Exception):
    """Simple general exception class to use if something goes wrong with this program."""
    def __init__(self, msg=None):
        self.message = msg


# The platforms that are currently supported.
_supported_platforms = ["Windows"]

def _get_platform():
    """Determine the platform we're running on.

    Sets the platform global to the platform string if the platform can be
    found and is supported, otherwise throws an ImgurSwitcherException.
    Not intended to be called from outside this module."""
    global platform
    platform = _platform.system()
    if not platform:
        raise ImgurSwitcherException("Can't figure out what platform this is running on, somehow. Cannot run program.")

    elif platform not in _supported_platforms:
        raise ImgurSwitcherException("Sorry, ImgurSwitcher currently does not support your platform (" + platform + "). Feel free to implement support for it!")

def verify_url(url):
    """Determines if url is valid; sets album_id and returns True if it is, returns False if it isn't.

    Specifically, "valid" in this case means "points to an actual Imgur album". The album_id variable is
    the unique album ID value from the URL, which is used to fetch the images from it later. It is set here
    because this function should be called before doing any work with imgur_album_url (since this is what makes sure
    it's actually valid), so we only have to run the regular expression on the URL once. If this function returns False,
    the caller should immediately do some error handling (probably exit the program).
    """
    match = re.search("(https?)\:\/\/(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", imgur_album_url)
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
        size_match = re.search("size:(?: )*?([0-9]+)", lines)
        timeout_match = re.search("timeout:(?: )*?([0-9]+)", lines)
        url_match = re.search("url:(?: )*?([a-zA-Z0-9:/\.]+)", lines)
        album_pos_match = re.search("position:(?: )*?([0-9]+)", lines)

        # Work with the global config vars
        global album_pos
        global max_queue_size
        global imgur_album_url
        global queue_op_timeout
        global event_queue

        # Set the values; if anything fails then defaults will be used.
        if size_match:
            max_queue_size = int(size_match.group(1)) 
        else:
            print("FAIL QUEUE")
        
        event_queue = queue.PriorityQueue(max_queue_size)

        if timeout_match:
            queue_op_timeout = int(timeout_match.group(1))
        else:
            print("FAIL TIMEOUT")

        if album_pos_match:
            album_pos = int(album_pos_match.group(1)) 
            if album_pos < 0: 
                album_pos = 0
                # The case where album_pos is larger than the number of images in the album is handled in the callbacks.
        else:
            print("FAIL POS")

        if url_match:
            if verify_url(url_match.group(1)):
                imgur_album_url = url_match.group(1)
            elif not verify_url(imgur_album_url):
                # This checks the default URL, and also is needed so that the album_key variable is set properly.
                # If this is hit, then someone messed with the default value of imgur_album_url and broke it. Go fix it.
                raise ImgurSwitcherException("You changed the default value of imgur_album_url in config.py and broke the program,"
                    " because it is no longer a valid Imgur URL. Go fix it!")
        else:
            print("FAIL URL")

def on_quit():
    """Function to call just before quitting. Writes album_pos and imgur_album_url to the config file for the next run."""

    with open(CONFIG_FILE_NAME, "r+") as cfg_file:
        lines = cfg_file.read()
        
        # delete the first previous occurrence of the position line and the url line, then clear the text from the
        # file and write in the new text

        result = re.subn("url:(?: )*?(.*)", "url: " + imgur_album_url, lines, 1) # at most one replacement
        if result[1] == 1:
            lines = result[0]

        else:
            lines = "url: " + imgur_album_url + "\n" + lines

        result = re.subn("position:(?: )*?(.*)", "position: " + str(album_pos), lines, 1) # at most one replacement
        if result[1] == 1:
            lines = result[0]

        else:
            lines += "\nposition: " + str(album_pos)

        # Clear text from the file and reset the stream pointer to the beginning of the file
        cfg_file.seek(0)
        cfg_file.truncate()
        cfg_file.write(lines)


def init():
    """Function that initializes the config settings."""

    _get_platform() # don't try/except this because we WANT to fail if this throws
    parse_cfg_file()

init() # do initialization on first import