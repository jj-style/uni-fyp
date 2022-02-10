from rdpgen.gli import Cpp, Context, Type, Primitive, Composite, MissingTypeError

from .cpp_progs import *

import pytest


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


def test_cpp_array_append():
    cpp = Cpp(Context(expand_tabs=True))
    assert cpp.array_append("mylist", 5) == "mylist.push_back(5);"
    assert cpp.array_append("mylist", cpp.string("hi")) == 'mylist.push_back("hi");'


def test_cpp_command():
    cpp = Cpp(Context(expand_tabs=True))

    # test it produces correct call for running ls -l
    c = cpp.command(cpp.string("ls -l"), exit_on_failure=False)
    assert "stdlib.h" in cpp.imports
    assert str(c) == COMMAND_NO_OUTPUT

    # test it produces correct call for running ls -l with output
    c = cpp.command(cpp.string("ls -l"), suppress_output=False, exit_on_failure=False)
    assert "stdlib.h" in cpp.imports
    assert c == COMMAND_OUTPUT


def test_cpp_command_with_exit():
    cpp = Cpp(Context(expand_tabs=True))

    # test it produces correct call for running ls -l
    c = cpp.command(cpp.string("ls -l"), exit_on_failure=True)
    assert "stdlib.h" in cpp.imports
    assert c == COMMAND_NO_OUTPUT_WITH_EXIT

    # test it produces correct call for running ls -l with output
    c = cpp.command(cpp.string("ls -l"), suppress_output=False, exit_on_failure=True)
    assert "stdlib.h" in cpp.imports
    assert c == COMMAND_OUTPUT_WITH_EXIT


def test_cpp_exit():
    cpp = Cpp(Context(expand_tabs=True))
    assert cpp.exit() == "exit(0);"
    assert "stdlib.h" in cpp.imports
    cases = range(100)
    for c in cases:
        assert cpp.exit(c) == f"exit({c});"


def test_cpp_read_lines():
    cpp = Cpp(Context(expand_tabs=True))
    cpp.read_lines("myfile.txt")
    cpp.read_lines("myfile.txt")
    assert len(cpp.helper_funcs) == 1

    lines = cpp.assign("lines", cpp.read_lines(cpp.string("file.txt")))
    assert lines == 'lines = read_lines("file.txt");'
    f = str(cpp.helper_funcs["read_lines"])
    assert f == READ_LINES_FUNC


def test_cpp_boolean_and():
    cpp = Cpp(Context(expand_tabs=True))
    assert cpp.bool_and(cpp.gt("x", 10), cpp.lt("x", 20)) == "x > 10 && x < 20"


def test_cpp_boolean_or():
    cpp = Cpp(Context(expand_tabs=True))
    assert cpp.bool_or(cpp.lt("x", 10), cpp.gt("x", 20)) == "x < 10 || x > 20"


def test_cpp_array_iterate():
    cpp = Cpp(Context(expand_tabs=True))
    i1 = cpp.array_iterate("mylist", "i", cpp.println("i"))
    assert (
        i1
        == """int i;
for (i = 0; i < mylist.size(); i = i + 1) {
  std::cout << i << std::endl;
}"""
    )

    i2 = cpp.array_iterate("mylist", "i", cpp.println("i"), declare_it=False)
    assert (
        i2
        == """for (i = 0; i < mylist.size(); i = i + 1) {
  std::cout << i << std::endl;
}"""
    )

    i3 = cpp.array_iterate(
        "mylist",
        "elem",
        cpp.println("elem"),
        iterate_items=True,
        type=Primitive.String,
    )
    assert (
        i3
        == """for (std::string elem : mylist) {
  std::cout << elem << std::endl;
}"""
    )

    with pytest.raises(MissingTypeError) as err:
        # could add special case for C++ to add `auto` if type not given
        str(
            cpp.array_iterate("mylist", "elem", cpp.println("elem"), iterate_items=True)
        )


def test_cpp_array_enumerate():
    cpp = Cpp(Context(expand_tabs=True))

    e1 = cpp.array_enumerate("mylist", "i", "elem", cpp.println("i", "elem"))
    assert (
        str(e1)
        == """int i;
for (i = 0; i < mylist.size(); i = i + 1) {
  elem = mylist[i];
  std::cout << i << elem << std::endl;
}"""
    )

    e2 = cpp.array_enumerate(
        "mylist",
        "i",
        "elem",
        cpp.println("i", "elem"),
        declare_item=True,
        type=Primitive.String,
    )
    assert (
        str(e2)
        == """std::string elem;
int i;
for (i = 0; i < mylist.size(); i = i + 1) {
  elem = mylist[i];
  std::cout << i << elem << std::endl;
}"""
    )

    with pytest.raises(MissingTypeError) as err:
        str(
            cpp.array_enumerate(
                "mylist",
                "i",
                "elem",
                cpp.println("i", "elem"),
                declare_item=True,
            )
        )


def test_cpp_string_split():
    cpp = Cpp(Context(expand_tabs=True))
    assert (
        cpp.string_split(cpp.string("hello,world"), cpp.string(","))
        == """split_string("hello,world", ',')"""
    )
    assert len(cpp.helper_funcs) == 1
    f = cpp.helper_funcs["split_string"]
    assert str(f) == STRING_SPLIT_FUNC
    assert cpp.string_split("list", cpp.string(":")) == """split_string(list, ':')"""
    assert len(cpp.helper_funcs) == 1
    f = cpp.helper_funcs["split_string"]
    assert str(f) == STRING_SPLIT_FUNC
    should_import = ["sstream"]
    for imp in should_import:
        assert imp in cpp.imports


def test_cpp_array_remove():
    cpp = Cpp(Context(expand_tabs=True))
    assert cpp.array_remove("mylist", 0) == "mylist.erase(mylist.begin() + 0);"
    assert cpp.array_remove("mylist", 10) == "mylist.erase(mylist.begin() + 10);"
