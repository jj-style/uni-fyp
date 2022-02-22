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
@click.option(
    "--case",
    "-c",
    type=click.Choice(["camel", "snake"]),
    help="which case identifiers should be generated in",
)
@click.option(
    "--expand-tabs/--no-expand-tabs",
    help="expand tabs to spaces (default expand-tabs)",
    default=True,
)
@click.option(
    "--tab-size",
    "-t",
    type=int,
    help="How many spaces in each layer of indentation (if expand-tabs is set)",
)
def cli(
    file: str, outdir: str, language: str, case: str, expand_tabs: bool, tab_size: int
):
    # parse config
    with open(file, "rb") as f:
        config = tomli.load(f)

    tokens = tokens_from_config_map(config.get("tokens", {}).items())

    lang_opts_cfg = config.get("language_options", {})
    lang_opts_cli = {"case": case, "expand_tabs": expand_tabs, "tab_size": tab_size}
    lang_opts_cli = {k: v for k, v in lang_opts_cli.items() if v is not None}
    # cli args take precedence over config file
    lang_opts = {**lang_opts_cfg, **lang_opts_cli}

    # create a lexer program
    template_lex_file(tokens, outdir)

    # parse the bnf grammar rules
    grammar_cfg = config.get("grammar", {})
    grammar = Grammar(grammar_cfg)
    prog = parser_from_grammar(grammar, tokens, language, lang_opts, outdir)

    outpath = Path(outdir) / f"parser.{prog.extension}"
    prog.write_file(str(outpath))
    print(f"parser generated at {outpath}")
