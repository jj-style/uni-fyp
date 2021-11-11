from typing import List
import click
import tomli
from lexgen import Token, template_lex_file


@click.command()
@click.argument("file")
@click.argument("outdir")
def cli(file: str, outdir: str):
    """Interface to the recursive descent parser generator

    Args:
        file (str):             path to TOML file containing token and grammar rules
        outdir (Optional[str]): directory to output parser program
    """
    with open(file) as f:
        config = tomli.load(f)

    # get all the tokens that will appear in the language
    tokens: List[Token] = []
    for name, regex in config.get("tokens", {}).items():
        tokens.append(Token(name, regex))

    # create a lexer program
    template_lex_file(tokens, outdir)
