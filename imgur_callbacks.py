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


# File contains methods to deal with Imgur/callbacks to use when the user chooses to move things around.
# TODO: Make a proper docstring/improve the wording of this comment.

from os import _exit # lets us kill the whole program from a thread, which is needed because the quit functionality 
                     # is called in a thread!
import urllib.request, urllib.parse, urllib.error
import re
import pythoncom as com
import config as cfg

cfg.parse_cfg_file() # Need to call this because ImgurImages depends on it

def _initialize_images():
    """ Initializes the image ID list from the given URL in the config module """
    
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
            raise cfg.ImgurSwitcherException("Error reading Imgur: Error Code %d" % response_code)

        html = response.read().decode('utf-8')
        return re.findall('<div id="([a-zA-Z0-9]+)" class="post-image-container', html) # found by inspecting the source of an imgur album page

    else:
        # TODO: change this into a dialog box
        raise cfg.ImgurSwitcherException("The provided URL is not a valid Imgur URL!")

class ImgurImages:
    
    _image_ids = _initialize_images()
    _image_index = 0 # keep track of which image we're on
    
    @staticmethod
    def next_image():
        """ TODO: Improve this docstring
            Callback to use to fetch the next image.
        """
        
    @staticmethod
    def prev_image():
        """ TODO: Improve this docstring
            Callback to use to fetch the previous image.
        """
        print("Prev image callback!")

    @staticmethod
    def save_image():
        """ TODO: Improve this docstring
            Callback to use to save the current image to file.

            More accurately, this will simply move the file from the
            %TEMP% directory to somewhere the user chooses, since the
            image was already written to disk to be able to use it as
            a background.
        """
        print("Save image callback!")

    @staticmethod
    def random_image():
        """ Callback to select a random image. """
        print("Random image callback!")
        
    @staticmethod
    def change_url():
        """ Callback to use to change the URL of the Imgur album to pull images from."""
        pass

    @staticmethod
    def quit():
        """ Callback to use to cause this program to end."""
        _exit(0)