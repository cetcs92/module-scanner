# Module Scanner
Scans Python project for all module imports that are NOT part of Python standard library regardless of whether the package is installed or not. Since this module does not consult pip installed modules, this scan can be performed on CI.
## Features
* Scans source code repository recursively for module imports
* Finds packages even if they are not installed (useful in automated builds with no virtual environments)
* Lightweight scanner

## Installation
* Clone repository and run the script
* Install using pip
```shell
$pip install module-scanner
```
