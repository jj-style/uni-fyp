from .parse import Grammar
from rdpgen.lexgen import Token
from rdpgen.gli import Program, Language, Context, Go, Python, Cpp, Composite, Primitive
from rdpgen.bnfparse.parse import NodeType

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
    prog.add(l.declare("tokens", Composite.array(Composite.array(Primitive.String))))

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

    load_tokens = l.function(
        "load_tokens",
        None,
        None,
        l.declare("token_lines", Composite.array(Primitive.String)),
        l.assign("token_lines", l.read_lines(l.string(outdir / "lexer" / "out.jl"))),
        l.array_iterate(
            "token_lines",
            "idx",
            l.array_append(
                "tokens", l.string_split(l.index("token_lines", "idx"), l.string(":"))
            ),
        ),
    )

    peek = l.function(
        "peek",
        Composite.array(Primitive.String),
        None,
        l.if_else(
            l.gt(l.array_length("tokens"), 0),
            [l.do_return(expression=l.index("tokens", 0))],
        ),
        l.do_return(expression=l.array(Primitive.String, [])),
    )
    get_token = l.function(
        "get_token",
        Composite.array(Primitive.String),
        None,
        l.if_else(
            l.gt(l.array_length("tokens"), 0),
            [
                l.declare("next", Composite.array(Primitive.String)),
                l.assign("next", l.index("tokens", 0)),
                l.array_remove("tokens", 0),
                l.do_return(expression="next"),
            ],
        ),
        l.do_return(l.array(Primitive.String, [])),
    )

    expect = l.function(
        "expect",
        None,
        {"e": Primitive.String},
        l.println(l.string("Error: expected "), "e", l.string(" at this position")),
        l.exit(code=1),
    )

    parse = l.function(
        "parse",
        Primitive.Int,
        {"file": Primitive.String},
        l.declare("source", Primitive.String),
        l.comment("TODO: source = load_file(file)"),
        l.call("generate_tokens", "source"),
        l.call("load_tokens"),
        l.comment(l.call(grammar.start)),
    )

    prog.add(call_lexer)
    prog.add(load_tokens)
    prog.add(peek)
    prog.add(get_token)
    prog.add(expect)
    prog.add(parse)

    for rule, prod in grammar.productions.items():
        # either-or-construction
        if prod == NodeType.OR:
            left_set = grammar.left_set(rule)
            tok = list(left_set.keys())[0]
            tok_func = left_set[tok]
            f = l.function(
                rule,
                None,
                None,
                l.declare("next_token", Composite.array(Primitive.String)),
                l.assign("next_token", l.call("peek")),
                l.if_else(
                    l.eq(l.index("next_token", 1), l.string(tok)),
                    [
                        l.call(tok_func),
                    ],
                    false_stmts=[],
                ),
            )
        else:
            f = l.function(rule, None, [], l.do_return(None))
        prog.add(f)
        # print(f)
    print(prog.generate())
    return prog
