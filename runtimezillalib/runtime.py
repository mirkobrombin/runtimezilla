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
import yaml
import shutil
import tarfile

from runtimezillalib.log import log


class Runtime:

    def __init__(self, properties: dict, output: str):
        self.properties = properties
        self.output = output
        self.paths = {
            'runtime': self.output,
            'bin': os.path.join(self.output, 'bin'),
            'lib32': os.path.join(self.output, 'lib32'),
            'lib64': os.path.join(self.output, 'lib64')
        }
        self.paths['lib'] = [self.paths['lib32'], self.paths['lib64']]
    
    def init(self):
        log(["Initializing runtime"])
        for path in self.paths:
            if path == "lib":
                continue
            os.makedirs(self.paths[path], exist_ok=True)
        
        with open(os.path.join(self.output, 'manifest.yml'), 'w') as f:
            yaml.dump(self.properties, f)

    
    def copy(self, file: str, dest: str):
        log([f"Copying {file} to runtime"])
        try:
            if dest not in self.paths:
                return False

            if dest == "lib":
                shutil.copy(file, self.paths["lib32"])
                shutil.copy(file, self.paths["lib64"])
            else:
                shutil.copy(file, self.paths[dest])
        except Exception as e:
            log([f"Error while copying {file} to runtime: {e}"])
            return False
            
        return True

    def compress(self):
        log(["Compressing runtime"])
        with tarfile.open(f"{self.output}.tar.gz", 'w:gz') as tar:
            tar.add(self.output, arcname=os.path.basename(self.output))
        return True
