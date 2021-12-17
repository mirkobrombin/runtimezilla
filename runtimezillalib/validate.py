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

from re import sub
from schema import Schema, And, Use, Optional, SchemaError

from runtimezillalib.log import log

class Validator:
    recipe_schema = Schema({
        "properties": {
            "name": And(Use(str)),
            "version": And(Use(str)),
            "description": And(Use(str)),
            "author": And(Use(str)),
            "url": And(Use(str)),
            "license": And(Use(str))
        },
        "packager": And(Use(str)),
        "system": {
            "name": And(Use(str)),
            "min_version": And(Use(str)),
            "max_version": And(Use(str))
        },
        "ingredients": [
            {
                "name": And(Use(str)),
                "package": And(Use(str)) or None,
                "source": And(Use(str)) or None,
                "type": And(Use(str), lambda x: x in ['lib32', 'lib64', 'bin'])
            }
        ]
    })

    packager_schema = Schema({
        "name": And(Use(str)),
        "commands": And(Use(list)),
        "wrapper": {
            "sudo": And(Use(bool)),
            "install": And(Use(str)),
            "remove": And(Use(str)),
            "upgrade": And(Use(str)),
            "update": And(Use(str)),
            "clean": And(Use(str)),
            "autoremove": And(Use(str)),
            "whatprovides": And(Use(str))
        }
    })

    @staticmethod
    def test(data: dict, schema: Schema):
        try:
            schema.validate(data)
            return True
        except SchemaError as e:
            log([f'{e}'])
            return False

    @staticmethod
    def test_recipe(recipe:dict):
        from pprint import pprint
        return Validator.test(recipe, Validator.recipe_schema)
        
    @staticmethod
    def test_packager(packager:dict):
        return Validator.test(packager, Validator.packager_schema)

