import json
import os
from typing import IO, Any, Optional

try:
    import commentjson

    _load_fn = commentjson.load
    _loads_fn = commentjson.loads
except ImportError:
    try:
        import pyjson5

        _load_fn = pyjson5.load
        _loads_fn = pyjson5.loads
    except ImportError:
        _load_fn = json.load
        _loads_fn = json.loads


PREFIX = "$import"

# use builtin json module directly
dump = json.dump
dumps = json.dumps


def _get_key(source_data: Any, key: str) -> Any:
    """
    Get the value of ``key`` from ``source_data``.
    """
    if isinstance(source_data, dict):
        # dicts in JSON can only have strings as keys
        return source_data[key]

    elif isinstance(source_data, (list, str)):
        return source_data[int(key)]

    else:
        raise ValueError(f"{key} is not a valid key for {source_data}")


def _import(
    import_string: str, source_filename: Optional[str], strict: bool, **kwargs
) -> Any:
    """
    Take an import string, parse it, and import the file.
    Import string looks like the following:
    $import:filename.json:/path/to/value
    """
    import_string_split = import_string.split(":")

    # get the path to the file
    import_filepath = import_string_split[1]

    # if the given file path is not absolute
    if not os.path.isabs(import_filepath):
        # if we're parsing data from a string, use the current working directory
        if source_filename is None:
            import_filepath = os.path.join(os.getcwd(), import_filepath)
        elif os.path.isfile(
            os.path.join(os.path.dirname(source_filename), import_filepath)
        ):
            # otherwise, use the directory of the source file
            import_filepath = os.path.join(
                os.path.dirname(source_filename), import_filepath
            )
        else:
            # fall back to working directory
            import_filepath = os.path.join(os.getcwd(), import_filepath)

    # if the file does not exist, return original value
    if not os.path.isfile(import_filepath):
        if not strict:
            return import_string

        raise FileNotFoundError(f"{import_filepath} could not be found")

    # import the file
    with open(import_filepath, "r", encoding="utf-8") as fp:
        import_data = load(fp, strict=strict, **kwargs)  # type: ignore

    # no key path given
    if len(import_string_split) == 2:
        return import_data

    # drill down to grab specificed key
    for key in import_string_split[2].split("/"):
        # skip keys that are empty strings
        if key != "":
            try:
                import_data = _get_key(import_data, key)
            except Exception as e:
                if strict:
                    raise e

                return import_string

    return import_data


def _import_recursive(
    json_data: Any, source_filename: Optional[str], strict: bool, **kwargs
) -> Any:
    """
    Recursively import from other JSON files.
    """
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            # process a key which which is the prefix
            if isinstance(key, str) and key == PREFIX and isinstance(value, str):
                import_data = _import(
                    f"{key}:{value}", source_filename, strict, **kwargs
                )

                if isinstance(import_data, dict):
                    json_data = {**json_data, **import_data}
                    del json_data[key]
            # otherwise, recurse
            else:
                json_data[key] = _import_recursive(
                    value, source_filename, strict, **kwargs
                )

        return json_data

    elif isinstance(json_data, list):
        # iterate over list elements
        return [
            _import_recursive(item, source_filename, strict, **kwargs)
            for item in json_data
        ]

    elif isinstance(json_data, str) and json_data.startswith(f"{PREFIX}:"):
        # process a value which starts with the prefix
        return _import(json_data, source_filename, strict, **kwargs)

    else:
        return json_data


def load(fp: IO, strict: bool = False, **kwargs) -> Any:
    """
    Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
    a JSON document) to a Python object, processing imports.
    """
    original_data = _load_fn(fp, **kwargs)
    return _import_recursive(original_data, getattr(fp, "name", None), strict, **kwargs)


def loads(*args, strict: bool = False, **kwargs) -> Any:
    """
    Deserialize ``s`` (a ``str`` instance containing a JSON document)
    to a Python object, processing imports.
    """
    original_data = _loads_fn(*args, **kwargs)
    return _import_recursive(original_data, None, strict, **kwargs)
