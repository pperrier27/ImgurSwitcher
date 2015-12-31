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


"""Module contains methods used for callbacks.

The callbacks themselves apply across all platforms, but the implementation
specifics may vary. For implementation-specific functionality, put a function in 
the appropriate platform-specific module in this package and then update config.py to
expose the function/set its implementation (see existing code for examples).
"""

import re
import os
import random
import shutil
import logging
import urllib.request, urllib.parse, urllib.error
from . import config as cfg
from . import dialogs as dialogs
from . import get_data

logger = logging.getLogger(__name__)

def _initialize_images():
    """Initializes ImgurCallbacks' image ID list from the URL given in the config module.

    Should not be called from outside ImgurCallbacks.
    This function will also cause the program to terminate if the config URL is not valid,
    or if an error occurs.
    """
    
    # This should always be True because cfg.parse_cfg_file should always be called before this is,
    # but here for redundancy anyway.
    if cfg.verify_url(cfg.imgur_album_url):
        # Read the image ID's into a list and return them.
        # Parts of this code modified from https://github.com/alexgisby/imgur-album-downloader
        
        fullListURL = "http://imgur.com/a/" + cfg.album_id + "/layout/blog" # the scriptless version of the album page

        logger.info("Initializing image ID list to point to %s" % fullListURL)

        response = None
        response_code = None
        try:
            logger.debug("Attempting to download image list...")
            response = urllib.request.urlopen(url=fullListURL)
            response_code = response.getcode()
        except Exception as e:
            response = False
            response_code = e.code
        
        if not response or response.getcode() != 200:
            # It COULD be a single-picture gallery, which doesn't play nicely with being turned into an album (404 error).
            # Try a straight download of the one picture if we get a 404, see if that works.
            if response_code == 404:
                logger.info("404 code, trying single image download from URL %s...", r"http://i.imgur.com/" + cfg.album_id)
                fullListURL = r"http://i.imgur.com/" + cfg.album_id # hardcode imgur stub in because we have to 
                try:
                    response = urllib.request.urlopen(url=fullListURL)
                    response_code = response.getcode()
                except Exception as e:
                    response = False
                    response_code = e.code
                if not response or response.getcode() != 200:
                    logger.critical("Error reading Imgur: Error Code %d. Aborting program..." % response_code)
                    dialogs.error_dialog_box("Error reading Imgur: Error Code %d.\n\nImgurSwitcher will shut down." % response_code)
                    raise cfg.ImgurSwitcherException("Error reading Imgur: Error Code %d" % response_code)
            else:
                logger.critical("Error reading Imgur: Error Code %d. Aborting program..." % response_code)
                dialogs.error_dialog_box("Error reading Imgur: Error Code %d.\n\nImgurSwitcher will shut down." % response_code)
                raise cfg.ImgurSwitcherException("Error reading Imgur: Error Code %d" % response_code)

        html = response.read().decode('utf-8')
        logger.info("Image list download successful. Image list initialized")
        return re.findall('<div id="([a-zA-Z0-9]+)" class="post-image-container', html) # found by inspecting the source of an imgur album page

    else:
        logger.critical("The provided URL is not a valid Imgur URL! Aborting program...")
        dialogs.error_dialog_box("The provided URL is not a valid Imgur URL!\n\nImgurSwitcher will shut down.")
        raise cfg.ImgurSwitcherException("The provided URL is not a valid Imgur URL!")

def _download_image(url):
    """Helper that downloads images.

    url: the url to download the image from.

    Returns the path to the downloaded image, or None
    if the download was not successful.
    """
    logger.info("Downloading image from URL: %s", url)
    try:
        path_to_image, junk2 = urllib.request.urlretrieve(url, ImgurCallbacks._img_path) # clobbers the old image
        return os.path.abspath(path_to_image) # We know where the images will be already, more of a sentinel "this worked"
    except Exception as e:
        logger.error("Download from URL: %s failed! Reason: %s", url, e)    
        dialogs.error_dialog_box(title="Download Error" , message="Image download failed!")    
        return None

