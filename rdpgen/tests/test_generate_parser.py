import pytest

from pytest_bdd import given, scenario, then, when, parsers
from pathlib import Path
import os
import tempfile
import click
from click.testing import CliRunner
import subprocess
from rdpgen.cli import cli

GRAMMAR_DIR = Path(os.path.realpath(__file__)).parent / "data" / "grammars"


@pytest.fixture
def grammar():
    pass


@pytest.fixture
def directory():
    pass


@pytest.fixture
def file():
    pass


@pytest.fixture
def return_code():
    pass


@scenario("features/generate_parser.feature", "Parser Accepts Valid Input")
def test_parser_accepts_valid_input():
    """Parser Accepts Valid Input."""
    pass


@scenario("features/generate_parser.feature", "Parser Rejects Invalid Input")
def test_parser_rejects_invalid_input():
    """Parser Rejects Invalid Input."""
    pass


@given(parsers.parse("I have a grammar {name}"), target_fixture="grammar")
def i_have_a_grammar(name):
    """I have a grammar {name}."""
    return str(GRAMMAR_DIR.joinpath(name).absolute()) + ".toml"


@when(parsers.parse("I generate a parser in {language}"), target_fixture="directory")
def i_generate_a_parser_in_language(language, grammar):
    """I generate a parser in {language}."""
    d = tempfile.mkdtemp()
    runner = CliRunner()
    result = runner.invoke(cli, [grammar, d, language])
    return Path(d)


@then(parsers.parse("I see a file {file}"), target_fixture="file")
def i_see_a_file(file, directory):
    """I see a file {file}."""
    assert directory.joinpath(file).exists()
    return str(directory.joinpath(file))


@when(
    parsers.parse('I run the parser with "{command}" and input:\n{text}'),
    target_fixture="return_code",
)
def i_run_the_parser_with_input(command, text, directory, file):
    """I run the parser with "{command}" and input:\n{text}"""
    # write text to a file
    f = tempfile.NamedTemporaryFile("w", delete=False)
    f.write(text)
    f.close()
    if command.find("_") > 0:
        command = command.replace("_", file)
    else:
        command = command + " " + file
    result = subprocess.run(f"cd {str(directory)} && {command} {f.name}", shell=True)
    return result.returncode


@then(parsers.parse("I get a {number:d} return code"))
def i_get_a_return_code(number, return_code):
    """I get a {number} response code."""
    assert return_code == number
