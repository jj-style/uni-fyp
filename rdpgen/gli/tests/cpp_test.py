from rdpgen.gli import Cpp, Context, Type, Primitive, Composite

from .cpp_progs import *


def test_cpp_hello_world():
    g = Cpp(Context(expand_tabs=True))
    f = g.function("main", None, None, g.println(g.string("hello world")))
    assert f == HELLO_WORLD


def test_cpp_variables_in_function():
    g = Cpp(Context(expand_tabs=True))
    f = g.function(
        "variables",
        None,
        [Primitive.Int, Primitive.String],
        g.declare("x", Primitive.Int),
        g.assign("x", 25),
        g.print(g.string("x is "), "x"),
        g.println(g.string("arguments to function are "), "arg1", "arg2"),
    )
    assert str(f) == PRINT_VARIABLES


def test_cpp_for_loop():
    g = Cpp(Context(expand_tabs=True))
    f = g.for_loop(
        "i",
        0,
        g.lt("i", 10),
        g.increment("i", inc=1),
        g.println(g.string("i is "), "i"),
    )
    assert str(f) == FOR_LOOP


def test_cpp_if_else():
    g = Cpp(Context(expand_tabs=True))
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


def test_cpp_types_array():
    g = Cpp(Context(expand_tabs=True))
    assert g.types(Composite.array(Primitive.Int)) == "std::vector<int>"
    assert g.types(Composite.array(Primitive.String)) == "std::vector<std::string>"


def test_cpp_array_declare():
    g = Cpp(Context(expand_tabs=True))
    f = g.function(
        "main",
        None,
        None,
        g.declare("mylist", Composite.array(Primitive.Int)),
        g.assign("mylist", g.array(Composite.array(Primitive.Int), [1, 2, 3])),
        g.println(g.string("mylist is "), "mylist"),
    )
    assert str(f) == ARRAY_DECLARE_ASSIGN


def test_cpp_prelude():
    g = Cpp(Context(expand_tabs=True))
    f = g.function("main", None, None, g.println(g.string("hello world")))
    assert g.prelude() == HELLO_WORLD_PRELUDE


def test_cpp_comment_oneline():
    g = Cpp(Context(expand_tabs=True))
    assert g.comment("i am a comment") == "// i am a comment"


def test_cpp_comment_multiline():
    g = Cpp(Context(expand_tabs=True))
    assert (
        g.comment("i am first line\ni am second line\ni am third line")
        == MULTI_LINE_COMMENT
    )


def test_cpp_while_true_loop():
    g = Cpp(Context(expand_tabs=True))
    assert (
        g.while_loop(g.println(g.string("i am in an infinite loop"))) == INFINITE_LOOP
    )


def test_cpp_while_condition():
    g = Cpp(Context(expand_tabs=True))
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

def test_cpp_array_length():
    cpp = Cpp(Context(expand_tabs=True))
    assert cpp.array_length("mylist") == "mylist.size()"