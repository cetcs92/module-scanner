#!/usr/bin/env python
# 
import os
import re
import importlib

class ImportScan(object):
    def __init__(self):
        self._import_re = re.compile(r'(?:^|\n[ \t]*)(?:from|import)[ \t]+([a-zA-Z0-9_]+)(?:.*)')
        self._imports_found = set()

    def scan(self, path=os.getcwd()):
        for subdir, _, files in os.walk(path):
            for file in [_ for _ in files if _.endswith('.py')]:
                self._scan_file(os.path.join(subdir, file))

    def print(self):
        if self._imports_found:
            for _ in self._imports_found:
                print(_)
        else:
            print('No pip module imports discovered')

    def packages(self):
        for _ in self._imports_found:
            yield _

    def _scan_file(self, file):
        with open(file, 'r') as pyfile:
            try:
                file_contents = pyfile.read()
            except:
                print('Unable to parse file {}. Skipping ...'.format(file))
            else:
                if self._import_re.search(file_contents):
                    for import_found in self._import_re.findall(file_contents):
                        standard_module = True
                        try:
                            module = importlib.import_module(import_found)
                        except ModuleNotFoundError:
                            standard_module = False
                        else:
                            try:
                                loc = module.__spec__.origin or ''
                            except AttributeError:
                                try:
                                    loc = module.__file__ or ''
                                except AttributeError:
                                    loc = ''
                            if 'site-packages' in loc:
                                standard_module = False
                        if not standard_module:
                            self._imports_found.add(import_found)


def main():
    s = ImportScan()
    s.scan()
    s.print()

if __name__ == '__main__':
    main()
