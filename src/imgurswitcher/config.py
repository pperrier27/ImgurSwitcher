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
import imgurswitcher.event_queue as eq
import imgurswitcher.exceptions as xcpt
import imgurswitcher.dialogs as dialogs

logger = logging.getLogger(__name__)

# Name of the config file. Expected to be in the same directory as this module
CONFIG_FILE_NAME = "ImgurSwitcher/config.cfg"

imgur_album_url = "http://imgur.com/gallery/wCBYO" # default album
album_id = "wCBYO" # default album_id
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
        dialogs.error_dialog_box("Platform Not Found", "Can't figure out what platform this is running on, somehow. Cannot run program.")
        raise xcpt.ImgurSwitcherException("Can't figure out what platform this is running on, somehow. Cannot run program.")

    elif _platform not in _supported_platforms:
        dialogs.error_dialog_box("Platform Not Supported", "Sorry, ImgurSwitcher currently does not support your platform (" + _platform + ")." + 
                                "\n\nFeel free to implement support for it!")
        raise xcpt.ImgurSwitcherException("Sorry, ImgurSwitcher currently does not support your platform (" + _platform + "). Feel free to implement support for it!")

def verify_url(url):
    """Determines if url is valid; sets album_id and returns True if it is, returns False if it isn't.

    Specifically, "valid" in this case means "points to an actual Imgur album". The album_id variable is
    the unique album ID value from the URL, which is used to fetch the images from it later. It is set here
    because this function should be called before doing any work with imgur_album_url (since this is what makes sure
    it's actually valid), so we only have to run the regular expression on the URL once. If this function returns False,
    the caller should immediately do some error handling.
    """
    match = re.search("(https?)\:\/\/(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", url)
    global album_id
    if match:
        album_id = match.group(4) # the piece that is the album's unique ID
        logger.info("URL match successful. URL: %s, Album ID: %s", url, album_id)
        return True
    else:
        logger.warning("URL match unsuccessful. Attempted URL: %s", url)
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
            logger.info("Setting max queue size to %i from config file", eq.max_queue_size)
        else:
            logger.warning("Could not get queue size from config file; using default value of %i", eq.max_queue_size)
        
        if timeout_match:
            eq.set_queue_timeout(int(timeout_match.group(1)))
            logger.info("Setting queue operation timeout value to %i from config file", eq.queue_op_timeout)
        else:
            logger.warning("Could not get queue operation timeout value from config file; using default value of %i", eq.queue_op_timeout)

        if album_pos_match:
            album_pos = int(album_pos_match.group(1))
            logger.info("Setting album position to %i from config file", album_pos)
            if album_pos < 0:
                logger.info("Correcting album position to %i since config value file was negative", 0)
                album_pos = 0
                # The case where album_pos is larger than the number of images in the album is handled in the callbacks.
        else:
            logger.warning("Could not get album position from config file; using default value of %i", album_pos)

        url_valid = False
        if url_match:
            if verify_url(url_match.group(1)):
                imgur_album_url = url_match.group(1)
                url_valid = True
                logger.info("Setting Imgur album URL to %s from config file", imgur_album_url)
        else:
            logger.warning("Could not get imgur album URL from config file; trying default value of %i", imgur_album_url)

        # This checks the default URL if no match was found in the config file,
        # and also is needed so that the album_key variable is set properly in case of having 
        # to use the default.
        if not url_valid and not verify_url(imgur_album_url):
            # If this is hit, then someone messed with the default value of imgur_album_url and broke it. Go fix it.
            logger.critical("Default Imgur album URL is not valid! URL: %s Aborting...", imgur_album_url)
            dialogs.error_dialog_box("URL Not Valid", "Default Imgur album URL is not valid! URL: " + imgur_album_url + "\n\nAborting program...")
            raise ImgurSwitcherException("You changed the default value of imgur_album_url in config.py and broke the program,"
                " because it is no longer a valid Imgur URL. Go fix it!")

def write_config_to_file():
    """Writes album_pos and imgur_album_url to the config file.

    Call this immediately before quitting to save state for the next run, or after changing
    the values of imgur_album_url and/or album_pos to force the changes to take hold.
    """

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

        logger.info("Wrote configuration info to file. URL: %s, album position: %i", imgur_album_url, album_pos)

def set_platform_config():
    """Function that sets up the (platform-dependent) configuration/variables that the other modules in this package rely on.

    platform: the platform string to set the configuration for. This is expected to be one of the strings from _supported_platforms.

    Call this function after having initialized the event queue, but before running the platform main.
    """

    global Main
    global set_as_background
    global exit_program

    if _platform == "Windows":
        logger.info("Current platform is Windows")
        import imgurswitcher.windows as current_platform
    # Add other supported platform configurations here.
    
    Main = current_platform.main
    set_as_background = current_platform.set_as_background
    exit_program = current_platform.exit_program
    logger.info("Platform-specific callbacks were set")

def _init():
    """Function that gets the platform and reads the config file.

    Does NOT set the platform config, because that would cause a circular reference whenever
    the platform-specific modules get imported (they import config.py). Call that in __init__.py.
    """
    logger.info("Initializing configuration settings")
    platform = _get_platform() # don't try/except this because we WANT to fail if this throws
    parse_cfg_file()
    logger.info("Configuration settings initialized")

_init() # do initialization and setup on first import