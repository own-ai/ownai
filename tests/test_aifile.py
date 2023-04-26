"""Test loading and validation of aifiles."""
import pytest

from backaind.aifile import validate_aifile, read_aifile_from_path, InvalidAifileError

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

def test_read_aifile_from_path_returns_aifile():
    """Test if reading an aifile from a file works."""
    aifile = read_aifile_from_path('examples/huggingface_hub/OpenAssistant_SFT-4_12B.aifile')
    assert 'OpenAssistant' in aifile['name']
