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
import subprocess
from glob import glob

from runtimezillalib.result import Result


class Packager:

    def get_packagers() -> dict:
        results = {}

        if not os.path.exists('packagers'):
            return {}
        
        packagers = glob('packagers/*.yml')
        for p in packagers:
            with open(p, 'r') as f:
                _packager = yaml.safe_load(f)
                results[_packager['name']] = _packager

        return results
    
    def get_packager(name: str) -> dict:
        packagers = Packager.get_packagers()
        return packagers.get(name, {})
    
    def list_supported() -> list:
        packagers = Packager.get_packagers()
        return list(packagers.keys())


class PackagerWrapper:

    def __init__(self, packager: str):
        self.packager = Packager.get_packager(packager)
    
    def __exec(self, command: str):
        if self.packager["wrapper"]["sudo"]:
            command = f"sudo {command}"

        res = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = res.communicate()
        return Result(
            status=res.returncode == 0,
            data={
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        )
    
    def whatprovides(self, package: str, install: bool = False):
        cmd = self.packager["wrapper"]["whatprovides"].format(package)
        res = self.__exec(cmd)
        res.data["packages"] = res.data["stdout"].split("\n")

        if install:
            _package = res.data["packages"][0]
            res = self.install(_package)
            
        return res        
    
    def install(self, package: str):
        cmd = self.packager["wrapper"]["install"].format(package)
        return self.__exec(cmd)
        
    def remove(self, package: str):
        cmd = self.packager["wrapper"]["remove"].format(package)
        return self.__exec(cmd)
    
    def upgrade(self):
        cmd = self.packager["wrapper"]["upgrade"]
        return self.__exec(cmd)
    
    def update(self):
        cmd = self.packager["wrapper"]["update"]
        return self.__exec(cmd)
    
    def clean(self):
        cmd = self.packager["wrapper"]["clean"]
        return self.__exec(cmd)
    
    def autoremove(self):
        cmd = self.packager["wrapper"]["autoremove"]
        return self.__exec(cmd)
    