from rdpgen.gli import Go, Context, Type, Primitive, Composite, MissingTypeError

from .go_progs import *
import pytest


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
    c = g.command("ls -l", exit_on_failure=False)
    assert "os/exec" in g.imports
    assert c == COMMAND_NO_OUTPUT

    # test it produces correct call for running ls -l with output
    c = g.command("ls -l", suppress_output=False, exit_on_failure=False)
    assert "os/exec" in g.imports
    assert c == COMMAND_OUTPUT


def test_go_command_exit_on_failure():
    g = Go(Context(expand_tabs=True))

    c = g.command("ls -l", exit_on_failure=True)
    assert c == COMMAND_NO_OUTPUT_WITH_EXIT

    c = g.command("ls -l", suppress_output=False, exit_on_failure=True)
    assert c == COMMAND_OUTPUT_WITH_EXIT


def test_go_exit():
    g = Go(Context(expand_tabs=True))
    assert g.exit() == "os.Exit(0)"
    assert "os" in g.imports
    cases = range(100)
    for c in cases:
        assert g.exit(c) == f"os.Exit({c})"


def test_go_read_lines():
    g = Go(Context(expand_tabs=True))
    g.read_lines("myfile.txt")
    g.read_lines("myfile.txt")
    assert len(g.helper_funcs) == 1

    lines = g.assign("lines", g.read_lines(g.string("file.txt")))
    assert lines == 'lines = readLines("file.txt")'
    f = str(g.helper_funcs["readLines"])
    assert f == READ_LINES_FUNC


def test_go_array_append():
    g = Go(Context(expand_tabs=True))
    assert g.array_append("mylist", 5) == "mylist = append(mylist, 5)"
    assert g.array_append("mylist", g.string("hi")) == 'mylist = append(mylist, "hi")'


def test_go_boolean_and():
    go = Go(Context(expand_tabs=True))
    assert go.bool_and(go.gt("x", 10), go.lt("x", 20)) == "x > 10 && x < 20"


def test_go_boolean_or():
    go = Go(Context(expand_tabs=True))
    assert go.bool_or(go.lt("x", 10), go.gt("x", 20)) == "x < 10 || x > 20"


def test_go_array_iterate():
    g = Go(Context(expand_tabs=True))
    i1 = g.array_iterate("mylist", "i", g.println("i"))
    assert (
        str(i1)
        == """var i int
for i, _ = range mylist {
  fmt.Println(i)
}"""
    )

    i2 = g.array_iterate("mylist", "i", g.println("i"), declare_it=False)
    assert (
        i2
        == """for i, _ = range mylist {
  fmt.Println(i)
}"""
    )

    i3 = g.array_iterate(
        "mylist",
        "elem",
        g.println("elem"),
        iterate_items=True,
        type=Primitive.String,
    )
    assert (
        i3
        == """var elem string
for _, elem = range mylist {
  fmt.Println(elem)
}"""
    )

    with pytest.raises(MissingTypeError) as err:
        str(g.array_iterate("mylist", "elem", g.println("elem"), iterate_items=True))


def test_go_array_enumerate():
    g = Go(Context(expand_tabs=True))

    e1 = g.array_enumerate("mylist", "i", "elem", g.println("i", "elem"))
    assert (
        str(e1)
        == """var i int
for i, elem = range mylist {
  fmt.Println(i, elem)
}"""
    )

    e2 = g.array_enumerate(
        "mylist",
        "i",
        "elem",
        g.println("i", "elem"),
        declare_item=True,
        type=Primitive.String,
    )
    assert (
        str(e2)
        == """var i int
var elem string
for i, elem = range mylist {
  fmt.Println(i, elem)
}"""
    )

    with pytest.raises(MissingTypeError) as err:
        str(
            g.array_enumerate(
                "mylist",
                "i",
                "elem",
                g.println("i", "elem"),
                declare_item=True,
            )
        )


def test_go_string_split():
    g = Go(Context(expand_tabs=True))
    assert (
        g.string_split(g.string("hello,world"), g.string(","))
        == """strings.Split("hello,world", ",")"""
    )
    assert g.string_split("list", g.string(":")) == """strings.Split(list, ":")"""
    assert "strings" in g.imports
