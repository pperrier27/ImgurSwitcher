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

"""Module contains the worker class for ImgurSwitcher."""

from threading import Thread
import logging
from . import config as cfg
from . import event_queue as eq

logger = logging.getLogger(__name__)

class Worker(Thread):
    """Class that does the invoking of the queued callbacks to avoid blocking the main thread."""

    def run(self):
        while True:
            eq.get_and_exec()