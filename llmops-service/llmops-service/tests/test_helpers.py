from __future__ import annotations


from app.utils.helpers import dump_compact, normalize_whitespace


def test_dump_compact_dict():
    result = dump_compact({"key": "value", "num": 42})
    assert '"key":"value"' in result
    assert '"num":42' in result


def test_dump_compact_empty_dict():
    assert dump_compact({}) == "{}"


def test_dump_compact_none_value():
    result = dump_compact(None)
    assert result == "null"


def test_dump_compact_list():
    result = dump_compact([1, 2, 3])
    assert result == "[1,2,3]"


def test_dump_compact_no_spaces():
    result = dump_compact({"a": 1, "b": 2})
    assert " " not in result


def test_normalize_whitespace_strips_extra_spaces():
    result = normalize_whitespace("  hello   world  ")
    assert result == "hello world"


def test_normalize_whitespace_collapses_newlines():
    result = normalize_whitespace("line one\n  line two\n")
    assert result == "line one line two"


def test_normalize_whitespace_single_word():
    assert normalize_whitespace("word") == "word"
