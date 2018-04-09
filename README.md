# EarTimeWrangler

[![Generic badge](https://img.shields.io/badge/Python-3.6-<red>.svg)](https://www.python.org/downloads/release/python-360/)  [![Generic badge](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 

Tabular Document Wrangler. The code parses data –  originally in the form of severely heterogeneous .pdf files – on ministerial meetings between ministers and lobbyists. It forms a central part of **'Ear-time with the Cabinet: Ministerial meetings as vehicles for lobbying.'**, which is a joint collaboration between the University of Oxford and Transparency International UK.

### Prerequisites
As a pre-requisite to running [wrangler.py](https://github.com/crahal/EarTimeWrangler/blob/master/src/wrangler.py), you might consider setting up a [virtual environment](https://docs.python.org/3/tutorial/venv.html) with an installation of ```pdfminer3k```.

### Running the Code

Either manually download a zip of this repository or ```git clone https://github.com/ianknowles/EarTimeWrangler
``` this repository and run ```python wrangler.py``` in ```src```.

### Data Location

The expected location for input files is ```data```, with subfolders expected to match the government department code.

### License

This work is free. You can redistribute it and/or modify it under the terms of the MIT license.

### Acknowledgments

The project was initially funded by an ESRC Impact Acceleration Account Knowledge Exchange Kick-Start grant and contained contributions from researchers funded at one stage or another by Transparency International, the British Academy, ERC and the Wellcome Trust.
