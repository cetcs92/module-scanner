# Module Scan
Scans Python project repositories for all module imports that are NOT part of Python standard library regardless of whether the package is installed or not. Since this module does not consult pip installed modules, this scan can be performed on CI.
## Features
* Scan source code repository recursively for module imports
* Uses native Python parser to find module imports
* Find packages even if they are not installed (useful in automated builds with no virtual environments)
* Lightweight scanner useful for generating Software Bill Of Materials (SBOM)

## Installation
* Clone repository and run the script
```shell
$ git clone git@github.com:cetcs92/module-scanner.git
```
* Install using pip
```shell
$ pip install module-scan
```

## Scan repository
```shell
$ cd <repo root>
$ module-scan
```

## Import in your code
```shell
from module_scan import ImportScan

s = ImportScan()

# scan repository in current working directory
s.scan() 

# OR scan repository in a different location
# s.scan(<path to repository to scan>)

# Print the modules discovered
# _imports_found is a dictionary with filename as key and set of packages as value
# { 
#   file1: {pkg1, pkg2, ...},
#   file2: ....
# }
print(s._imports_found)

# Let module scan do a pretty print of modules discovered
s.print()

# Use module-scan info in your code
for file, pkg in s.packages():
  # do something with file, pkg
```
