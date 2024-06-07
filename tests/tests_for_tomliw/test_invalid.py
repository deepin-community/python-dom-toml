# stdlib
from datetime import time, timezone

# 3rd party
import pytest

# this package
import dom_toml


def test_invalid_type_nested():
	with pytest.raises(TypeError):
		dom_toml.dumps({"bytearr": bytearray()})


def test_invalid_time():
	offset_time = time(23, 59, 59, tzinfo=timezone.utc)
	with pytest.raises(ValueError, match="TOML does not support offset times"):
		dom_toml.dumps({"offset time": offset_time})
