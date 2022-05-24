import os
from typing import Any

import commentjson
import pyjson5
import pytest

import jsonimport

FILES_DIR = os.path.join(os.path.dirname(__file__), "files")
TEST_CASES = (
    [
        (
            "valid_key_basic.json",
            {
                "key1": "value1",
                "key2": "value2",
                "key3": {"key4": "value4", "key5": "value5"},
            },
        ),
        (
            "valid_key_path1.json",
            {"key4": "value4", "key5": "value5"},
        ),
        (
            "valid_key_path2.json",
            {"key4": "value4", "key5": "value5"},
        ),
        (
            "valid_key_path3.json",
            {"key4": "value4", "key5": "value5"},
        ),
        (
            "valid_key_path4.json",
            {"key4": "value4", "key5": "value5"},
        ),
        (
            "valid_value_str_basic.json",
            {
                "strkey": {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": {"key4": "value4", "key5": "value5"},
                }
            },
        ),
        (
            "valid_value_str_path.json",
            {
                "strkey": "value1",
            },
        ),
        (
            "valid_value_list_basic.json",
            {
                "listkey": [
                    {
                        "key1": "value1",
                        "key2": "value2",
                        "key3": {"key4": "value4", "key5": "value5"},
                    }
                ]
            },
        ),
        (
            "valid_value_list_path.json",
            {"listkey": ["value1", "value2"]},
        ),
        (
            "valid_key_nested.json",
            {"key4": "value4", "key5": "value5"},
        ),
    ],
)


@pytest.mark.parametrize("filename, data", *TEST_CASES)
def test_loads(filename: str, data: Any) -> None:
    cwd = os.getcwd()
    # need to cd into files direcotry to be in the right working directory
    os.chdir(FILES_DIR)

    with open(os.path.join(FILES_DIR, filename), "r") as fp:
        try:
            assert jsonimport.loads(fp.read()) == data
        finally:
            os.chdir(cwd)


@pytest.mark.parametrize("filename, data", *TEST_CASES)
def test_load(filename: str, data: Any) -> None:
    with open(os.path.join(FILES_DIR, filename), "r") as fp:
        assert jsonimport.load(fp) == data


def test_load_cwd_fallback() -> None:
    # test loading a file falling back to the current working directory
    with open(os.path.join(FILES_DIR, "valid_key_basic_cwd.json"), "r") as fp:
        assert jsonimport.load(fp) == {
            "key1": "value1",
            "key2": "value2",
            "key3": {"key4": "value4", "key5": "value5"},
        }


def test_file_not_found() -> None:
    with open(os.path.join(FILES_DIR, "invalid_key_basic.json"), "r") as fp:
        assert jsonimport.load(fp) == {"$import": "notreal.json"}

    with open(os.path.join(FILES_DIR, "invalid_key_basic.json"), "r") as fp:
        with pytest.raises(FileNotFoundError):
            jsonimport.load(fp, strict=True)


def test_key_not_found() -> None:
    with open(os.path.join(FILES_DIR, "invalid_key_path.json"), "r") as fp:
        assert jsonimport.load(fp) == {"$import": "imported.json:/notreal/"}

    with open(os.path.join(FILES_DIR, "invalid_key_path.json"), "r") as fp:
        with pytest.raises(KeyError):
            jsonimport.load(fp, strict=True)


def test_commentjson() -> None:
    with open(os.path.join(FILES_DIR, "valid_key_inline.jsonc"), "r") as fp:
        jsonimport._load_fn = commentjson.load
        assert jsonimport.load(fp) == {
            "key1": "value1",
            "key2": "value2",
            "key3": {"key4": "value4", "key5": "value5"},
        }

def test_pyjson5() -> None:
    with open(os.path.join(FILES_DIR, "valid_key_multiline.jsonc"), "r") as fp:
        jsonimport._load_fn = pyjson5.load
        assert jsonimport.load(fp) == {
            "key1": "value1",
            "key2": "value2",
            "key3": {"key4": "value4", "key5": "value5"},
        }
