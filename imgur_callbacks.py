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

from imgurpython import ImgurClient
import config as cfg

class ImgurCallbacks:
    """ Encapsulate callbacks as static methods of this class. """
    
    @staticmethod
    def next_image():
        """ TODO: Improve this docstring
            Callback to use to fetch the next image.
        """
        print("Next image callback!")

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
        print("Quit callback!")