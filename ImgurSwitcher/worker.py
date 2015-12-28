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
import ImgurSwitcher.config as cfg
import ImgurSwitcher.event_queue as eq

class Worker(Thread):
    """Class that does the invoking of the queued callbacks to avoid blocking the main thread."""

    def run(self):
        while True:
            fcn = eq.event_queue.get()
            if fcn[1]:
                fcn[1]()  # the event queue contains tuples; the callback is the second item
                eq.event_queue.task_done()
            else:
                # This means that the user wants to quit the program, since only quit should pass a None callback
                break
        
        cfg.write_config_to_file()
        cfg.exit_program()