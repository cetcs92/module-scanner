#!/usr/bin/env python
#
"""
Scan the modules/files to identify imports

"""

import os
import ast
import importlib


def find_imports(source):

    """
    Use AST to find all imports in the source code
    """

    for _ in ast.walk(ast.parse(source)):
        if isinstance(_, ast.Import):
            for import_found in _.names:
                yield import_found.name.split('.')[0]
        elif isinstance(_, ast.ImportFrom) and _.module:
            yield _.module.split('.')[0]


class ImportScan():

    """
    Scan imports from the modules/files
    """

    def __init__(self):
        self._imports_found = set()
        self._repo_root = None
        self._cur_local_modules = None

    def scan(self, path=os.getcwd()):

        """
        Scan the module/files for imports from particular path (optional)

        Args:
            path (String, optional): Path for module which is to be scanned.\
                Defaults to os.getcwd().
        """

        self._repo_root = path
        for subdir, directories, files in os.walk(path):
            py_files = [_ for _ in files if _.endswith('.py')]
            self._cur_local_modules = [_ for _ in directories if not _.startswith('.')] +\
                [_.replace('.py', '') for _ in py_files]
            for file in py_files:
                try:
                    self._scan_file(os.path.join(subdir, file))
                except SyntaxError:
                    print(f'# SyntaxError; Skipping file {file}')

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
                print(f'Unable to parse file {file}. Skipping ...')
            else:
                self._find_all_imports(file_contents)

    def _find_all_imports(self, file_contents):

        """
        Scan the file contents to find the imports

        Args:
            file_contents (String):
            content of file that is to be scanned to find imports
        """

        for import_found in find_imports(file_contents):
            if import_found in self._cur_local_modules:
                continue

            try:
                module = importlib.import_module(import_found)
            except ModuleNotFoundError:
                # Possible pip package, but PYTHONPATH / virtual env not set?
                self._imports_found.add(import_found)
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
