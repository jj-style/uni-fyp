import os
from typing import List, Dict
from pathlib import Path
from jinja2 import FileSystemLoader, Environment
from lexgen.core import Token


def tokens_from_config_map(config: Dict[str, str]) -> List[Token]:
    """Parse the tokens section of the config into Token items

    Args:
        config (Dict[str, str]): Config section from TOML file

    Returns:
        List[Token]: The tokens that appear in the language
    """
    tokens: List[Token] = []
    for name, regex in config:
        tokens.append(Token(name, regex))
    return tokens


def template_lex_file(tokens: List[Token], directory: str):
    """Generate the lexer from some description of tokens and write to file or stout.

    Args:
        tokens    (List[Token]):   token rules that exist in the language
        directory (str):           path to directory to create lexer in
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    loader = FileSystemLoader(os.path.join(this_dir, "templates"))
    env = Environment(loader=loader)
    template = env.get_template("lex.j2")
    result = template.render(tokens=tokens, skip_whitespace=True)

    base_path = Path(directory)
    # if base_path.exists():
    #     raise Exception(
    #         f"directory {base_path} already exists. Aborting to prevent data loss"
    #     )
    lexer_path = base_path.joinpath("lexer")
    if not lexer_path.exists():
        lexer_path.mkdir(parents=True)

    with open(lexer_path.joinpath("prog.lex"), "w") as outfile:
        outfile.write(result)

    makefile = env.get_template("Makefile.j2")
    with open(lexer_path.joinpath("Makefile"), "w") as mf:
        mf.write(
            makefile.render(program="lexer", lexfile="prog.lex"),
        )
