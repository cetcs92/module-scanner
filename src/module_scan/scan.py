#!/usr/bin/env python
#
"""
Scan the modules/files to identify imports

"""

import os
import re
import importlib
from functools import reduce


WHITE_SPACE = r'[ \t]*'
WHITE_SPACE_PLUS = r'[ \t]+'
NON_CAPTURE_BEGINNING_OF_LINE = r'(?:^|\n' + WHITE_SPACE + r')'
NON_CAPTURE_IMPORT_STATEMENT = r'(?:from|import)'
CAPTURE_MODULE_NAME = r'([a-zA-Z0-9_]+)'
OPTIONAL_MORE_MODULES = r'(?:' + WHITE_SPACE + r'[,]' + WHITE_SPACE + CAPTURE_MODULE_NAME + r')*'


class ImportScan():

    """
    Scan imports from the modules/files
    """

    def __init__(self):
        self._import_re = re.compile(
            NON_CAPTURE_BEGINNING_OF_LINE +
            NON_CAPTURE_IMPORT_STATEMENT +
            WHITE_SPACE_PLUS +
            CAPTURE_MODULE_NAME +
            OPTIONAL_MORE_MODULES
        )
        self._imports_found = set()
        self._repo_root = None

    def scan(self, path=os.getcwd()):

        """
        Scan the module/files for imports from particular path (optional)

        Args:
            path (String, optional): Path for module which is to be scanned.\
                Defaults to os.getcwd().
        """

        self._repo_root = path
        for subdir, _, files in os.walk(path):
            for file in [_ for _ in files if _.endswith('.py')]:
                self._scan_file(os.path.join(subdir, file))

    def print(self):

        """
        Print discovered imports
        """

        if self._imports_found:
            for _ in self._imports_found:
                print(_)
        else:
            print('No pip module imports discovered')

    def packages(self):
        """
        Scan Packages
        """
        for _ in self._imports_found:
            yield _

    def _scan_file(self, file):

        """
        Scanning file to find out the imports

        Args:
            file (String):Path of a file that is to be scanned for imports
        """

        with open(file, 'r', encoding='utf-8') as pyfile:
            try:
                file_contents = pyfile.read()
            except UnicodeDecodeError:
                print('Unable to parse file {}. Skipping ...'.format(file))
            else:
                self._scan_file_contents(file_contents)

    def _scan_file_contents(self, file_contents):

        """
        Scan the file contents to find the imports

        Args:
            file_contents (String):
            content of file that is to be scanned to find imports
        """

        if self._import_re.search(file_contents):
            imports_found = {_ for _ in \
                reduce(lambda l1,l2:l1+l2, \
                self._import_re.findall(file_contents)) \
                if _.strip()}
            for import_found in imports_found:
                # assume all are standard python modules
                module_type = 'standard'
                try:
                    module = importlib.import_module(import_found)
                except ModuleNotFoundError:
                    # Possible pip package, but PYTHONPATH / virtual env not set?
                    module_type = 'pip ?'
                else:
                    # determine the module is pip package or local import
                    try:
                        loc = module.__spec__.origin or ''
                    except AttributeError:
                        try:
                            loc = module.__file__ or ''
                        except AttributeError:
                            loc = ''
                    if 'site-packages' in loc or 'dist-packages' in loc:
                        module_type = 'pip'
                    elif loc.startswith(self._repo_root):
                        module_type = 'local repo'
                if module_type not in ['standard', 'local repo']:
                    self._imports_found.add(import_found)


def main():

    """
    Main function Entry point to run the code
    """

    module_scan = ImportScan()
    module_scan.scan()
    module_scan.print()

if __name__ == '__main__':
    main()
