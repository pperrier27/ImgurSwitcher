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
import imgurswitcher.config as cfg
import imgurswitcher.event_queue as eq

logger = logging.getLogger(__name__)

class Worker(Thread):
    """Class that does the invoking of the queued callbacks to avoid blocking the main thread."""

    def run(self):
        while True:
            if not eq.is_blocked():
                fcn = eq.event_queue.get()
                if fcn[1]:
                    logger.debug("Executing callback: %s", fcn[1].__name__)
                    fcn[1]()  # the event queue contains tuples; the callback is the second item
                    eq.event_queue.task_done()
                    logger.debug("Done executing callback: %s", fcn[1].__name__)
                else:
                    # This means that the user wants to quit the program, since only quit should pass a None callback
                    logger.debug("Quit command sent")
                    break
            else:
                logger.debug("Event queue is blocked, cannot execute callbacks")

        cfg.write_config_to_file()
        cfg.exit_program()