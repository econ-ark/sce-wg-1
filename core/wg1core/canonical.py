"""Strict YAML loading, the canonical serialization, and the hash that identifies a model.

A parameter file is YAML in a strict subset: no anchors, aliases, tags or merge keys, no repeated keys, no booleans, no
infinities or NaN. Null appears only where a validator admits it, which is a truncation bound's "no bound". Its hash is the SHA-256 of a canonical JSON serialization of the parsed values: keys sorted, no white space, every
number written as the shortest decimal that reads back to the same double. So `0.10` and `0.1` hash alike, as do `1`
and `1.0`, while two files that differ in any value differ in their hash.
"""

from __future__ import annotations

import hashlib
import json
import math

import yaml


class StrictYAMLError(ValueError):
    """The text uses a YAML feature the strict subset leaves out."""


class _StrictLoader(yaml.SafeLoader):
    """A safe loader that refuses a repeated key in any mapping."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise StrictYAMLError(f"repeated key {key!r} at line {key_node.start_mark.line + 1}")
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def load_strict(text: str):
    """Parse YAML text in the strict subset, or raise StrictYAMLError."""
    for token in yaml.scan(text):
        if isinstance(token, yaml.AnchorToken):
            raise StrictYAMLError(f"anchor at line {token.start_mark.line + 1}")
        if isinstance(token, yaml.AliasToken):
            raise StrictYAMLError(f"alias at line {token.start_mark.line + 1}")
        if isinstance(token, yaml.TagToken):
            raise StrictYAMLError(f"tag at line {token.start_mark.line + 1}")
        if isinstance(token, yaml.ScalarToken) and token.value == "<<":
            raise StrictYAMLError(f"merge key at line {token.start_mark.line + 1}")
    data = yaml.load(text, Loader=_StrictLoader)
    _check_values(data, "")
    return data


def _check_values(value, path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise StrictYAMLError(f"a key that is not a string at {path or '/'}: {key!r}")
            _check_values(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _check_values(item, f"{path}/{index}")
    elif value is None:
        return  # admitted only where a validator says so: a truncation bound's "no bound"
    elif isinstance(value, bool):
        raise StrictYAMLError(f"a boolean at {path or '/'}; the schemas use numbers, strings and null only")
    elif isinstance(value, float) and not math.isfinite(value):
        raise StrictYAMLError(f"an infinite or undefined number at {path or '/'}")
    elif not isinstance(value, (int, float, str)):
        raise StrictYAMLError(f"a value of type {type(value).__name__} at {path or '/'}")


def canonical_json(value) -> str:
    """The canonical serialization: sorted keys, no white space, every number as a double."""
    return json.dumps(_numbers_as_floats(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def _numbers_as_floats(value):
    if isinstance(value, dict):
        return {key: _numbers_as_floats(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_numbers_as_floats(item) for item in value]
    if isinstance(value, bool):
        raise StrictYAMLError("a boolean has no canonical form")
    if isinstance(value, (int, float)):
        return float(value)
    return value


def model_hash(value) -> str:
    """The SHA-256, in hexadecimal, of the canonical serialization."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
