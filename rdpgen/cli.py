import click
import tomli
from pathlib import Path
from .lexgen import template_lex_file, tokens_from_config_map
from .bnfparse.parse import Grammar
from .bnfparse.parsergen import parser_from_grammar


@click.command()
@click.argument("file")
@click.argument("outdir")
@click.argument(
    "language", type=click.Choice(["c++", "go", "python"], case_sensitive=False)
)
def cli(file: str, outdir: str, language: str):
    with open(file, "rb") as f:
        config = tomli.load(f)

    tokens = tokens_from_config_map(config.get("tokens", {}).items())

    # create a lexer program
    template_lex_file(tokens, outdir)

    # parse the bnf grammar rules
    grammar_cfg = config.get("grammar", {})
    grammar = Grammar(grammar_cfg)
    prog = parser_from_grammar(grammar, tokens, language, outdir)

    outpath = Path(outdir) / f"parser.{prog.extension}"
    prog.write_file(str(outpath))
