'''
MIT License

Copyright (c) 2021 Mirko Brombin <send@mirko.pm>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import subprocess

from runtimezillalib.packager import PackagerWrapper
from runtimezillalib.runtime import Runtime
from runtimezillalib.log import log


class Builder:

    def __init__(self, recipe, output):
        self.recipe = recipe
        self.output = output
        self.runtime = Runtime(self.recipe["properties"], self.output)
        self.result = {
            'found': [],
            'missing': []
        }

        self.packager_wrapper = PackagerWrapper(self.recipe['packager'])
    
    def process_ingredients(self):
        log(["Processing {} ingredients".format(len(self.recipe['ingredients']))])

        # install packages
        for ingredient in self.recipe['ingredients']:
            _package = ingredient.get('package')

            if _package is not None:
                '''
                If the ingredient defines a package, install it before
                processing all files. If not, look for which package
                provides each file.
                '''
                _res = self.packager_wrapper.install(_package)

            for file in ingredient['files']:
                _name = file

                if _package is None:
                    '''
                    Package was not installed, so we need to find which
                    one provides the needed file.
                    '''
                    _res = self.packager_wrapper.whatprovides(_name, install=True)
                
                if _res.status:
                    self.result['found'].append(_name)
                else:
                    self.result['missing'].append(_name)

        # pack found in runtime
        for file in self.result['found']:
            _name = file
            self.copy_to_runtime(_name)

        log([
            "All ingredients are processed:",
            f"Found [{len(self.result['found'])}]:",
            self.result['found'],
            f"Missing [{len(self.result['missing'])}]:",
            self.result['missing']
        ])

        return True
    
    def copy_to_runtime(self, file: str):
        files = self.search_in_system(file)
        if not file:
            log([f"{file} not found in current system, skipping"])
            return False
                
        for f in files:
            self.runtime.copy(f)
        return True
    
    def search_in_system(self, file: str):
        log([f"Searching for {file}"])
        found = []
        
        res = subprocess.Popen(
            "ldconfig -p | grep '{}'".format(file),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = res.communicate()

        if res.returncode == 0:
            ld_res = stdout.decode('utf-8').split('\n')
            if len(ld_res) > 1:
                for l in ld_res:
                    l = l.split('=>')
                    if len(l) > 1:
                        found.append(l[1].strip())
            return found
        return False

    def build(self):
        self.runtime.init()
        if self.process_ingredients():
            self.runtime.compress()
            log(["Runtime is ready, you can find it in {}".format(self.output)])
