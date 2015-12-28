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

"""Module that contains the assorted dialog boxes that ImgurSwitcher uses.

Uses tkinter to provide cross-platform dialog boxes. Rather than have one
long-running tk instance, create and destroy them as needed since they're 
not expected to be required that often/live for a long time.
"""

import tkinter
import tkinter.filedialog
import tkinter.messagebox

def save_dialog_box(title = "Save File As...", defaultextension = "", 
                    initialdir=None, initialfile=None, filetypes=None):
    """Show a save dialog box.

    Returns the file name the user wants to save the file as if successful,
    None if not.
    """

    root = tkinter.Tk()
    root.withdraw() # hide the main tk window
    filename = tkinter.filedialog.asksaveasfilename(title=title, defaultextension=defaultextension,
                                                    initialfile=initialfile, initialdir=initialdir)
    root.destroy() 
    return filename
