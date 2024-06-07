# stdlib
from typing import Any, Dict

# 3rd party
import pytest
from coincidence import AdvancedFileRegressionFixture

# this package
import dom_toml
from dom_toml import TomlEncoder, dumps

PEP621 = {
		"name": "greppy",
		"version": "0.0.0",
		"description": "Recursively grep over Python files in the files in the given directory 🔎",
		"readme": "README.rst",
		"keywords": [],
		"authors": [{"email": "dominic@davis-foster.co.uk", "name": "Dominic Davis-Foster"}],
		"dynamic": ["requires-python", "classifiers", "dependencies"],
		"license": {"file": "LICENSE"},
		}

array_of_tables = {"key": [
		{"dict1": "dict1_value"},
		{"dict2": "dict2_value"},
		{"dict3": "dict3_value"},
		]}


@pytest.mark.parametrize(
		"data",
		[
				pytest.param({"dotted.key": "string"}, id="dotted.key"),
				pytest.param({"key": "☃🚀📦"}, id="unicode"),
				pytest.param({"key": "string"}, id="string_value"),
				pytest.param({"key": ["list", 'double ""', "single ''"]}, id="list_value"),
				pytest.param({
						"key": [
								"insure",
								"auspicious",
								"neglect",
								"craven",
								"match",
								"worship",
								"wave",
								"languid",
								"bad",
								"news",
								"flashy",
								"recall",
								"mother",
								"festive",
								"cup",
								'double ""',
								"single ''",
								"mixed '\"",
								"newline\n",
								"formfeed\f",
								"carriage_return\r",
								"backslash\\",
								"backspace\b",
								"tab\t",
								]
						},
								id="long_list"),
				pytest.param({"key": {"dict": "dict_value"}}, id="dict_value"),
				pytest.param(array_of_tables, id="array_of_tables"),
				pytest.param({"section": {"key": "string"}}, id="section_string_value"),
				pytest.param({"section": {"key": ["list"]}}, id="section_list_value"),
				pytest.param({"project": PEP621}, id="pep621"),
				]
		)
def test_encoder(data: Dict[str, Any], advanced_file_regression: AdvancedFileRegressionFixture):
	as_toml = dumps(data, encoder=TomlEncoder())
	advanced_file_regression.check(as_toml, extension=".toml")
	assert dom_toml.loads(as_toml) == data


@pytest.mark.parametrize(
		"data",
		[
				pytest.param({"key": ("list", )}, id="tuple_value"),
				pytest.param({"section": {"key": ("list", )}}, id="section_tuple_value"),
				]
		)
def test_encoder_tuples(data: Dict[str, Any], advanced_file_regression: AdvancedFileRegressionFixture):
	as_toml = dumps(data, encoder=TomlEncoder())
	advanced_file_regression.check(as_toml, extension=".toml")


def test_encoder_inline_table(advanced_file_regression: AdvancedFileRegressionFixture):
	source = "[project]\nreadme = {file = 'README.rst', content-type = 'text/x-rst'}\n"
	advanced_file_regression.check(
			dom_toml.dumps(dom_toml.loads(source), encoder=TomlEncoder(preserve=True)), extension=".toml"
			)


def test_encoder_inline_table_nested(advanced_file_regression: AdvancedFileRegressionFixture):
	source = "[project]\nreadme = {file = 'README.rst', nested = {content-type = 'text/x-rst'}}\n"
	advanced_file_regression.check(
			dom_toml.dumps(dom_toml.loads(source), encoder=TomlEncoder(preserve=True)), extension=".toml"
			)
	dom_toml.loads(dom_toml.dumps(dom_toml.loads(source), encoder=TomlEncoder(preserve=True)))
