from rdpgen.gli import Go, Context, Type, Primitive, Composite

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
        [Primitive.Int, Primitive.String],
        g.declare("x", Primitive.Int),
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
        g.function(
            "inner", None, [Primitive.String], g.println(g.string("inner function"))
        ),
    )
    assert str(f) == INNER_FUNC


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


def test_go_types_array():
    g = Go(Context(expand_tabs=True))
    assert g.types(Composite.array(Primitive.Int)) == "[]int"
    assert g.types(Composite.array(Primitive.String)) == "[]string"


def test_go_array_declare():
    g = Go(Context(expand_tabs=True))
    f = g.function(
        "main",
        None,
        None,
        g.declare("mylist", Composite.array(Primitive.Int)),
        g.assign("mylist", g.array(Primitive.Int, [1, 2, 3])),
        g.println(g.string("mylist is "), "mylist"),
    )
    assert str(f) == ARRAY_DECLARE_ASSIGN


def test_go_prelude():
    g = Go(Context(expand_tabs=True))
    f = g.function("main", None, None, g.println(g.string("hello world")))
    assert g.prelude() == HELLO_WORLD_PRELUDE


def test_go_comment_oneline():
    g = Go(Context(expand_tabs=True))
    assert g.comment("i am a comment") == "// i am a comment"


def test_go_comment_multiline():
    g = Go(Context(expand_tabs=True))
    assert (
        g.comment("i am first line\ni am second line\ni am third line")
        == MULTI_LINE_COMMENT
    )


def test_go_while_true_loop():
    g = Go(Context(expand_tabs=True))
    assert (
        g.while_loop(g.println(g.string("i am in an infinite loop"))) == INFINITE_LOOP
    )


def test_go_while_condition():
    g = Go(Context(expand_tabs=True))
    f = g.function(
        "main",
        None,
        None,
        g.declare("x", Primitive.Int),
        g.assign("x", "0"),
        g.while_loop(
            g.println(g.string("x is"), "x"),
            g.increment("x"),
            condition=g.lt("x", "10"),
        ),
    )
    assert str(f) == WHILE_CONDITIONAL_LOOP


def test_go_array_length():
    g = Go(Context(expand_tabs=True))
    assert g.array_length("mylist") == "len(mylist)"


def test_go_command():
    g = Go(Context(expand_tabs=True))

    # test it produces correct call for running ls -l
    c = g.command("ls -l")
    assert "os/exec" in g.imports
    assert c == COMMAND_NO_OUTPUT

    # test it produces correct call for running ls -l with output
    c = g.command("ls -l", suppress_output=False)
    assert "os/exec" in g.imports
    assert c == COMMAND_OUTPUT
