import click
import tomli
from .lexgen import template_lex_file, tokens_from_config_map
from .bnfparse.parse import Grammar
from .bnfparse.parsergen import parser_from_grammar


@click.command()
@click.argument("file")
@click.argument("outdir")
def cli(file: str, outdir: str):
    """Interface to the recursive descent parser generator

    Args:

        file (str):             path to TOML file with token and grammar rules
        outdir (Optional[str]): directory to output parser program
    """
    with open(file) as f:
        config = tomli.load(f)

    tokens = tokens_from_config_map(config.get("tokens", {}).items())

    # create a lexer program
    template_lex_file(tokens, outdir)

    # parse the bnf grammar rules
    grammar_cfg = config.get("grammar", {})
    grammar = Grammar(grammar_cfg)
    parser_from_grammar(grammar)
