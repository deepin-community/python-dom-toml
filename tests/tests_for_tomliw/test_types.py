# stdlib
from decimal import Decimal

# this package
import dom_toml


def test_decimal():
	obj = {
			"decimal-0": Decimal(0),
			"decimal-pi": Decimal("3.14159"),
			"decimal-inf": Decimal("inf"),
			"decimal-minus-inf": Decimal("-inf"),
			"decimal-nan": Decimal("nan"),
			}
	assert (
			dom_toml.dumps(obj) == """\
decimal-0 = 0
decimal-pi = 3.14159
decimal-inf = inf
decimal-minus-inf = -inf
decimal-nan = nan
"""
			)


def test_tuple():
	obj = {"empty-tuple": (), "non-empty-tuple": (1, (2, 3))}
	assert (dom_toml.dumps(obj) == """\
empty-tuple = []
non-empty-tuple = [ 1, [ 2, 3,],]
""")
