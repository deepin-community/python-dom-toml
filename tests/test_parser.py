# stdlib
from typing import Dict, Iterable, List, Type

# 3rd party
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
import dom_toml
from dom_toml import load
from dom_toml.decoder import TomlPureDecoder
from dom_toml.parser import TOML_TYPES, AbstractConfigParser, BadConfigError, construct_path


class PEP621Parser(AbstractConfigParser):
	"""
	Parser for :pep:`621` metadata from ``pyproject.toml``.
	"""

	def parse_description(self, config: Dict[str, TOML_TYPES]) -> str:
		"""
		Parse the `description <https://www.python.org/dev/peps/pep-0621/#description>`_ key.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		description = config["description"]
		self.assert_type(description, str, ["project", "description"])
		return description

	def parse_keywords(self, config: Dict[str, TOML_TYPES]) -> List[str]:
		"""
		Parse the `keywords <https://www.python.org/dev/peps/pep-0621/#keywords>`_ key.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		parsed_keywords = set()

		for idx, keyword in enumerate(config["keywords"]):
			self.assert_indexed_type(keyword, str, ["project", "keywords"], idx=idx)
			parsed_keywords.add(keyword)

		return sorted(parsed_keywords)

	def parse_classifiers(self, config: Dict[str, TOML_TYPES]) -> List[str]:
		"""
		Parse the `classifiers <https://www.python.org/dev/peps/pep-0621/#classifiers>`_ key.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		parsed_classifiers = set()

		for idx, keyword in enumerate(config["classifiers"]):
			self.assert_indexed_type(keyword, str, ["project", "classifiers"], idx=idx)
			parsed_classifiers.add(keyword)

		return sorted(parsed_classifiers)

	def parse_urls(self, config: Dict[str, TOML_TYPES]) -> Dict[str, str]:
		"""
		Parse the `urls <https://www.python.org/dev/peps/pep-0621/#urls>`_ table.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		parsed_urls = {}

		project_urls = config["urls"]

		self.assert_type(project_urls, dict, ["project", "urls"])

		for category, url in project_urls.items():
			self.assert_value_type(url, str, ["project", "urls", category])

			parsed_urls[category] = url

		return parsed_urls

	def parse_scripts(self, config: Dict[str, TOML_TYPES]) -> Dict[str, str]:
		"""
		Parse the `scripts <https://www.python.org/dev/peps/pep-0621/#entry-points>`_ table.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		scripts = config["scripts"]

		self.assert_type(scripts, dict, ["project", "scripts"])

		for name, func in scripts.items():
			self.assert_value_type(func, str, ["project", "scripts", name])

		return scripts

	def parse_gui_scripts(self, config: Dict[str, TOML_TYPES]) -> Dict[str, str]:
		"""
		Parse the `gui-scripts <https://www.python.org/dev/peps/pep-0621/#entry-points>`_ table.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		gui_scripts = config["gui-scripts"]

		self.assert_type(gui_scripts, dict, ["project", "gui-scripts"])

		for name, func in gui_scripts.items():
			self.assert_value_type(func, str, ["project", "gui-scripts", name])

		return gui_scripts

	def parse_entry_points(self, config: Dict[str, TOML_TYPES]) -> Dict[str, str]:
		"""
		Parse the `entry-points <https://www.python.org/dev/peps/pep-0621/#entry-points>`_ table.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""

		entry_points = config["entry-points"]

		self.assert_type(entry_points, dict, ["project", "entry-points"])

		for group, sub_table in entry_points.items():

			self.assert_value_type(sub_table, dict, ["project", "entry-points", group])

			for name, func in sub_table.items():
				self.assert_value_type(func, str, ["project", "entry-points", group, name])

		return entry_points

	def parse_dependencies(self, config: Dict[str, TOML_TYPES]) -> List[str]:
		"""
		Parse the
		`dependencies <https://www.python.org/dev/peps/pep-0621/#dependencies-optional-dependencies>`_ key.

		:param config: The unparsed TOML config for the ``[project]`` table.
		"""  # noqa: D400

		parsed_dependencies = set()

		for idx, keyword in enumerate(config["dependencies"]):
			self.assert_indexed_type(keyword, str, ["project", "dependencies"], idx=idx)
			parsed_dependencies.add(keyword)

		return sorted(parsed_dependencies)

	@property
	def keys(self) -> List[str]:
		"""
		The keys to parse from the TOML file.
		"""

		return [
				"name",
				"description",
				"keywords",
				"classifiers",
				"urls",
				"scripts",
				"gui-scripts",
				"dependencies",
				]


MINIMAL_CONFIG = '[project]\nname = "spam"\nversion = "2020.0.0"'

KEYWORDS = f"""\
{MINIMAL_CONFIG}
keywords = ["egg", "bacon", "sausage", "tomatoes", "Lobster Thermidor"]
"""

CLASSIFIERS = f"""\
{MINIMAL_CONFIG}
classifiers = [
  "Development Status :: 4 - Beta",
  "Programming Language :: Python"
]
"""

DEPENDENCIES = f"""\
{MINIMAL_CONFIG}
dependencies = [
  "httpx",
  "gidgethub[httpx]>4.0.0",
  "django>2.1; os_name != 'nt'",
  "django>2.0; os_name == 'nt'"
]
"""

URLS = f"""\
{MINIMAL_CONFIG}

