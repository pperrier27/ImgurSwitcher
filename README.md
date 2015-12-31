# ImgurSwitcher

Python 3.4 script designed to run in the background and read assorted key combinations to change your background picture from an Imgur album.
Currently Windows-only, but Mac/Linux support is in the works!

## How To Install ##
#### Windows ####
On Windows 64-bit (not Itanium) machines, simply [download the zip file](./windows/dist) in `windows/dist` and unzip to somewhere on your computer. Then, launch imgurswitcher.exe and you're done! See the [usage instructions](#how-to-use) for the key combinations.

If you don't want to launch the ImgurSwitcher executable every time you log in, you should add the ImgurSwitcher executable to the list of startup tasks. Google has good info on how to do this, but here's [a link](http://superuser.com/a/797635) to some instructions.

On machines other than this, you will have to build from source (for now). See the [Windows development info](./info/windows_dev.md) for instructions.

## How To Use ##
Here are the key combinations:

* ALT + D: Set background to the next image in the album (wraps around)
* ALT + A: Set background to the previous image in the album (wraps around)
* ALT + R: Set background to a random image in the album
* ALT + S: Save the current background image to a location of your choice
* ALT + U: Set the URL to the Imgur album you want to use as the image source
* ALT + Q: Quit ImgurSwitcher

## Support ##
Tested on my Windows 10 64-bit machine (i.e. the only one I have access to right now :) ). 

If you find a bug, please submit it to the Issues page on this repository.

## ToDo List ##
The ToDo list is [here](./TODO.md)

## Development Info ##
#### Windows ####
The Windows development info, including requirements and building instructions, is [here](./info/windows_dev.md).

## Contributors ##
[Me](https://github.com/pperrier27/)