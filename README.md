# EarTimeWrangler

[![Generic badge](https://img.shields.io/badge/Python-3.6-<red>.svg)](https://www.python.org/downloads/release/python-360/)  [![Generic badge](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 

Tabular Document Wrangler. The code parses data from several types of poorly formatted tabular data formats, including pdf and csv files – on ministerial meetings between ministers and lobbyists. It forms a central part of **'Ear-time with the Cabinet: Ministerial meetings as vehicles for lobbying'**, which is a joint collaboration between the University of Oxford and Transparency International UK.

### Prerequisites
As a pre-requisite to running [wrangler.py](https://github.com/crahal/EarTimeWrangler/blob/master/src/wrangler.py), you might consider setting up a [virtual environment](https://docs.python.org/3/tutorial/venv.html) with an installation of `pdfminer3k`. An install of Python 3.6 or greater is required.
`pdfminer3k` can be installed with the command `pip install 'pdfminer3k'`, a full tutorial can be found [here](https://packaging.python.org/tutorials/installing-packages/).

### Running the Code

Download a [zip](https://github.com/ianknowles/EarTimeWrangler/archive/master.zip) of this repository or `git clone https://github.com/ianknowles/EarTimeWrangler` this repository and run `python wrangler.py` from the `src` folder at the command line. For a step-by-step setup guide aimed at beginners see [beginners.md](beginners.md).

### Input/output file folders

The script looks for input files in the `data` folder, with subfolders expected to match the government department code.
The SQLite database and csv exports will be placed in the `output` folder.

### License

This work is free. You can redistribute it and/or modify it under the terms of the MIT license.
This license does not apply to any input or output data processed.

### Acknowledgments

The project was funded by an ESRC IAA Kick-Start (1609-KICK-244) grant.