[project.urls]
homepage = "example.com"
documentation = "readthedocs.org"
repository = "github.com"
changelog = "github.com/me/spam/blob/master/CHANGELOG.md"
"""

UNICODE = f"""\
{MINIMAL_CONFIG}
description = "Factory ⸻ A code generator 🏭"
authors = [{{name = "Łukasz Langa"}}]
"""


@pytest.mark.parametrize(
		"config, expects, match",
		[
				pytest.param(
						f'{MINIMAL_CONFIG}\nkeywords = [1, 2, 3, 4, 5]',
						TypeError,
						r"Invalid type for 'project.keywords\[0\]': expected <class 'str'>, got <class 'int'>",
						id="keywords_wrong_type"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\ndescription = [1, 2, 3, 4, 5]',
						TypeError,
						r"Invalid type for 'project.description': expected <class 'str'>, got <class 'list'>",
						id="description_wrong_type"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\ndescription = 12345',
						TypeError,
						r"Invalid type for 'project.description': expected <class 'str'>, got <class 'int'>",
						id="description_wrong_type"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\nclassifiers = [1, 2, 3, 4, 5]',
						TypeError,
						r"Invalid type for 'project.classifiers\[0\]': expected <class 'str'>, got <class 'int'>",
						id="classifiers_wrong_type"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\ndependencies = [1, 2, 3, 4, 5]',
						TypeError,
						r"Invalid type for 'project.dependencies\[0\]': expected <class 'str'>, got <class 'int'>",
						id="dependencies_wrong_type"
						),
				pytest.param(
						f'{MINIMAL_CONFIG}\nurls = {{foo = 1234}}',
						TypeError,
						r"Invalid value type for 'project.urls.foo': expected <class 'str'>, got <class 'int'>",
						id="urls_wrong_type"
						),
				]
		)
def test_parse_config_errors(config: str, expects: Type[Exception], match: str, tmp_pathplus: PathPlus):
	(tmp_pathplus / "pyproject.toml").write_clean(config)

	with pytest.raises(expects, match=match):
		PEP621Parser().parse(load(tmp_pathplus / "pyproject.toml")["project"])


@pytest.mark.parametrize(
		"toml_config",
		[
				pytest.param(MINIMAL_CONFIG, id="minimal"),
				pytest.param(f'{MINIMAL_CONFIG}\ndescription = "Lovely Spam! Wonderful Spam!"', id="description"),
				pytest.param(KEYWORDS, id="keywords"),
				pytest.param(CLASSIFIERS, id="classifiers"),
				pytest.param(DEPENDENCIES, id="dependencies"),
				pytest.param(URLS, id="urls"),
				pytest.param(UNICODE, id="unicode"),
				]
		)
def test_parse_valid_config(
		toml_config: str,
		tmp_pathplus: PathPlus,
		advanced_data_regression: AdvancedDataRegressionFixture,
		):
	(tmp_pathplus / "pyproject.toml").write_clean(toml_config)
	config = PEP621Parser().parse(dom_toml.loads(toml_config, decoder=TomlPureDecoder)["project"])
	advanced_data_regression.check(config)


@pytest.mark.parametrize(
		"path, expected",
		[
				(["foo"], "foo"),
				(iter(["foo"]), "foo"),
				(("foo", ), "foo"),
				(["foo", "bar"], "foo.bar"),
				(iter(["foo", "bar"]), "foo.bar"),
				(("foo", "bar"), "foo.bar"),
				(["foo", "hello world"], 'foo."hello world"'),
				(iter(["foo", "hello world"]), 'foo."hello world"'),
				(("foo", "hello world"), 'foo."hello world"'),
				]
		)
def test_construct_path(path: Iterable[str], expected: str):
	assert construct_path(path) == expected


def test_badconfigerror_documentation():

	with pytest.raises(BadConfigError, match="Hello World") as e:
		raise BadConfigError("Hello World", documentation="This is the documentation")

	assert e.value.documentation == "This is the documentation"
