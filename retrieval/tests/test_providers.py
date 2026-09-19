import pytest

from providers import get_provider


def test_get_provider_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unknown embedding provider"):
        get_provider("bogus")
