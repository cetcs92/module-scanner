#!/usr/bin/env python
#
"""
Scan the modules/files to identify imports

"""

import os
import ast
import importlib


class ImportScan:
    """
    Scan imports from the modules/files
    """
    def __init__(self):
        self._imports_found = {}
        self._subdirs = None

    def scan(self, path=os.getcwd()):
        """
        Scan the module/files for imports from particular path (optional)

        Args:
            path (String, optional): Path for module which is to be scanned.\
                Defaults to os.getcwd().
        """
        if not os.path.exists(path):
            print(f'Invalid path: {path}')
            return

        for cur_dir, self._subdirs, files in os.walk(path):
            for one_dir in [_ for _ in self._subdirs if _.startswith('.') or _ == 'site-packages']:
                self._subdirs.remove(one_dir)
            for file in [_ for _ in files if _.endswith('.py')]:
                try:
                    self._scan_file(os.path.join(cur_dir, file))
                except SyntaxError:
                    print(f'# SyntaxError; Skipping file {file}')

    def print(self):
        """
        Print discovered imports
        """
        if self._imports_found:
            for file, pkgs in self._imports_found.items():
                print(f'File: {file}')
                print('\tImported packages:' + ('None' if not pkgs else ''))
                for pkg in pkgs:
                    print(f'\t\t{pkg}')
        else:
            print('No pip module imports discovered')

    def packages(self):
        """
        Scan Packages
        """
        for file, pkgs in self._imports_found.items():
            for pkg in pkgs:
                yield file, pkg

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
                imports = self._find_all_imports(file_contents)
                self._imports_found[file] = imports

    def _find_all_imports(self, file_contents):
        """
        Scan the file contents to find the imports

        Args:
            file_contents (String):
            content of file that is to be scanned to find imports
        """
        imports = set()
        for import_found in self._find_imports(file_contents):
            try:
                module = importlib.import_module(import_found)
            except ModuleNotFoundError:
                # Possible pip package, but PYTHONPATH / virtual env not set?
                imports.add(import_found)
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
                    imports.add(import_found)
        return imports

    def _find_imports(self, source):
        """
        Use AST to find all imports in the source code
        """
        for _ in ast.walk(ast.parse(source)):
            modules = []
            if isinstance(_, ast.Import):
                modules = [nm.name.split('.')[0] for nm in _.names]
            elif isinstance(_, ast.ImportFrom) and _.module and _.level == 0:
                modules = [_.module.split('.')[0]]
            for mod_name in [mod for mod in modules if mod not in self._subdirs]:
                yield mod_name


def main():
    """
    Main function Entry point to run the code
    """
    module_scan = ImportScan()
    module_scan.scan()
    module_scan.print()


if __name__ == '__main__':
    main()
