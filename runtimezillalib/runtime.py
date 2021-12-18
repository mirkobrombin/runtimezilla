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
        self.output = os.path.abspath(output)
    
    def init(self):
        log(["Initializing runtime"])
        os.makedirs(self.output, exist_ok=True)
        
        with open(os.path.join(self.output, 'manifest.yml'), 'w') as f:
            yaml.dump(self.properties, f)

    
    def copy(self, file: str):
        log([f"Copying {file} to runtime"])
        try:
            dirname = os.path.dirname(file)
            dest_path = f"{self.output}/{dirname}".replace('//', '/')
            os.makedirs(dest_path, exist_ok=True)
            shutil.copy(file, os.path.join(dest_path, os.path.basename(file)))
        except Exception as e:
            log([f"Error copying {file} to runtime: {e}"])
            return False
            
        return True

    def compress(self):
        log(["Compressing runtime"])
        with tarfile.open(f"{self.output}.tar.gz", 'w:gz') as tar:
            tar.add(self.output, arcname=os.path.basename(self.output))
        return True
