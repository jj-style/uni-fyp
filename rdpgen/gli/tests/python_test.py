from rdpgen.gli import Python, Context, Primitive, Composite
from .python_progs import *


def test_python_imports():
    cases = [
        {"import": "typing.List", "expect": "from typing import List"},
        {"import": "random.randint", "expect": "from random import randint"},
        {"import": "math", "expect": "import math"},
        {"import": "a.b.c.d", "expect": "from a.b.c import d"},
    ]
    for case in cases:
        p = Python(Context(expand_tabs=True))
        p.import_package(case["import"])
        assert p.prelude().strip() == case["expect"]


def test_python_postlude():
    p = Python(Context(expand_tabs=True))
    f = str(p.function("main", None, None, p.println(p.string("hello world"))))
    assert str(p.postlude()) == """if __name__ == "__main__":\n  main()\n"""


def test_python_hello_world():
    p = Python(Context(expand_tabs=True))
    f = p.function("main", None, None, p.println(p.string("hello world")))
    assert f == HELLO_WORLD


def test_python_variables_in_function():
    p = Python(Context(expand_tabs=True))
    f = p.function(
        "variables",
        None,
        [Primitive.Int, Primitive.String],
        p.declare("x", Primitive.Int),
        p.assign("x", 25),
        p.print(p.string("x is "), "x"),
        p.println(p.string("arguments to function are "), "arg1", "arg2"),
    )
    assert f == PRINT_VARIABLES


def test_python_inner_functions():
    p = Python(Context(expand_tabs=True))
    f = p.function(
        "function",
        None,
        None,
        p.function(
            "inner", None, [Primitive.String], p.println(p.string("inner function"))
        ),
    )
    assert str(f) == INNER_FUNC


def test_python_for_loop():
    p = Python(Context(expand_tabs=True))
    f = p.for_loop(
        "i",
        0,
        p.lt("i", 10),
        p.increment("i", inc=1),
        p.println(p.string("i is "), "i"),
    )
    assert f == FOR_LOOP


def test_python_if_else():
    p = Python(Context(expand_tabs=True))
    first = p.if_else(
        p.eq("i", "0"),
        [p.println(p.string("i is zero"))],
        false_stmts=[p.println(p.string("i is not zero"))],
    )
    assert first == IF_ELSE

    second = p.if_else(
        p.eq("mode", p.string("debug")),
        [p.println(p.string("=== RUNNING IN DEBUG MODE ==="))],
    )
    assert second == IF_NO_ELSE


def test_python_types_array():
    p = Python(Context(expand_tabs=True))
    assert p.types(Composite.array(Primitive.Int)) == "[]int"
    assert p.types(Composite.array(Primitive.String)) == "[]string"


def test_python_array_declare():
    p = Python(Context(expand_tabs=True))
    f = p.function(
        "main",
        None,
        None,
        p.declare("mylist", Composite.array(Primitive.Int)),
        p.assign("mylist", p.array(Primitive.Int, [1, 2, 3])),
        p.println(p.string("mylist is "), "mylist"),
    )
    assert str(f) == ARRAY_DECLARE_ASSIGN


def test_python_prelude():
    p = Python(Context(expand_tabs=True))
    f = p.function("main", None, None, p.println(p.string("hello world")))
    assert p.prelude() == HELLO_WORLD_PRELUDE


def test_python_comment_oneline():
    p = Python(Context(expand_tabs=True))
    assert p.comment("i am a comment") == "// i am a comment"


def test_python_comment_multiline():
    p = Python(Context(expand_tabs=True))
    assert (
        p.comment("i am first line\ni am second line\ni am third line")
        == MULTI_LINE_COMMENT
    )


def test_python_while_true_loop():
    p = Python(Context(expand_tabs=True))
    assert (
        p.while_loop(p.println(p.string("i am in an infinite loop"))) == INFINITE_LOOP
    )


def test_python_while_condition():
    p = Python(Context(expand_tabs=True))
    f = p.function(
        "main",
        None,
        None,
        p.declare("x", Primitive.Int),
        p.assign("x", "0"),
        p.while_loop(
            p.println(p.string("x is"), "x"),
            p.increment("x"),
            condition=p.lt("x", "10"),
        ),
    )
    assert str(f) == WHILE_CONDITIONAL_LOOP


def test_python_array_length():
    p = Python(Context(expand_tabs=True))
    assert p.array_length("mylist") == "len(mylist)"
