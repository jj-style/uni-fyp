from .parse import Grammar
from rdpgen.lexgen import Token
from rdpgen.ali import Program, Language, Go, Python, Cpp, Composite, Primitive
from rdpgen.bnfparse.parse import NodeType

from typing import List, Dict, Any
from pathlib import Path
from copy import deepcopy


def lang_from_name(name: str, options: Dict[str, Any]) -> Language:
    if name in options:
        # there are specific language options
        specific_opts = options.pop(name)
        # merge back in to top-level of dictionary
        options = {**options, **specific_opts}
    # remove other language options
    for lang in ["c++", "go", "python"]:
        if lang in options:
            options.pop(lang)
    try:
        if name == "c++":
            return Cpp(**options)
        elif name == "go":
            return Go(**options)
        elif name == "python":
            return Python(**options)
    except TypeError as e:
        print("failed to create language:", e)
        exit(1)


def parser_from_grammar(
    grammar: Grammar,
    tokens: List[Token],
    language: str,
    language_options: Dict[str, Any],
    outdir: str,
):
    outdir = Path(outdir)
    l = lang_from_name(language, language_options)  # noqa
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
            l.s("""cd lexer && make --silent && ./lexer """),
        ),
        l.increment("command", inc="file"),
        l.command("command", exit_on_failure=True, suppress_output=False),
    )

    load_tokens_stmts = [
        l.assign("tokens", l.array(Composite.array(Primitive.String), [])),
        l.declare("token_lines", Composite.array(Primitive.String)),
        l.assign("token_lines", l.read_lines(l.s("lexer/out.jl"))),
        l.array_iterate(
            "token_lines",
            "idx",
            l.array_append(
                "tokens",
                l.string_split(l.index(l.cc("token_lines"), "idx"), l.s("\a")),
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
            l.s("Error: line "),
            "line_num",
            l.s("- expected "),
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
        l.call(l.cc(grammar.start)) + l.terminator,
    )

    nt = l.cc("next_token")
    main = l.function(
        "main",
        None,
        None,
        l.if_else(l.lt(l.argc(), 2), [l.println(l.s("usage: parser FILE")), l.exit(1)]),
        l.declare("filename", Primitive.String),
        l.assign("filename", l.index(l.argv(), 1)),
        l.call("parse", "filename") + l.terminator,
        # check for EOF
        l.declare(nt, Composite.array(Primitive.String)),
        l.assign(nt, l.call("get_token")),
        l.if_else(
            l.neq(l.index(nt, 0), l.s("EOF")),
            [l.call("expect", l.index(nt, 2), l.s("EOF")) + l.terminator],
        ),
    )

    prog.add(call_lexer)
    prog.add(load_tokens)
    prog.add(peek)
    prog.add(get_token)
    prog.add(expect)

    def handle_rule(t):
        if t == NodeType.TERM:
            return handle_term(t)
        elif t == NodeType.NONTERMINAL:
            return handle_nonterminal(t)
        elif t == NodeType.TERMINAL or t == NodeType.TOKEN:
            return handle_terminal(t)

    def handle_term(t):
        stmts = []
        idx = 0
        # loop through children, but if there's following non-terminals,
        # consume them too and skip ahead
        while idx < len(t.children):
            factor = t.children[idx]
            if factor == NodeType.TERMINAL or factor == NodeType.TOKEN:
                following = []
                if idx + 1 < len(t.children):
                    for i in range(idx + 1, len(t.children)):
                        if t.children[i] == NodeType.NONTERMINAL:
                            following.append(t.children[i])
                            idx += 1
                        else:
                            break
                stmts.extend(handle_terminal(factor, *following))
            elif factor == NodeType.NONTERMINAL:
                stmts.extend(handle_nonterminal(factor))
            idx += 1
        return stmts

    def handle_terminal(factor, *following_factors):
        following = []
        for f in following_factors:
            following.extend(handle_nonterminal(f))

        next_term_name = l.cc(l.varn("next_token"))
        s1 = l.declare(next_term_name, Composite.array(Primitive.String))
        s2 = l.assign(
            next_term_name,
            l.call("get_token"),
        )

        token_idx = 1 if factor == NodeType.TERMINAL else 0
        s3 = l.if_else(
            l.eq(l.index(next_term_name, token_idx), l.s(factor.value)),
            [l.do_nothing()] if len(following) == 0 else following,
            false_stmts=[
                l.call("expect", l.index(next_term_name, 2), l.s(factor.value))
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

            has_epsilon = "¬" in left_set
            if has_epsilon:
                left_set.pop("¬")
                tokens.remove("¬")

            non_terminals = False
            for child in prod.children:
                if child == NodeType.TERM:
                    for factor in child.children:
                        non_terminals |= factor == NodeType.NONTERMINAL
                else:
                    non_terminals |= child == NodeType.NONTERMINAL

            def recurse(left):
                tok_idx = 0 if left_set[left[0]].get("token", False) else 1

                next_tok = l.cc("next_token")
                get_tok = l.cc("get_token")

                or_term = left_set[left[0]]["or_term"]
                if len(or_term.children) > 1:
                    following_stuff = deepcopy(or_term)
                    following_stuff._children.pop(0)

                return l.if_else(
                    l.eq(l.index(next_tok, tok_idx), l.s(left[0])),
                    handle_rule(or_term)
                    if non_terminals
                    else [l.call(get_tok) + l.terminator]
                    if has_epsilon
                    else [l.do_nothing()]
                    if len(or_term.children) <= 1
                    else handle_rule(following_stuff),
                    false_stmts=[recurse(left[1:])]
                    if len(left) > 1
                    else [
                        l.call(
                            "expect",
                            l.index(next_tok, 2),
                            l.s(",".join(tokens)),
                        )
                        + l.terminator
                    ]
                    if not has_epsilon
                    else None,
                )

            f = l.function(
                rule,
                None,
                None,
                l.comment(grammar.bnf_from_rule(rule)),
                l.declare(l.cc("next_token"), Composite.array(Primitive.String)),
                l.assign(
                    l.cc("next_token"),
                    l.call("peek")
                    if non_terminals or has_epsilon
                    else l.call("get_token"),
                ),
                recurse(tokens),
            )
        elif prod == NodeType.TERM:
            f = l.function(
                rule,
                None,
                None,
                l.comment(grammar.bnf_from_rule(rule)),
                *handle_term(prod),
            )
        elif prod == NodeType.TERMINAL or prod == NodeType.TOKEN:
            f = l.function(
                rule,
                None,
                None,
                l.comment(grammar.bnf_from_rule(rule)),
                *handle_terminal(prod),
            )
        elif prod == NodeType.NONTERMINAL:
            f = l.function(
                rule,
                None,
                None,
                l.comment(grammar.bnf_from_rule(rule)),
                *handle_nonterminal(prod),
            )
        else:
            f = l.function(rule, None, [], l.do_return(None))
        prog.add(f)

    prog.add(parse)
    prog.add(main)

    return prog