class ImgurCallbacks:
    """Holds the callbacks and information they require."""

    _image_ids = _initialize_images()
    imgur_stub = r"http://i.imgur.com/"
    # Windows needs absolute paths or it fails to set background properly (gives a black screen)
    _img_path = get_data("background.jpg")
    _DEFAULT_IMAGE = get_data("default.jpg")

    @staticmethod
    def next_image():
        """Callback to use to fetch the next image in the album and set it as the background."""
        # cfg.album_pos is 1-indexed, so it is the index we need (no need for modification)
        index = (cfg.album_pos) % len(ImgurCallbacks._image_ids)
        logger.debug("Index is %i", index)

        # Need arbitrary image type extension to get to the page with just the image.
        # We'll assume that the file is a jpg, because it probably is according to 
        # my interpretation of https://help.imgur.com/hc/en-us/articles/201424906-What-file-types-are-allowed
        # Alternatively, future development could read the magic bytes of the image and figure out
        # what image type it was.
        image_url = ImgurCallbacks.imgur_stub + ImgurCallbacks._image_ids[index] + ".jpg" 
        result = _download_image(image_url)
        
        if result is not None:
            if cfg.set_as_background(ImgurCallbacks._img_path):
                logger.debug("Successfully set background")
                cfg.album_pos = index + 1
                logger.debug("New index is %i", cfg.album_pos)
            
            else:
                logger.warning("Setting background failed, trying the default image...")
                # Delete current image file and try the default
                try:
                    os.remove(ImgurCallbacks._img_path)
                except Exception as e:
                    # Doesn't matter, just don't kill the program
                    pass 
                if cfg.set_as_background(ImgurCallbacks._DEFAULT_IMAGE):
                    logger.warning("Successfully set default background")
                else:
                    logger.critical("Something went terribly wrong...")
                    dialogs.error_dialog_box(title="Critical Failure" , message="Something went terribly wrong...")
            
    @staticmethod
    def prev_image():
        """Callback to use to fetch the previous image in the album and set it as the background."""
        # cfg.album_pos is 1-indexed, so cfg.album_pos is the index number for the NEXT image,
        # cfg.album_pos -1 is the index of the current image, and cfg.album_pos - 2 is the 
        # index of the previous image (the one we want). This one will take a bit more special case handling

        # Slight "bug" if the starting cfg.album_pos value is one more than some integer multiple
        # of the album size; calling this will then get you the same image that you currently have.
        # This is what it SHOULD do, but maybe something should be done about it?
        index = -1
        if cfg.album_pos != 0 and len(ImgurCallbacks._image_ids) != 1:
            index = (cfg.album_pos % len(ImgurCallbacks._image_ids))-2
        logger.debug("Index is %i", index)

        # Need arbitrary image type extension to get to the page with just a picture.
        # We'll assume that the file is a jpg, because it probably is according to 
        # my interpretation of https://help.imgur.com/hc/en-us/articles/201424906-What-file-types-are-allowed
        # Alternatively, future development could read the magic bytes of the image and figure out
        # what image type it was.
        image_url = ImgurCallbacks.imgur_stub + ImgurCallbacks._image_ids[index] + ".jpg" 
        result = _download_image(image_url)
        
        if result is not None:
            if cfg.set_as_background(ImgurCallbacks._img_path):
                logger.debug("Successfully set background")
                cfg.album_pos = (index % len(ImgurCallbacks._image_ids)) + 1 # yay for the python modulus behaviour!
                logger.debug("New index is %i", cfg.album_pos)
            else:
                logger.warning("Setting background failed, trying the default image...")
                # Delete current image file and try the default
                try:
                    os.remove(ImgurCallbacks._img_path)
                except Exception as e:
                    # Doesn't matter, just don't kill the program
                    pass 

                if cfg.set_as_background(ImgurCallbacks._DEFAULT_IMAGE):
                    logger.warning("Successfully set default background")
                else:
                    logger.critical("Something went terribly wrong...")
                    dialogs.error_dialog_box(title="Critical Failure" , message="Something went terribly wrong...")

    @staticmethod
    def random_image():
        """Callback to fetch a random image in the album and set it as the background."""
                
        index = random.randint(0, len(ImgurCallbacks._image_ids)-1)
        logger.debug("Index is %i", index)
       
        # Need arbitrary image type extension to get to the page with just a picture.
        # We'll assume that the file is a jpg, because it probably is according to 
        # my interpretation of https://help.imgur.com/hc/en-us/articles/201424906-What-file-types-are-allowed
        # Alternatively, future development could read the magic bytes of the image and figure out
        # what image type it was.
        image_url = ImgurCallbacks.imgur_stub + ImgurCallbacks._image_ids[index] + ".jpg" 
        result = _download_image(image_url)
        
        if result is not None:
            if cfg.set_as_background(ImgurCallbacks._img_path):
                logger.debug("Successfully set background")
                cfg.album_pos = index + 1
                logger.debug("New index is %i", cfg.album_pos)
            else:
                logger.warning("Setting background failed, trying the default image...")
                # Delete current image file and try the default
                try:
                    os.remove(ImgurCallbacks._img_path)
                except Exception as e:
                    # Doesn't matter, just don't kill the program
                    pass 

                if cfg.set_as_background(ImgurCallbacks._DEFAULT_IMAGE):
                    logger.warning("Successfully set default background")
                else:
                    logger.critical("Something went terribly wrong...")
                    dialogs.error_dialog_box(title="Critical Failure" , message="Something went terribly wrong...")

    @staticmethod
    def save_image():
        """Callback to use to save the current image to file.

        More accurately, this will simply copy the file from where it is
        in the image folder to somewhere the user chooses, since the
        image was already written to disk to be able to use it as
        a background.
        """
        if os.path.isfile(ImgurCallbacks._img_path):
            filename = dialogs.save_dialog_box(title="Save File As...", initialfile="cool_background.jpg", defaultextension=".jpg")
            if filename:
                logger.info("Saving file to %s", filename)
                try:
                    shutil.copyfile(ImgurCallbacks._img_path, filename)
                except Exception as e:
                    logger.error("The copy operation failed")
                    dialogs.error_dialog_box(title="Copy Failed" , message="The copy operation failed!")
            else:
                logger.info("Cancelled save image operation")
        else:
            logger.warning("No image to save, doing nothing...")
            dialogs.warning_dialog_box(title="No File Exists" , message="There is no image to save!")

    @staticmethod
    def change_url():
        """Callback to use to change the URL of the Imgur album to pull images from."""
        new_url = ""
        first_time = True # used to emulate a do-while loop
        while (first_time or (new_url is not None and not cfg.verify_url(new_url))):

            if not first_time:
                # If we hit this, then the URL was not valid so the user should be prompted.
                logger.error("The provided URL was not a valid Imgur album URL! URL: %s", new_url)
                dialogs.error_dialog_box(title="Invalid URL" , message="The provided URL is not a valid Imgur album URL!")

            new_url = dialogs.string_input_box(title="Imgur URL Entry", prompt="Enter the new Imgur album URL to use: ",
                                                initialvalue=cfg.imgur_album_url)
            first_time = False

        if new_url is None:
            # User cancelled out of the dialog box
            return

        logger.info("Changing Imgur album URL to %s", new_url)
        cfg.imgur_album_url = new_url
        cfg.album_pos = 0

        # Immediately write new url and position to config file (so that in case of unexpected/unnatural shutdown,
        # the changes will be saved)
        cfg.write_config_to_file()

        # Reinitialize the image id's
        ImgurCallbacks._image_ids = _initialize_images()