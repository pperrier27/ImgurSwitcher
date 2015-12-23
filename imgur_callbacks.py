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
import pythoncom as com
import config as cfg

class ImgurSwitcherException(Exception):
    """ Simple general exception class to use if something goes wrong with this program. """
    def __init__(self, msg=None):
        self.message = msg


def _initialize_images():
    """ Initializes the image ID list from the given URL in the config module """
    
    # This should always be true unless someone went and manually edited the value, rather than using the program
    # to change it.
    if cfg.verify_url(cfg.imgur_album_url):
        # Do stuff
        pass
    else:
        # TODO: make this an error dialog box
        print("URL is not valid!")

class ImgurImages:
    
    _imageIds = _initialize_images()
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
    def change_url():
        """ Callback to use to change the URL of the Imgur album to pull images from."""
        pass

    @staticmethod
    def quit():
        """ Callback to use to cause this program to end."""
        _exit(0)