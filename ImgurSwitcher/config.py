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

"""Module that controls the configuration of the program (platform-specific and otherwise.)

This is, in a way, the application of the template pattern to a whole program. The basic functionality of the program
is the same on all platforms, the only thing that changes is some of the specifics (like how to set an image as the background).
This function uses this module's knowledge of the platform to set up these specifics. The other modules can then call config.<function>
whenever they need to do something platform-specific.
"""

import re
import platform
import logging
import ImgurSwitcher.event_queue as eq
import ImgurSwitcher.exceptions as xcpt

# Name of the config file. Expected to be in the same directory as this module
CONFIG_FILE_NAME = "ImgurSwitcher/config.cfg"

# Name of the log file. Will be created in the same directory as this script.
LOG_FILE_NAME = "imgur_switcher_log.txt"

imgur_album_url = "http://imgur.com/gallery/wCBYO" # default album
album_pos = 0 # default position in album (1-indexed). This is the image we are currently on. 
              # 0 means no image (i.e. it's kind of like None)

_platform = None
# Platform-specific callback variables that other modules in the package need to use.
# Set in _set_platform_config so that MUST be called before using these.
Main = None
set_as_background = None
exit_program = None

# The platforms that are currently supported.
_supported_platforms = ["Windows"]

def _get_platform():
    """Determine the platform we're running on and return it.

    Returns the platform string if the platform can be
    found and is supported, otherwise throws an ImgurSwitcherException.
    Not intended to be called from outside this module."""
    global _platform
    _platform = platform.system()
    if not _platform:
        raise xcpt.ImgurSwitcherException("Can't figure out what platform this is running on, somehow. Cannot run program.")

    elif _platform not in _supported_platforms:
        raise xcpt.ImgurSwitcherException("Sorry, ImgurSwitcher currently does not support your platform (" + _platform + "). Feel free to implement support for it!")

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
        global imgur_album_url

        # Set the values; if anything fails then defaults will be used.
        if size_match:
            eq.set_max_queue_size(int(size_match.group(1)))
        else:
            print("FAIL QUEUE")
        
        if timeout_match:
            eq.set_queue_timeout(int(timeout_match.group(1)))
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

def set_platform_config():
    """Function that sets up the (platform-dependent) configuration/variables that the other modules in this package rely on.

    platform: the platform string to set the configuration for. This is expected to be one of the strings from _supported_platforms.

    Call this function after having initialized the event queue, but before running the platform main.
    """

    global Main
    global set_as_background
    global exit_program

    if _platform == "Windows":
        import ImgurSwitcher.windows as current_platform
    # Add other supported platform configurations here.
    
    Main = current_platform.main
    set_as_background = current_platform.set_as_background
    exit_program = current_platform.exit_program


def _init():
    """Function that gets the platform and reads the config file.

    Does NOT set the platform config, because that would cause a circular reference whenever
    the platform-specific modules get imported (they import config.py).
    """

    platform = _get_platform() # don't try/except this because we WANT to fail if this throws
    parse_cfg_file()

_init() # do initialization and setup on first import