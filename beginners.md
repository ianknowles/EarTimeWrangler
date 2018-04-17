# Beginner's setup guide

1. Download the latest version of Python (3.6 or higher) from https://www.python.org/downloads/
2. Install Python with the default options (add to PATH should be enabled and pip should be installed)
3. Open a command prompt or PowerShell. Note that to run an external executable in PowerShell such as Python or pip the command needs to be prefixed with `&`.
4. Ensure Python and pip are correctly installed by running the commands `python --version` and `pip --version`. These commands should print the version numbers of python and pip, if they do not follow the guide at https://packaging.python.org/tutorials/installing-packages/.
5. Run the command `pip install 'pdfminer3k'` to install the pdfminer library.
6. Download a [zip](https://github.com/ianknowles/EarTimeWrangler/archive/master.zip) of this repository and extract to a local folder.
7. Place input files in the `data` folder, split into subfolders for each department.
8. Open a command prompt or PowerShell in the `src` folder or use the `cd` command to set the current directory to the `src` folder.
9. Run the command `python wrangler.py` (prefix with `&` in PowerShell).
10. The outputs should now be found in the `output` folder, an sqlite database and csv formatted tables exported from the database. 
