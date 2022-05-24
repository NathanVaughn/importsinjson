# ImportsInJSON

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub license](https://img.shields.io/github/license/NathanVaughn/importsinjson)](https://github.com/NathanVaughn/importsinjson/blob/master/LICENSE)
[![PyPi versions](https://img.shields.io/pypi/pyversions/importsinjson)](https://pypi.org/project/importsinjson)
[![PyPi downloads](https://img.shields.io/pypi/dm/importsinjson)](https://pypi.org/project/importsinjson)

Python JSON Import Library

---

ImportsInJSON is an easy way to allow Python to load JSON files that import data
from other JSON files. This is very helpful for splitting up large JSON files
into smaller chunks that can still be combined.

## Installation

ImportsInJSON requires Python 3.7+.

```bash
pip install importsinjson
```

If you'd like to support loading JSON files with comments, either add
the [`commentjson`](https://pypi.org/project/commentjson/) or
[`pyjson5`](https://pypi.org/project/pyjson5/) extra when installing.

```bash
pip install importsinjson[commentjson]
# or
pip install importsinjson[pyjson5]
```

## Usage

In your Python code, `import importsinjson` is a drop-in replacement for the
[`json`](https://docs.python.org/3/library/json.html) module.

In your JSON document, there are 2 ways to import data from other JSON files.

The first way is to simply have a key called `$import` with a string value
that points to another file. Let's say you have a JSON file `a.json`:

```json
{
  "name": "John Doe",
  "age": 30,
  "$import": "b.json"
}
```

and

```json
{
  "profession": "Engineer"
}
```

Running `importsinjson.load('a.json')` will return the following:

```json
{
  "name": "John Doe",
  "age": 30,
  "profession": "Engineer"
}
```

This does observe Python's dictionary merging rules, so any keys in the imported
JSON file that are also in the original document will replace the values in the
original document.

The second way to import data is to have a string value that starts with `$import:`
and has the path to the file to import. Modifying the example from before, `a.json`
would become

```json
{
  "name": "John Doe",
  "age": 30,
  "profession": "$import:b.json"
}
```

However this would load the following:

```json
{
  "name": "John Doe",
  "age": 30,
  "profession": {
    "profession": "Engineer"
  }
}
```

To prevent duplicate keys like this, you can add another `:` after the file path,
and provide a path to the key in the imported file to use.

```json
{
  "name": "John Doe",
  "age": 30,
  "profession": "$import:b.json:/profession/"
}
```

This value can be anywhere in the JSON document, including in a list:

```json
{
  "name": "John Doe",
  "age": 30,
  "professions": ["$import:b.json", "$import:c.json"]
}
```

## Options

Depending on the JSON parsing backend selected, options do vary.
However, for all backends, the following options are available:

- `strict`: Defaults to `False`. If `True`, will raise a `FileNotFoundError`
  if the imported filepath cannot be found. Additionally, if the specified key/index
  could not be found, the `KeyError`, `IndexError`, etc will be raised. If `False`,
  the original value will be kept instead.

### Default

The default JSON parsing backend is the Python standard library `json` module.
All normal options for this can be used.

### CommentJSON

[Homepage](https://commentjson.readthedocs.io/en/latest/)

```bash
pip install importsinjson[commentjson]
```

If installed, `commentjson` will be used as the JSON parsing backend.
This is a pure-Python implementation that strips comments from JSON data before
handing them to the `json` module. This also supports all options of the `json` module.
However, it does not support multi-line comments.

### PyJSON5

[Homepage](https://pyjson5.readthedocs.io/en/latest/)

```bash
pip install importsinjson[pyjson5]
```

Lastly, if installed, `pyjson5` will be used as the JSON parsing backend.
This is a Cython implementation that loads JSON data with comments. This is the most
restrictive backend, with very basic options.
See [here](https://pyjson5.readthedocs.io/en/latest/decoder.html#pyjson5.load)
When using this, you may need to explictly add `encoding="utf-8"` to the `load` and
`loads` functions.

If for some reason you want to change the prefix used to import data, you can set
that like so:

```python
import importsinjson
importsinjson.PREFIX = "$newimportsymbol"
```

## Gotchas

Using the `load` function is much preferred over the `loads` function.
This is because with a file handle, the path of the file can be used as an additional
search directory when looking for imported files.

With `load` imported file paths can be either:

- absolute
- relative to the parent file
- relative to the current working directory

With `loads` imported file paths can only be:

- absolute
- relative to the current working directory

Additionally, this module also works recursively, so make sure not to create an
infinite loop.
