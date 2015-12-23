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

""" Module contains the platform-specific functionality to set an
    image as a background picture. 
"""

import config as cfg

if cfg.platform == "Windows":
    def set_as_background(url):
        print("Setting background Windows!")
        import ctypes
        SPI_SETDESKWALLPAPER = 20 
        return ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, url, 3)

elif cfg.platform == "Darwin":
    def set_as_background(url):
        print("Setting background Mac!")

elif cfg.platform == "Linux":
    def set_as_background(url):
        print("Setting background Linux!")

# Default handler in case something slipped through, but should NEVER get here
else:
    print("How did you get here?")