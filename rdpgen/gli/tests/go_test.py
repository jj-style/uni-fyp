from .common import file_contains
from rdpgen.gli import Go, Context, Type

from .go_progs import HELLO_WORLD, PRINT_VARIABLES


def test_go_hello_world():
    g = Go(Context(expand_tabs=True))
    f = g.function("main", None, None, g.println(g.string("hello world")))
    assert str(f) == HELLO_WORLD


def test_go_variables_in_function():
    g = Go(Context(expand_tabs=True))
    f = g.function(
        "variables",
        None,
        [Type.Int, Type.String],
        g.declare("x", Type.Int),
        g.assign("x", 25),
        g.print(g.string("x is "), "x"),
        g.println(g.string("arguments to function are "), "arg1", "arg2"),
    )
    print(f)
    assert str(f) == PRINT_VARIABLES
