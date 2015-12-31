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
import tkinter.simpledialog
from . import event_queue as eq # most/all of the dialogs need to block the event queue

def save_dialog_box(title = "Save File As...", defaultextension = "", 
                    initialdir=None, initialfile=None, filetypes=None):
    """Show a save dialog box.

    title: The title of the dialog box.
    defaultextension: The default extension for the file, if not specified by the user.
    initialdir: The directory to show on dialog box load.
    initialfile: The initial name for the file to save.
    filetypes: Not really used, but a list of tuples of the label and the pattern that the file should match
    e.g. [("All files", "*.*")]

    Returns the file name the user wants to save the file as if successful,
    None if not.
    """

    eq.block()
    root = tkinter.Tk()
    root.withdraw() # hide the main tk window
    filename = tkinter.filedialog.asksaveasfilename(title=title, defaultextension=defaultextension,
                                                    initialfile=initialfile, initialdir=initialdir)
    root.destroy()
    eq.unblock() 
    return filename

def string_input_box(title="String Entry", prompt="Enter a string: ", initialvalue=""):
    """Show a dialog box where a string can be input.

    title: The title of the dialog box.
    prompt: The prompt immediately above the string entry box.
    initialvalue: The initial value of the string in the entry box.
    Returns the string that was input, or None if the window was exited.
    """
    eq.block()
    root = tkinter.Tk()
    root.withdraw() # hide the main tk window
    result = tkinter.simpledialog.askstring(title=title, prompt=prompt, initialvalue=initialvalue)
    root.destroy()
    eq.unblock() 
    return result

def error_dialog_box(title="ImgurSwitcher", message="An error occurred."):
    """Shows an error dialog box.

    title: The title of the dialog box.
    message: The message to show.

    Returns nothing.
    """
    eq.block()
    root = tkinter.Tk()
    root.withdraw() # hide the main tk window
    result = tkinter.messagebox.showerror(title=title, message=message)
    root.destroy()
    eq.unblock()

def warning_dialog_box(title="ImgurSwitcher", message="A warning occurred."):
    """Shows a warning dialog box.

    title: The title of the dialog box.
    message: The message to show.

    Returns nothing.
    """
    eq.block()
    root = tkinter.Tk()
    root.withdraw() # hide the main tk window
    result = tkinter.messagebox.showwarning(title=title, message=message)
    root.destroy()
    eq.unblock()