from .parse import Grammar
from rdpgen.lexgen import Token
from rdpgen.gli import Program, Language, Context, Go, Python, Cpp, Composite, Primitive

from typing import List
from pathlib import Path


def lang_from_name(name: str, ctx: Context) -> Language:
    print("name is", name)
    if name == "c++":
        return Cpp(ctx)
    elif name == "go":
        return Go(ctx)
    elif name == "python":
        return Python(ctx)


def parser_from_grammar(
    grammar: Grammar, tokens: List[Token], language: str, outdir: str
):
    outdir = Path(outdir)
    l = lang_from_name(language, Context(expand_tabs=True))  # noqa
    prog = Program(l)
    print(f"\nparser in {l.name}\n===================\n")

    # setup lexing stuff
    prog.add(l.declare("tokens", Composite.array(Primitive.String)))

    # shell out to the lexer to create tokens
    call_lexer = l.function(
        "generate_tokens",
        None,
        {"text": Primitive.String},
        l.declare("command", Primitive.String),
        l.assign(
            "command",
            l.string(f"""cd {outdir / "lexer"} && make && echo """),
        ),
        l.assign("command", l.add("command", "text")),
        l.assign("command", l.add("command", l.string(" | ./lexer"))),
        l.command("command", exit_on_failure=True),
    )
    prog.add(call_lexer)

    # for rule, prod in grammar.productions.items():
    # f = l.function(rule, None, [], l.do_return(None))
    # prog.add(f)
    print(prog.generate())
    return prog
