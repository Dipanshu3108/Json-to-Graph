import json

from app.api.repair import _extract_json


def test_extract_json_plain() -> None:
    assert _extract_json('{"a": 1}') == '{"a": 1}'


def test_extract_json_with_markdown_fences() -> None:
    text = "```json\n{\"a\": 1}\n```"
    assert _extract_json(text) == '{"a": 1}'


def test_extract_json_with_prose() -> None:
    text = "Here is the JSON:\n{\"a\": 1}\nHope this helps!"
    assert _extract_json(text) == '{"a": 1}'


def test_extract_json_array() -> None:
    assert _extract_json("```[1, 2, 3]```") == "[1, 2, 3]"


def test_extract_json_no_json() -> None:
    assert _extract_json("No JSON here") is None


def test_extracted_json_is_parseable() -> None:
    text = '{"datasets":[{"label":"S1","data":[{"x":1,"y":2}]}]}\nGENERATED:\n- point 0: y generated\nCHANGES: added y'
    extracted = _extract_json(text)
    assert extracted is not None
    assert json.loads(extracted) == {"datasets": [{"label": "S1", "data": [{"x": 1, "y": 2}]}]}
