# Kasli I2C Tools

This is [quartiq/kasli-i2c](https://github.com/quartiq/kasli-i2c) packed as a Python package.

## Installation

### Linux

1. Make sure you have [PyFTDI prerequisites](https://eblot.github.io/pyftdi/installation.html#debian-ubuntu-linux) satisfied. 
1. Create new Python virtual environment:
   ```bash
   python3 -m venv ./.venv
   ```
2. Activate environment:
   ```bash
   source ./.venv/bin/activate
   ```
3. Install `kasli-i2c`:
   ```bash
   pip install https://github.com/Technosystem-Labs/kasli-i2c/archive/package.zip
   ```

### Windows

1. Make sure you have [PyFTDI prerequisites](https://eblot.github.io/pyftdi/installation.html#windows) satisfied. 
**Please note that Kasli uses multi-channel device (Quad RS-232HS).**
1. Install [Python](https://www.python.org/downloads/windows/).
2. Open PowerShell console.
3. Create new Python virtual environment:
   ```PowerShell
   python -m venv .\venv
   ```
2. Activate environment:
   ```PowerShell
   venv\Scripts\activate.ps1
   ```
   If you experience an error, it may be that running scripts is disabled in your console, see: https://stackoverflow.com/questions/67150436/cannot-be-loaded-because-running-scripts-is-disabled-on-this-system-for-more-in
3. Install `kasli-i2c`:
   ```PowerShell
   pip install https://github.com/Technosystem-Labs/kasli-i2c/archive/package.zip
   ```

## Usage

After installation you should have the following commands available in your virtual environment:

* `scan_eem` - execute to list all EEM modules connected to your Kasli