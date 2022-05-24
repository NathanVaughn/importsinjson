from typing import Any, Type

import pytest

import jsonimport


@pytest.mark.parametrize(
    "source_data, key, value",
    [
        ({"key1": "value1"}, "key1", "value1"),
        ([1, 2, 3, 4, 5], "0", 1),
        ("abc", "0", "a"),
    ],
)
def test_get_key_pass(source_data: Any, key: str, value: Any) -> None:
    assert jsonimport._get_key(source_data, key) == value


@pytest.mark.parametrize(
    "source_data, key, error",
    [
        ({"key1": "value1"}, "key2", KeyError),
        ([1, 2, 3, 4], "a", ValueError),
        ([1, 2, 3, 4], "10", IndexError),
        ("abc", "5", IndexError),
        (True, "a", ValueError),
        (10, "a", ValueError),
    ],
)
def test_get_key_fail(source_data: Any, key: str, error: Type[Exception]) -> None:
    with pytest.raises(error):
        jsonimport._get_key(source_data, key)
