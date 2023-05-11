"""Functions to read and validate Aifiles."""
import json

MAX_AIFILEVERSION = 1


class InvalidAifileError(Exception):
    """The Aifile has invalid or missing data."""


def validate_aifile(aifile):
    """Validate an Aifile for required fields and correct version."""
    required_fields = ["name", "aifileversion", "chain"]
    allowed_input_keys = ["input_text", "input_knowledge"]

    for field in required_fields:
        if field not in aifile:
            raise InvalidAifileError(f"Missing field in aifile: {field}")

    for input_key in get_input_keys(aifile):
        if input_key not in allowed_input_keys:
            raise InvalidAifileError(f"Unknown input key: {input_key}")

    if aifile["aifileversion"] > MAX_AIFILEVERSION:
        raise InvalidAifileError("This aifile requires a newer version of ownAI.")


def get_input_keys(aifile):
    """Get all input keys for an aifile."""

    def iterate_json_key_values(json_obj, key_prefix=""):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                new_key_prefix = f"{key_prefix}.{key}" if key_prefix else key
                if isinstance(value, (dict, list)):
                    yield from iterate_json_key_values(value, new_key_prefix)
                else:
                    yield (new_key_prefix, value)
        elif isinstance(json_obj, list):
            for index, value in enumerate(json_obj):
                new_key_prefix = f"{key_prefix}[{index}]"
                if isinstance(value, (dict, list)):
                    yield from iterate_json_key_values(value, new_key_prefix)
                else:
                    yield (new_key_prefix, value)

    input_keys = set()
    for key, value in iterate_json_key_values(aifile):
        if ("input_key" in key or "input_variables" in key) and value.startswith(
            "input_"
        ):
            input_keys.add(value)
    return input_keys


def read_aifile_from_path(aifile_path):
    """Read an Aifile from the given path and validate its data. Return the Aifile as dictionary."""
    with open(aifile_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    validate_aifile(data)
    return data
