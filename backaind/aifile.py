"""Functions to read and validate Aifiles."""
import json

MAX_AIFILEVERSION = 1

class InvalidAifileError(Exception):
    """The Aifile has invalid or missing data."""

def validate_aifile(aifile):
    """Validate an Aifile for required fields and correct version."""
    required_fields = ['name', 'aifileversion', 'chain']

    for field in required_fields:
        if field not in aifile:
            raise InvalidAifileError(f'Missing field in aifile: {field}')

    if aifile['aifileversion'] > MAX_AIFILEVERSION:
        raise InvalidAifileError('This aifile requires a newer version of ownAI.')

def read_aifile_from_path(aifile_path):
    """Read an Aifile from the given path and validate its data. Return the Aifile as dictionary."""
    with open(aifile_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    validate_aifile(data)
    return data
