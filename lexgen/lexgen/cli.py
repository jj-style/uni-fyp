import os
from typing import List, Optional
from core import Token
import click
from jinja2 import FileSystemLoader, Environment
import tomli


@click.command()
@click.argument("file")
@click.option("--output", help="file to output to or stdout if None")
def cli(file: str, output: Optional[str]):
    """Interface to the lexer generator

    Args:
        file (str):             path to TOML file containing token and grammar rules
        output (Optional[str]): path to .lex file to create along with a Makefile
                                to build it. If not supplied then lex file is written
                                 to stdout
    """
    with open(file) as f:
        config = tomli.load(f)

    tokens: List[Token] = []
    for name, regex in config.get("tokens", {}).items():
        tokens.append(Token(name, regex))

    template_lex_file(tokens, output)


def template_lex_file(tokens: List[Token], output: Optional[str]):
    """Generate the lexer from some description of tokens and write to file or stout.

    Args:
        tokens (List[Token]):   token rules that exist in the language
        output (Optional[str]): path to .lex file to create along with a Makefile
                                to build it. If not supplied then lex file is written
                                to stdout
    """
    loader = FileSystemLoader("templates")
    env = Environment(loader=loader)
    template = env.get_template("lex.j2")
    result = template.render(tokens=tokens, skip_whitespace=True)
    if not output:
        print(result)
    else:
        with open(output, "w") as outfile:
            outfile.write(result)

        outdir = os.path.dirname(output)
        lexfile = os.path.basename(output)
        makefile = env.get_template("Makefile.j2")
        with open(f"{outdir}/Makefile", "w") as mf:
            mf.write(
                makefile.render(program=os.path.splitext(lexfile)[0], lexfile=lexfile),
            )
