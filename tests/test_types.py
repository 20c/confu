import pytest

from confu.types import TimeDuration


def test_TimeDuration_parse_string():
    assert 63295322.002 == TimeDuration.parse_string("2y 2d 2h 2m 2s 2ms")
    with pytest.raises(ValueError):
        TimeDuration.parse_string("2x 2h 2m 2s 2ms")
    with pytest.raises(ValueError):
        TimeDuration.parse_string("2sm")
    with pytest.raises(ValueError):
        TimeDuration.parse_string("s")
    with pytest.raises(ValueError):
        TimeDuration.parse_string("xyz")


def test_TimeDuration():
    assert 63295322.002 == TimeDuration("2y 2d 2h 2m 2s 2ms")
    assert 180122.002 == TimeDuration("180122.002")
    assert 180122.002 == TimeDuration(180122.002)
    assert 180122 == TimeDuration(180122)

    with pytest.raises(TypeError):
        TimeDuration({})
    with pytest.raises(ValueError):
        TimeDuration.parse_string("xyz")
