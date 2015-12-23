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

It is required to call cfg.parse_cfg_file immediately after the
imports, because this module depends on having some config values set.
"""

import re
import os
import urllib.request, urllib.parse, urllib.error
import pythoncom as com
import config as cfg
from set_background_image import set_as_background

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

        response = None
        response_code = None
        try:
            response = urllib.request.urlopen(url=fullListURL)
            response_code = response.getcode()
        except Exception as e:
            response = False
            response_code = e.code
        
        if not response or response.getcode() != 200:
            # TODO: Change this to a dialog box
            raise cfg.ImgurSwitcherException("Error reading Imgur: Error Code %d" % response_code)

        html = response.read().decode('utf-8')
        return re.findall('<div id="([a-zA-Z0-9]+)" class="post-image-container', html) # found by inspecting the source of an imgur album page

    else:
        # TODO: change this into a dialog box
        raise cfg.ImgurSwitcherException("The provided URL is not a valid Imgur URL!")


class ImgurCallbacks:
    """Holds the callbacks and information they require."""

    _image_ids = _initialize_images()
    _imgur_stub = r"http://i.imgur.com/"
    _current_image_path = ""
    _current_image_id = "" # Use as a caching helper

    @staticmethod
    def next_image():
        """Callback to use to fetch the next image in the album and set it as the background."""
        # cfg.album_pos is 1-indexed
        index = (cfg.album_pos - 1) % len(ImgurCallbacks._image_ids)
        
        # Save values that are about to be overriden that we need later
        old_image_path = ImgurCallbacks._current_image_path
        
        # Need arbitrary image format extension to get to the page with just the image. Will fix to the actual format later.
        image_url = ImgurCallbacks._imgur_stub + ImgurCallbacks._image_ids[index] + ".jpg" 
        
        try:
            ImgurCallbacks._current_image_path, junk = urllib.request.urlretrieve(image_url)
        
        except Exception as e:
            # For now just leave it alone... TODO: dialog box that warns the user that this operation couldn't complete.            
            print("Download failed!")
            return

        if set_as_background(ImgurCallbacks._current_image_path):
            print("Success at setting bg!")
            # Delete old image file
            album_pos += 1
        else:
            print("Bg set fail!")
            # Delete current image file
        
    @staticmethod
    def prev_image():
        """Callback to use to fetch the previous image in the album and set it as the background."""
        print("Prev image callback!")

    @staticmethod
    def random_image():
        """Callback to fetch a random image in the album and set it as the background."""
        print("Random image callback!")
    
    @staticmethod
    def save_image():
        """Callback to use to save the current image to file.

        More accurately, this will simply move the file from a temp
        file (and temp name) to something the user chooses, since the
        image was already written to disk to be able to use it as
        a background.
        """
        print("Save image callback!")


    @staticmethod
    def change_url():
        """Callback to use to change the URL of the Imgur album to pull images from."""
        print("Change url callback!")
