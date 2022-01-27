from .common import file_contains
from rdpgen.gli import Go, Context, Type

from .go_progs import *


def test_go_hello_world():
    g = Go(Context(expand_tabs=True))
    f = g.function("main", None, None, g.println(g.string("hello world")))
    assert f == HELLO_WORLD


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
    assert f == PRINT_VARIABLES


def test_go_inner_functions():
    g = Go(Context(expand_tabs=True))
    f = g.function(
        "function",
        None,
        None,
        g.function("inner", None, [Type.String], g.println(g.string("inner function"))),
    )
    assert f == INNER_FUNC


def test_go_for_loop():
    g = Go(Context(expand_tabs=True))
    f = g.for_loop(
        "i",
        0,
        g.lt("i", 10),
        g.increment("i", inc=1),
        g.println(g.string("i is "), "i"),
    )
    assert f == FOR_LOOP


def test_go_if_else():
    g = Go(Context(expand_tabs=True))
    first = g.if_else(
        g.eq("i", "0"),
        [g.println(g.string("i is zero"))],
        false_stmts=[g.println(g.string("i is not zero"))],
    )
    assert first == IF_ELSE

    second = g.if_else(
        g.eq("mode", g.string("debug")),
        [g.println(g.string("=== RUNNING IN DEBUG MODE ==="))],
    )
    assert second == IF_NO_ELSE
