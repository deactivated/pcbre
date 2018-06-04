# PCBRE

**WARNING** This branch is currently non-functional. **WARNING**

PCBRE is an open source package for semiautomated and manual PCB reverse engineering.

## Documentation and Support

PCBRE currently doesn't have any documentation. This will likely change fairly soon.

For support, please join #pcbre on freenode.

## Install

PCBRE requires the following dependencies. Some will probably need to come from your systems package manager. Some might come from pip. Some need to be custom installed.

**System Packages**

- python3.4
- python3-pip (for installing python packages)
- numpy
- scipy
- python3-pyqt5

<!-- begin list -->
- Cython (required by poly2tri and pypotrace)
- geos (required by shapely, be sure to install geos with development headers)
- capnp (required by pycapnp)
- libspatialindex (required by rtree)
- freetype (required by freetype_py)
- opencv3 (with Python 3 bindings)

<!-- begin list -->
- libagg (required by pypotrace, not yet needed)
- potrace (required by pypotrace, not yet needed)

**Python Packages**

- pycapnp
- shapely
- rtree
- freetype\_py
- pyopengl
- git+https://github.com/davidcarne/poly2tri.python.git

<!-- begin list -->
- mock (only needed for tests)
- git+https://github.com/davidcarne/pypotrace.git (will be needed in the future)

Personally, I use the following sequence to setup a test environment

    virtualenv --system-site-packages -p python3.4 .env
    . .env/bin/activate
    pip install shapely signalslot mock freetype_py git+https://github.com/davidcarne/pypotrace.git git+https://github.com/davidcarne/poly2tri.python.git
    python setup.py develop

Then you can just run pcbre by typing `pcbre` into your shell (its in the virtualenv path)

## Debian/Ubuntu Specific Installation notes

PCBRE should function correctly on Debian/Ubuntu.
Install the following packages using apt:

- python3
- python3-pip
- python3-numpy
- python3-scipy
- python3-pyqt5
- libspatialindex-dev
- libgeos-dev
- libpotrace-dev
- libagg-dev
- libfreetype6-dev
- cython3

If you are running tests, also install:

- python3-mock

The following libraries may have issues when installed using the package manager, but are still required:

- libcapnp-dev (outdated, you need 0.5.2, just make install if your distro lacks this version)
- libopencv-dev (outdated, you need 3.0.0 with BUILD_NEW_PYTHON_SUPPORT -- follow the instructions [here](http://rodrigoberriel.com/2014/10/installing-opencv-3-0-0-on-ubuntu-14-04/), but make sure to use the [release version of OpenCV 3.0](http://opencv.org/downloads.html).)

Install the packages listed above in Python Packages using pip (except for mock, which you should have already installed if you need it), and you should be good to go with prerequisites.


## Windows-specific Installation notes

PCBRE is still in the process of being ported to Windows, and does not yet function correctly.

Install Python 3.4 (32-bit or 64-bit, depending on system)  
Use pip to install the following binary packages from http://www.lfd.uci.edu/~gohlke/pythonlibs:

    numpy scipy PySide Shapely PyOpenGL PyOpenGL_accelerate opencv_python Cython

Binary .whl packages for rtree, freetype_py, and poly2tri will be available soon. This is still a work-in-progress.  
[py]capnp is currently an issue on Windows, since it heavily uses C++11, which is not available with the Visual C++ 2010 runtime used by Python 3.4.

## Mac-specific Installation notes

PCBRE is still in the process of being ported to Mac OS X, and does not yet function correctly. It is being developed with the above-listed dependencies installed from [Homebrew](http://brew.sh) with some packages from the [Homebrew-science](https://github.com/Homebrew/homebrew-science) tap.


## License and Contribution Information

All source with the excluding of the following is licensed under GPLv2-or-later. That said, if you need a different license, feel free to contact me. I'm likely to grant such requests, unless its to make a commercial, closed source fork of the entire codebase.

csrc/edtaa3func.\*  is licensed under the license in its file headers (BSD)
pysrc/pcbre/resources/Vera.ttf is under the Bistream Vera Fonts copyright (BSD-like)
