# Spine Toolbox

[![Python](https://img.shields.io/badge/python-3.7%20|%203.8-blue.svg)](https://www.python.org/downloads/release/python-379/)
[![Documentation Status](https://readthedocs.org/projects/spine-toolbox/badge/?version=latest)](https://spine-toolbox.readthedocs.io/en/latest/?badge=latest)
[![Unit tests](https://github.com/Spine-project/Spine-Toolbox/workflows/Unit%20tests/badge.svg)](https://github.com/Spine-project/Spine-Toolbox/actions?query=workflow%3A"Unit+tests")
[![codecov](https://codecov.io/gh/Spine-project/Spine-Toolbox/branch/master/graph/badge.svg)](https://codecov.io/gh/Spine-project/Spine-Toolbox)

An application to define, manage, and execute various energy system simulation models.

## Programming language

- Python 3.7
- Python 3.8

Please note that Python 3.9 is not supported yet. 

## License

Spine Toolbox is released under the GNU Lesser General Public License (LGPL) license. All accompanying
documentation, original graphics and other material are released under the 
[Creative Commons BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/).
Licenses of all packages used by Spine Toolbox are listed in the Spine Toolbox User 
Guide.


## Official releases

Release versions of Spine Toolbox can be found 
[here](https://drive.google.com/drive/folders/1t-AIIwRMl3HiYgka4ex5bCccI2gpbspK)
(only available for 64-bit Windows for now). Download the latest version, install and
run `spinetoolbox.exe`.

## Development version

The development version of Spine Toolbox is in the master branch on this repository, and it has all the latest features and bug-fixes.
Please note that this version has passed automated testing, but has not been completely manually tested.

### Installation

1. Do you have Conda? If yes, go directly to step 2. Otherwise, install either [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
(recommended) or [Anaconda](https://www.anaconda.com/distribution/) (good alternative).

2. Open [Anaconda Prompt](https://docs.anaconda.com/_images/win-anaconda-prompt1.png).

3. Create a new environment by typing:

        conda create -n spinetoolbox python=3.7

4. Activate the new environment:

        conda activate spinetoolbox

5. Install **git** in the new environment:

        conda install -c anaconda git

6. Clone the Spine Toolbox repository from GitHub to your computer:

        git clone https://github.com/Spine-project/Spine-Toolbox.git

7. Navigate to your clone's root:

        cd Spine-Toolbox

8. Install requirements using **pip**:

        python -m pip install -r requirements.txt

9. Run:

        python -m spinetoolbox


### Running

1. Open [Anaconda Prompt](https://docs.anaconda.com/_images/win-anaconda-prompt1.png).

2. Activate the `spinetoolbox` environment:

        conda activate spinetoolbox

3. Run:

        python -m spinetoolbox

### Upgrading


1. Open [Anaconda Prompt](https://docs.anaconda.com/_images/win-anaconda-prompt1.png).

2. Activate the `spinetoolbox` environment:

        conda activate spinetoolbox

3. Navigate to your Spine Toolbox clone's root:

        cd Spine-Toolbox

4. Pull the latest contents of the Spine Toolbox repository:

        git pull

5. Upgrade requirements using **pip**:

        python -m pip install --upgrade -r requirements.txt


### About requirements

Python 3.7 or Python 3.8 is required.

See file `setup.py` and `requirements.txt` for packages required to run Spine Toolbox.
(Additional packages needed for development are listed in `dev-requirements.txt`.)

The requirements include three packages ([`spinedb_api`](https://github.com/Spine-project/Spine-Database-API),
[`spine_engine`](https://github.com/Spine-project/spine-engine), and [`spine_items`](https://github.com/Spine-project/spine-items)),
developed by the Spine project consortium. Since these packages are developed very actively at the moment, 
they may get upgraded quite regularly whenever you run `python -m pip install --upgrade -r requirements.txt`.

In some cases (if you forget to run `python -m pip install --upgrade -r requirements.txt` after `git pull`),
the application will refuse to start unless you upgrade these packages.
Just follow the instructions that will appear in the Anaconda Prompt
(or simply, run `python -m pip install --upgrade -r requirements.txt`).


### Building the User Guide

You can find the latest documentation on [readthedocs](https://spine-toolbox.readthedocs.io/en/latest/index.html).
If you want to build the documentation yourself,
source files for the User Guide can be found in `docs/source` directory. In order to 
build the HTML docs, you need to install the *optional requirements* (see section 
'Installing requirements' above). This installs Sphinx (among other things), which 
is required in building the documentation. When Sphinx is installed, you can build the 
HTML pages from the user guide source files by using the `bin/build_doc.bat` script on 
Windows or the `bin/build_doc.sh` script on Linux and Mac. After running the script, the 
index page can be found in `docs/build/html/index.html`. The User Guide can also 
be opened from Spine Toolbox menu Help->User Guide (F2).

### Troubleshooting

#### Installation fails

Please make sure you are using Python 3.7 or Python 3.8 to install the requirements.

#### Installation fails on Linux
If Python runs into errors while installing on Linux systems, running the 
following commands in a terminal may help:

```shell
sudo apt install libpq-dev
sudo apt-get install unixodbc-dev
```

#### Problems in starting the application

If there are problems in starting Spine Toolbox, the chances are that the required 
packages were not installed successfully. In case this happens, the first thing you 
should check is that you don't have `Qt`, `PyQt4`, `PyQt5`, `PySide`, and `PySide2` 
packages installed in the same environment. These do not play nice together and may 
introduce conflicts. In addition, make sure that you do not have multiple versions 
of these `Qt` related packages installed in the same environment. The easiest way 
to solve this problem is to create a blank (e.g. virtual environment) Python 
environment just for `PySide2` applications and installing the requirements again.

**Warning: Using the *conda-forge* channel for installing the requirements is not 
recommended.**

The required `qtconsole` package from the ***conda-forge*** channel also
installs `qt` and `PyQt` packages. Since this is a `PySide2` application, those are 
not needed and there is a chance of conflicts between the packages.

**Note**: Supported PySide2 version is **5.14**. Spine Toolbox does not support PySide2 
version 5.15 (yet).

#### ImportError: DLL load failed while importing win32api

If you installed Spine Toolbox *without Conda* on **Python 3.8 on Windows**, 
you may see this error when trying to execute a project item. The cause of this error 
is the package `pywin32` version 225. To fix this error, upgrade the package with the 
following command

```shell
pip install --upgrade pywin32
```

to the latest version and restart the application.

## Contribution Guide

All are welcome to contribute!

See detailed instructions for contribution in [Spine Toolbox User Guide](https://spine-toolbox.readthedocs.io/en/latest/contribution_guide.html).

Below are the bare minimum things you need to know.

### Setting up development environment

1. Install the developer requirements:

        pip install -r dev-requirements.txt

2. Optionally, run `pre-commit install` in project's root directory. This sets up some git hooks.

### Coding style

- [Black](https://github.com/python/black) is used for Python code formatting.
  The project's GitHub page includes instructions on how to integrate Black in IDEs.
- Google style docstrings

### Linting

It is advisable to run [`pylint`](https://pylint.readthedocs.io/en/latest/) regularly on files that have been changed.
The project root includes a configuration file for `pylint`.
`pylint`'s user guide includes instructions on how to [integrate the tool in IDEs](https://pylint.readthedocs.io/en/latest/user_guide/ide-integration.html#pylint-in-pycharm).

### Unit tests

Unit tests are located in the `tests` directory.
You can run the entire test suite from project root by

```shell
python -m unittest
```

### Reporting bugs
If you think you have found a bug, please check the following before creating a new 
issue:
1. **Make sure you’re on the latest version.** 
2. **Try older versions.**
3. **Try upgrading/downgrading the dependencies**
4. **Search the project’s bug/issue tracker to make sure it’s not a known issue.**

What to put in your bug report:
1. **Python version**. What version of the Python interpreter are you using? 32-bit 
    or 64-bit?
2. **OS**. What operating system are you on?
3. **Application Version**. Which version or versions of the software are you using? 
    If you have forked the project from Git, which branch and which commit? Otherwise, 
    supply the application version number (Help->About menu).
4. **How to recreate**. How can the developers recreate the bug? A screenshot 
    demonstrating the bug is usually the most helpful thing you can report. Relevant 
    output from the Event Log and debug messages from the console of your run, should 
    also be included.

### Feature requests
The developers of Spine Toolbox are happy to hear new ideas for features or improvements 
to existing functionality. The format for requesting new features is free. Just fill 
out the required fields on the issue tracker and give a description of the new feature. 
A picture accompanying the description is a good way to get your idea into development
faster. But before you make a new issue, please check that there isn't a related idea 
already open in the issue tracker.
