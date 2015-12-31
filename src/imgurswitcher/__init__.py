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

# Name of the log file. Will be created in the same directory as this script.
LOG_FILE_NAME = "imgur_switcher_log.txt"

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename=LOG_FILE_NAME, filemode='w')
logger.setLevel(logging.INFO)

import imgurswitcher.event_queue
import imgurswitcher.config # also ensures that the initialization is run

# Initialize what needs initializing, specififcally in this order
event_queue.init()
config.set_platform_config()

# Make available common parts from the package level
# Worker depends on the event queue being initialized
from imgurswitcher.worker import Worker

# Set the main function to use based on the platform
main = config.Main

__all__ = [] # don't want to support using "from imgurswitcher import *""