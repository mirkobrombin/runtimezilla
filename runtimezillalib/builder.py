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

from glob import glob

from runtimezillalib.packager import PackagerWrapper
from runtimezillalib.runtime import Runtime
from runtimezillalib.log import log


class Builder:

    def __init__(self, recipe, output):
        self.recipe = recipe
        self.output = output
        self.runtime = Runtime(self.recipe["properties"], self.output)
        self.result = {
            'found': {},
            'missing': []
        }

        self.packager_wrapper = PackagerWrapper(self.recipe['packager'])
    
    def process_ingredients(self):
        log(["Processing {} ingredients".format(len(self.recipe['ingredients']))])

        # install packages
        for ingredient in self.recipe['ingredients']:
            _package = ingredient.get('package')
            _type = ingredient.get('type')

            if _package is not None:
                '''
                If the ingredient defines a package, install it before
                processing all files. If not, look for which package
                provides each file.
                '''
                _res = self.packager_wrapper.install(_package)

            for file in ingredient['files']:
                _name = list(file.keys())[0]
                _source = file[_name]

                if _package is None:
                    '''
                    Package was not installed, so we need to find which
                    one provides the needed file.
                    '''
                    _res = self.packager_wrapper.whatprovides(_name, install=True)
                
                if _res.status:
                    self.result['found'][_name] = {
                        'source': _source,
                        'type': _type,
                    }
                else:
                    self.result['missing'].append(_name)

        # pack found in runtime
        for file in self.result['found']:
            _file = self.result['found'][file]
            _source = _file.get('source')
            _type = _file.get('type')

            self.copy_to_runtime(
                file=_source if _source else file,
                scope=_type,
                find=_source is None
            )

        log([
            "All ingredients are processed:",
            f"Found [{len(self.result['found'])}]:",
            [k for k in self.result['found'].keys()],
            f"Missing [{len(self.result['missing'])}]:",
            self.result['missing']
        ])

        return True
    
    def copy_to_runtime(self, file: str, scope: str, find: bool = False):
        if find:
            log([f"Path to {file} is not specified, searching in current system"])
            paths = {
                "bin": [
                    '/bin',
                    '/usr/bin',
                    '/usr/local/bin'
                ],
                "lib32": [
                    '/lib',
                    '/usr/lib',
                    '/usr/local/lib',
                    '/usr/lib/i386-linux-gnu',
                ],
                "lib64": [
                    '/usr/lib64',
                    '/usr/local/lib64',
                    '/usr/lib/x86_64-linux-gnu'
                ]
            }
            paths["lib"] = paths["lib32"] + paths["lib64"]
            if scope in paths.keys():
                use_paths = paths[scope]
            else:
                use_paths = paths

            file = self.search_in_system(file, use_paths)
            if not file:
                log([f"{file} not found in current system, skipping"])
                return
                
        self.runtime.copy(file, scope)
        return True
    
    def search_in_system(self, name: str, paths: list):
        log([f"Searching for {name}"])
        for path in paths:
            for file in glob(f"{path}/**/{name}", recursive=True):
                return file
        return False

    def build(self):
        self.runtime.init()
        if self.process_ingredients():
            self.runtime.compress()
            log(["Runtime is ready, you can find it in {}".format(self.output)])
