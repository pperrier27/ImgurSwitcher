# Windows Development Info

## Requirements

ImgurSwitcher on Windows requires (see also the [requirements file](./requirements.txt)):

* Python 3.4 (at least until py2exe comes out with 3.5 support) and pip
* tkinter (comes with the Python 3.4 installation)
* pywin32 build 219 for Python 3.4 and your machine's particular architecture, available from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/) (recommended) or [here](http://sourceforge.net/projects/pywin32/)
* A custom version of pyHook. The base pyHook source is available [here](http://sourceforge.net/projects/pyhook), and a wheel for amd64 Windows machines is available from [here](../windows/pyhook_mods). See the [pyHook mod section](#pyhook-mod) for more details.
* [py2exe](http://www.py2exe.org/) if you want to build new executables
* [wheel](http://pythonwheels.com/) if you want to distribute wheel files

## Install ##
For py2exe and wheel, `pip install <name>` will work. For pywin32, follow the instructions given at wherever you got the source (`pip install` works with wheel files). For pyHook:
* If you are using the wheel from this repository, `pip install <name of whl file>`
* If you are building it yourself, see the [pyHook mod section](#pyhook-mod)

## pyHook mod
The most current version of pyHook causes crashes whenever the focus is on a window which uses Unicode characters in its title (Skype does this, as does Sublime Text 2). The mod fixes this problem, but if you are not using the wheel from this project, you will have to build the modified version of pyHook yourself.

For this you will need the [pyHook source](http://sourceforge.net/projects/pyhook), the MSVC 10.0 compiler for your particular machine bittedness (Visual Studio 2010 Express includes the 32-bit compiler you need; the Windows 7.1 SDK includes the 64-bit version), and [SWIG](http://www.swig.org/). The steps are:

1. Launch a command prompt with the MSVC 10.0 environment variables enabled (either launch one from VS2010 or find and run the batch script that sets them)
2. Replace the `cpyHook.i` and `setup.py` files in the pyHook source with the modified ones from [this repository](../windows/pyhook_mods)
3. Navigate to the root of the pyHook source directory and run `python setup.py build_ext --swig=<path to swig.exe>`, followed by `pip install --upgrade .`

## Building Executables
If you want to build a new executable, then set the variable `_building_exe` in `__init__.py` to True (this fixes a path problem with where the data files are). Then, navigate to the `src` directory and run `python py2exe_setup.py py2exe`. This will put all the required files in the `windows/dist` directory of this project.

### Note For `virtualenv` Users ###

If you use `virtualenv`, then you will have to copy the `tcl` directory from your local Python installation to the top-level directory of your virtual environment, unless you used `--system-site-packages` (have not tested this though)