"""Test loading and validation of aifiles."""
import pytest

from backaind.aifile import (
    get_input_keys,
    read_aifile_from_path,
    validate_aifile,
    InvalidAifileError
)

@pytest.mark.parametrize('aifile', (
    {},
    {'name': 'test'},
    {'aifileversion': 1},
    {'chain': {}},
    {'name': 'test', 'aifileversion': 1},
    {'name': 'test', 'chain': {}},
    {'aifileversion': 1, 'chain': {}},
))
def test_validate_aifile_raises_on_missing_fields(aifile):
    """Test if the validation complains on missing fields."""
    with pytest.raises(InvalidAifileError) as error:
        validate_aifile(aifile)

    assert 'Missing field' in str(error.value)

def test_validate_aifile_raises_on_newer_aifileversion():
    """Test if the validation complains if the aifile version is too new."""
    with pytest.raises(InvalidAifileError) as error:
        validate_aifile({'name': 'test', 'aifileversion': 2, 'chain': {}})

    assert 'This aifile requires a newer version of ownAI.' in str(error.value)

def test_validate_aifile_raises_on_unknown_input_keys():
    """Test if the validation complains on unknown input types."""
    with pytest.raises(InvalidAifileError) as error:
        validate_aifile({
            'name': 'test',
            'aifileversion': 1,
            'chain': { 'input_key': 'input_money' }
        })

    assert 'Unknown input key' in str(error.value)

def test_get_input_keys_always_returns_set():
    """Test if get_input_keys always returns a (possibly empty) set."""
    assert get_input_keys(None) == set()

def test_get_input_keys_returns_nested_inputs():
    """Test if get_input_keys returns nested inputs and only inputs."""
    aifile = {
        'chain': {
            'nested_list': [
                {
                    'chain1': {
                        'input_key': 'input_a'
                    }
                },
                {
                    'chain2': {
                        'input_variables': ['input_b', 'input_c', 'not_an_input']
                    }
                }
            ]
        }
    }
    assert get_input_keys(aifile) == {'input_a', 'input_b', 'input_c'}

def test_read_aifile_from_path_returns_aifile():
    """Test if reading an aifile from a file works."""
    aifile = read_aifile_from_path('examples/huggingface_hub/OpenAssistant_SFT-4_12B.aifile')
    assert 'OpenAssistant' in aifile['name']
