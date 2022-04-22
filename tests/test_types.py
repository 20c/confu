import pytest

from confu.types import TimeDuration


def test_TimeDuration():
    assert 180122.002 == TimeDuration("2d 2h 2m 2s 2ms")

    with pytest.raises(ValueError):
        TimeDuration("2x 2h 2m 2s 2ms")
    with pytest.raises(ValueError):
        TimeDuration("2")
    with pytest.raises(ValueError):
        TimeDuration("s")
    with pytest.raises(ValueError):
        TimeDuration("xyz")
