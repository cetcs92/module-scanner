#!/usr/bin/env python
#
"""
Scan the modules/files to identify imports

"""

import os
import ast
import importlib
from functools import reduce


class ImportScan():

    """
    Scan imports from the modules/files
    """

    def __init__(self):
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
                self._find_all_imports(file_contents)

    def _find_all_imports(self, file_contents):

        """
        Scan the file contents to find the imports

        Args:
            file_contents (String):
            content of file that is to be scanned to find imports
        """

        ast_parse = ast.parse(file_contents)
        for import_found in self._find_imports(ast_parse):
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

    def _find_imports(self, ast_parse):
        """
        Use AST to find all imports in the source code
        """
        for _ in ast_parse.body:
            if type(_) == ast.Import:
                for import_found in _.names:
                    yield import_found.name
            elif type(_) == ast.ImportFrom:
                yield _.module
            elif 'body' in _.__dict__:
                yield from self._find_imports(_)


def main():

    """
    Main function Entry point to run the code
    """

    module_scan = ImportScan()
    module_scan.scan()
    module_scan.print()

if __name__ == '__main__':
    main()
