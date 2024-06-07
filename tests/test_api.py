# From https://github.com/uiri/toml
#
# The MIT License
#
# Copyright 2013-2019 William Pearson
# Copyright 2015-2016 Julien Enselme
# Copyright 2016 Google Inc.
# Copyright 2017 Samuel Vasko
# Copyright 2017 Nate Prewitt
# Copyright 2017 Jack Evans
# Copyright 2019 Filippo Broggini
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# stdlib
import copy
import datetime
import os
import pathlib
import sys
from decimal import Decimal
from typing import Any, Dict

# 3rd party
import pytest

# this package
import dom_toml
from dom_toml import dump, dumps, load, loads
from dom_toml.decoder import InlineTableDict
from dom_toml.encoder import TomlArraySeparatorEncoder, TomlEncoder, TomlNumpyEncoder, TomlPathlibEncoder

test_toml = os.path.abspath(os.path.join(__file__, "..", "test.toml"))

TEST_STR = """
[a]\r
b = 1\r
c = 2
"""

TEST_DICT: Dict[str, Any] = {'a': {'b': 1, 'c': 2}}


def test_bug_196():
	d = datetime.datetime.now()
	bug_dict = {'x': d}
	round_trip_bug_dict: Dict[str, Any] = loads(dumps(bug_dict))
	assert round_trip_bug_dict == bug_dict
	assert round_trip_bug_dict['x'] == bug_dict['x']


# def test__dict():


def test_inline_dict():

	class TestDict(InlineTableDict):
		pass

	t = copy.deepcopy(TEST_DICT)
	t['d'] = TestDict()
	t['d']['x'] = "abc"
	o: Dict[str, Any] = loads(dumps(t, encoder=TomlEncoder(preserve=True)))
	assert o == loads(dumps(o, encoder=TomlEncoder(preserve=True)))


@pytest.mark.parametrize(
		"encoder_cls",
		[
				pytest.param(TomlArraySeparatorEncoder, id="type"),
				pytest.param(TomlArraySeparatorEncoder(), id="instance"),
				pytest.param(TomlArraySeparatorEncoder(separator=",\t"), id="instance_tab"),
				]
		)
def test_array_sep(encoder_cls):
	d = {'a': [1, 2, 3]}
	o: Dict[str, Any] = loads(dumps(d, encoder=encoder_cls))
	assert o == loads(dumps(o, encoder=encoder_cls))


def test_numpy_floats():
	np = pytest.importorskip("numpy")

	encoder = TomlNumpyEncoder()
	d = {'a': np.array([1, .3], dtype=np.float64)}
	o: Dict[str, Any] = loads(dumps(d, encoder=encoder))
	assert o == loads(dumps(o, encoder=encoder))

	d = {'a': np.array([1, .3], dtype=np.float32)}
	o = loads(dumps(d, encoder=encoder))
	assert o == loads(dumps(o, encoder=encoder))

	d = {'a': np.array([1, .3], dtype=np.float16)}
	o = loads(dumps(d, encoder=encoder))
	assert o == loads(dumps(o, encoder=encoder))


def test_numpy_ints():
	np = pytest.importorskip("numpy")

	encoder = TomlNumpyEncoder()
	d = {'a': np.array([1, 3], dtype=np.int64)}
	o: Dict[str, Any] = loads(dumps(d, encoder=encoder))
	assert o == loads(dumps(o, encoder=encoder))

	d = {'a': np.array([1, 3], dtype=np.int32)}
	o = loads(dumps(d, encoder=encoder))
	assert o == loads(dumps(o, encoder=encoder))

	d = {'a': np.array([1, 3], dtype=np.int16)}
	o = loads(dumps(d, encoder=encoder))
	assert o == loads(dumps(o, encoder=encoder))


