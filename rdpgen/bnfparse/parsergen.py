from .parse import Grammar
from rdpgen.lexgen import Token
from rdpgen.gli import Program, Language, Context, Go, Python, Cpp, Composite, Primitive
from rdpgen.bnfparse.parse import NodeType

from typing import List
from pathlib import Path


def lang_from_name(name: str, ctx: Context) -> Language:
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

    # setup lexing stuff
    prog.add(l.declare("tokens", Composite.array(Composite.array(Primitive.String))))

    # shell out to the lexer to create tokens
    call_lexer = l.function(
        "generate_tokens",
        None,
        {"file": Primitive.String},
        l.declare("command", Primitive.String),
        l.assign(
            "command",
            l.string("""cd lexer && make --silent && ./lexer """),
        ),
        l.increment("command", inc="file"),
        l.command("command", exit_on_failure=True, suppress_output=True),
    )

    load_tokens_stmts = [
        l.assign("tokens", l.array(Composite.array(Primitive.String), [])),
        l.declare("token_lines", Composite.array(Primitive.String)),
        l.assign("token_lines", l.read_lines(l.string("lexer/out.jl"))),
        l.array_iterate(
            "token_lines",
            "idx",
            l.array_append(
                "tokens", l.string_split(l.index("token_lines", "idx"), l.string(":"))
            ),
        ),
    ]
    # HACK: for python global tokens variable
    if isinstance(l, Python):
        load_tokens_stmts.insert(0, "global tokens")
    load_tokens = l.function("load_tokens", None, None, *load_tokens_stmts)

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
        {"line_num": Primitive.String, "e": Primitive.String},
        l.println(
            l.string("Error: line "),
            "line_num",
            l.string("- expected "),
            "e",
        ),
        l.exit(code=1),
    )

    parse = l.function(
        "parse",
        None,
        {"file": Primitive.String},
        l.call("generate_tokens", "file") + l.terminator,
        l.call("load_tokens") + l.terminator,
        l.call(grammar.start) + l.terminator,
    )

    main = l.function(
        "main",
        None,
        None,
        l.if_else(
            l.lt(l.argc(), 2), [l.println(l.string("usage: parser FILE")), l.exit(1)]
        ),
        l.declare("filename", Primitive.String),
        l.assign("filename", l.index(l.argv(), 1)),
        l.call("parse", "filename") + l.terminator,
    )

    prog.add(call_lexer)
    prog.add(load_tokens)
    prog.add(peek)
    prog.add(get_token)
    prog.add(expect)

    def handle_term(t):
        stmts = []
        idx = 0
        while idx < len(t.children):
            factor = t.children[idx]
            if factor == NodeType.TERMINAL:
                following = []
                if idx + 1 < len(t.children):
                    for i in range(idx + 1, len(t.children)):
                        if t.children[i] == NodeType.NONTERMINAL:
                            following.append(t.children[i])
                            idx += 1
                stmts.extend(handle_terminal(factor, *following))
            elif factor == NodeType.NONTERMINAL:
                stmts.extend(handle_nonterminal(factor))
            idx += 1
        return stmts

    def handle_terminal(factor, *following_factors):
        following = []
        for f in following_factors:
            following.extend(handle_nonterminal(f))

        next_term_name = l.varn("next_token")
        s1 = l.declare(next_term_name, Composite.array(Primitive.String))
        s2 = l.assign(
            next_term_name,
            l.call("get_token" if factor.quantifier is None else "peek"),
        )
        s3 = l.if_else(
            l.eq(l.index(next_term_name, 1), l.string(factor.value)),
            [l.do_nothing()] if len(following) == 0 else following,
            false_stmts=[
                l.call("expect", l.index(next_term_name, 2), l.string(factor.value))
                + l.terminator
            ],
        )

        return [s1, s2, s3]

    def handle_nonterminal(factor):
        return [l.call(factor.value) + l.terminator]

    for rule, prod in grammar.productions.items():
        # either-or-construction
        if prod == NodeType.OR:
            left_set = grammar.left_set(rule)
            tokens = list(left_set.keys())

            terminals = all([c == NodeType.TERMINAL for c in prod.children])

            def recurse(left):
                return l.if_else(
                    l.eq(l.index("next_token", 1), l.string(left[0])),
                    [
                        l.call(left_set[left[0]]) + l.terminator
                        if not terminals
                        else l.do_nothing(),
                    ],
                    false_stmts=[
                        recurse(left[1:])
                        if len(left) > 1
                        else l.call(
                            "expect",
                            l.index("next_token", 2),
                            l.string(",".join(tokens)),
                        )
                        + l.terminator
                    ],
                )

            f = l.function(
                rule,
                None,
                None,
                l.declare("next_token", Composite.array(Primitive.String)),
                l.assign(
                    "next_token",
                    l.call("peek") if not terminals else l.call("get_token"),
                ),
                recurse(tokens),
            )
        elif prod == NodeType.TERM:
            f = l.function(rule, None, None, *handle_term(prod))
        elif prod == NodeType.TERMINAL:
            f = l.function(rule, None, None, *handle_terminal(prod))
        else:
            f = l.function(rule, None, [], l.do_return(None))
        prog.add(f)
        # print(f)

    prog.add(parse)
    prog.add(main)

    # print(prog.generate())
    return prog
