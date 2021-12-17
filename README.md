# runtimezilla
This tool helps you building your own runtime.

## Requirements
- Python 3.9+ (tested on 3.10)
- [`PyYAML`](https://pypi.org/project/PyYAML/)
- [`schema`](https://pypi.org/project/schema/)

## Usage
```bash
git clone https://github.com/mirkobrombin/runtimezilla.git
cd runtimezilla
chmod +x runtimezilla
./runtimezilla --recipe <recipe> --output <output>
# e.g. ./runtimezilla --recipe my-runtime.yml --output my-runtime
```

With the above example, it will create a new runtime archive in the 
`my-runtime` directory, using the `my-runtime.yml` recipe.

### Recipe
A recipe is a YAML file that describes how to build a runtime, specifying
its ingredients (libraries, packages, etc.), and metadata (name, version,
description, etc.).

Find a full example in the `example.yml` file.

#### Packager
Each recipe defines a packager, which is the package manager used to install
the required packages to build the runtime. Currently the following packagers
are supported:
- apt
- aptitude
- dnf

you can add your own packager by creating a new yaml file in the `packagers`
directory.

### Output
The output is the directory where the runtime will be created.