# @pytest.mark.parametrize(
# 		"encoder_cls",
# 		[
# 				pytest.param(toml_ordered.TomlOrderedEncoder, id="type"),
# 				pytest.param(toml_ordered.TomlOrderedEncoder(), id="instance"),
# 				]
# 		)
# @pytest.mark.parametrize(
# 		"decoder_cls",
# 		[
# 				pytest.param(toml_ordered.TomlOrderedDecoder, id="type"),
# 				pytest.param(toml_ordered.TomlOrderedDecoder(), id="instance"),
# 				]
# 		)
# def test_ordered(encoder_cls, decoder_cls):
# 	o: Dict[str, Any] = loads(dumps(TEST_DICT, encoder=encoder_cls), decoder=decoder_cls)
# 	assert o == loads(dumps(TEST_DICT, encoder=encoder_cls), decoder=decoder_cls)


def test_tuple():
	d = {'a': (3, 4)}
	o: Dict[str, Any] = loads(dumps(d))
	assert o == loads(dumps(o))


def test_decimal():
	PLACES = Decimal(10)**-4

	d = {'a': Decimal("0.1")}
	o: Dict[str, Any] = loads(dumps(d))
	assert o == loads(dumps(o))
	assert Decimal(o['a']).quantize(PLACES) == d['a'].quantize(PLACES)

	with pytest.raises(TypeError):
		loads(2)  # type: ignore[arg-type]

	if sys.version_info < (3, 12):
		error_msg = "expected str, bytes or os.PathLike object, not int"
	else:
		error_msg = "argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'int'"

	with pytest.raises(TypeError, match=error_msg):
		load(2)  # type: ignore[arg-type]

	if sys.version_info < (3, 12):
		error_msg = "expected str, bytes or os.PathLike object, not list"
	else:
		error_msg = "argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'list'"

	with pytest.raises(TypeError, match=error_msg):
		load([])  # type: ignore[arg-type]

	if sys.version_info < (3, 12):
		error_msg = "argument should be a str object or an os.PathLike object returning str, not <class 'bytes'>"
	else:
		error_msg = "argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'bytes"

	with pytest.raises(TypeError, match=error_msg):
		load(b"test.toml")  # type: ignore[arg-type]


class FakeFile:

	def __init__(self):
		self.written = ''

	def write(self, s):
		self.written += s

	def read(self):
		return self.written


def test_dump(tmp_pathplus):
	dump(TEST_DICT, tmp_pathplus / "file.toml")
	dump(load(tmp_pathplus / "file.toml"), tmp_pathplus / "file2.toml")
	dump(load(tmp_pathplus / "file2.toml"), tmp_pathplus / "file3.toml")

	assert (tmp_pathplus / "file2.toml").read_text() == (tmp_pathplus / "file3.toml").read_text()


def test_paths():
	load(test_toml)
	load(pathlib.Path(test_toml))


def test_nonexistent():
	load(test_toml)

	with pytest.raises(FileNotFoundError, match=r"No such file or directory: .*'nonexist.toml'\)?"):
		load("nonexist.toml")


def test_commutativity():
	o: Dict[str, Any] = loads(dumps(TEST_DICT))
	assert o == loads(dumps(o))


@pytest.mark.parametrize(
		"encoder_cls", [
				pytest.param(TomlPathlibEncoder, id="type"),
				pytest.param(TomlPathlibEncoder(), id="instance"),
				]
		)
def test_pathlib(encoder_cls):
	o = {"root": {"path": pathlib.Path("/home/edgy")}}
	sep = "\\\\" if os.sep == '\\' else '/'
	test_str = f"""[root]
path = "{sep}home{sep}edgy"
"""
	assert test_str == dumps(o, encoder=encoder_cls)
	dom_toml.loads(test_str)


def test_deepcopy_timezone():
	o: Dict[str, Any] = loads("dob = 1979-05-24T07:32:00-08:00")
	o2: Dict[str, Any] = copy.deepcopy(o)
	assert o2["dob"] == o["dob"]
	assert o2["dob"] is not o["dob"]
