from .core import Grammar
from rdpgen import gli


def parser_from_grammar(grammar: Grammar):
    g = gli.Go()
    for p in grammar.productions:
        f = g.function(p.name, None, [], g.do_return(None))
        print(f)
        # create function with p.name
        # print(f"def parse_{p.name}():")
        # print("\ttoken = get_token()")
        # for idx, term in enumerate(p.expression.terms):
        # get_token - check equals a term
        # print(f"\t{'el' if idx > 0 else ''}", end="")
        # print("if " + f"token == {term}:\n\t\tpass")
        # print("\telse:\n\t\traise Exception()")
