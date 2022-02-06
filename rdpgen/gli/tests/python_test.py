from rdpgen.gli import Python, Context, Primitive, Composite, MissingTypeError
from .python_progs import *
from tempfile import NamedTemporaryFile
from pathlib import Path
import pytest


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
    assert str(p.postlude()) == """if __name__ == "__main__":\n  main()"""


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


def test_python_for_loop_generic():
    p = Python(Context(expand_tabs=True))
    f = p.for_loop(
        "i",
        0,
        p.lt("i", 10),
        p.assign("i", p.call("doSomething", "i")),
        p.println(p.string("i is "), "i"),
    )
    assert f == FOR_LOOP_GENERIC


def test_python_for_loop_ranged():
    p = Python(Context(expand_tabs=True))
    inc = p.for_loop(
        "i",
        0,
        p.lt("i", 10),
        p.increment("i"),
        p.println(p.string("in a classic python for loop")),
    )
    assert str(inc) == FOR_LOOP_RANGED_INC

    dec = p.for_loop(
        "i",
        10,
        p.gt("i", 0),
        p.decrement("i"),
        p.println(p.string("in a decreasing python for loop")),
    )
    assert str(dec) == FOR_LOOP_RANGED_DEC


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
    assert p.types(Composite.array(Primitive.Int)) == "List[int]"
    assert p.types(Composite.array(Primitive.String)) == "List[str]"


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
    assert p.comment("i am a comment") == "# i am a comment"


def test_python_comment_multiline():
    p = Python(Context(expand_tabs=True))
    assert (
        p.comment("i am first line\ni am second line\ni am third line")
        == MULTI_LINE_COMMENT
    )


def test_python_while_true_loop():
    p = Python(Context(expand_tabs=True))
    loop = p.while_loop(p.println(p.string("i am in an infinite loop")))
    assert str(loop) == INFINITE_LOOP


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


def test_python_command():
    p = Python(Context(expand_tabs=True))

    # test it produces correct call for running ls -l
    c = p.command("ls -l", exit_on_failure=False)
    assert "subprocess" in p.imports
    assert (
        c
        == """subprocess.run("ls -l", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)"""
    )

    # test without supressing output
    c = p.command("ls -l", suppress_output=False, exit_on_failure=False)
    assert c == """subprocess.run("ls -l", shell=True)"""

    # get a write-only file, run command to write text to it and check it now contains text
    file = NamedTemporaryFile("w")
    path = Path(file.name)
    assert path.exists()
    assert path.read_text() == ""
    cmd = p.command(f'echo "some text" > {str(path)}', exit_on_failure=False)
    assert (
        cmd
        == f"""subprocess.run("echo \\"some text\\" > {str(path)}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)"""
    )
    import subprocess

    eval(cmd)  # run the command
    assert path.read_text() == "some text\n"

    file.close()


def test_python_command_exit_on_failure():
    p = Python(Context(expand_tabs=True))
    file = "/some/random/file/that/probably/doesnt/exist"
    c = p.command(f"cat {file}", exit_on_failure=False, suppress_output=False)
    assert str(c) == f"""subprocess.run("cat {file}", shell=True)"""

    c = p.command(f"cat {file}", exit_on_failure=True, suppress_output=False)
    assert (
        str(c)
        == f"""response = subprocess.run("cat {file}", shell=True)\nif response.returncode != 0:\n  exit(1)"""
    )


def test_python_exit():
    p = Python(Context(expand_tabs=True))
    assert p.exit() == "exit(0)"
    cases = range(100)
    for c in cases:
        assert p.exit(c) == f"exit({c})"


def test_python_read_lines():
    p = Python(Context(expand_tabs=True))
    p.read_lines("myfile.txt")
    p.read_lines("myfile.txt")
    assert len(p.helper_funcs) == 1

    lines = p.assign("lines", p.read_lines(p.string("file.txt")))
    assert lines == 'lines = read_lines("file.txt")'
    f = str(p.helper_funcs["read_lines"])
    assert f == READ_LINES_FUNC


def test_python_array_append():
    p = Python(Context(expand_tabs=True))
    assert p.array_append("mylist", 5) == "mylist.append(5)"
    assert p.array_append("mylist", p.string("5")) == 'mylist.append("5")'


def test_python_boolean_and():
    p = Python(Context(expand_tabs=True))
    assert p.bool_and(p.gt("x", 10), p.lt("x", 20)) == "x > 10 and x < 20"


def test_python_boolean_or():
    p = Python(Context(expand_tabs=True))
    assert p.bool_or(p.lt("x", 10), p.gt("x", 20)) == "x < 10 or x > 20"


def test_python_array_iterate():
    p = Python(Context(expand_tabs=True))
    i1 = p.array_iterate("mylist", "i", p.println("i"))
    assert (
        i1
        == """i: int
for i in range(len(mylist)):
  print(i)"""
    )

    i2 = p.array_iterate("mylist", "i", p.println("i"), declare_it=False)
    assert (
        i2
        == """for i in range(len(mylist)):
  print(i)"""
    )

    i3 = p.array_iterate(
        "mylist",
        "elem",
        p.println("elem"),
        iterate_items=True,
        type=Primitive.String,
    )
    assert (
        i3
        == """elem: str
for elem in mylist:
  print(elem)"""
    )

    with pytest.raises(MissingTypeError) as err:
        str(p.array_iterate("mylist", "elem", p.println("elem"), iterate_items=True))


def test_python_array_enumerate():
    p = Python(Context(expand_tabs=True))

    e1 = p.array_enumerate("mylist", "i", "elem", p.println("i", "elem"))
    assert (
        str(e1)
        == """i: int
for i, elem in enumerate(mylist):
  print(i, elem)"""
    )

    e2 = p.array_enumerate(
        "mylist",
        "i",
        "elem",
        p.println("i", "elem"),
        declare_item=True,
        type=Primitive.String,
    )
    assert (
        str(e2)
        == """i: int
elem: str
for i, elem in enumerate(mylist):
  print(i, elem)"""
    )

    with pytest.raises(MissingTypeError) as err:
        str(
            p.array_enumerate(
                "mylist",
                "i",
                "elem",
                p.println("i", "elem"),
                declare_item=True,
            )
        )


def test_python_string_split():
    p = Python(Context(expand_tabs=True))
    assert (
        p.string_split(p.string("hello,world"), p.string(","))
        == """"hello,world".split(",")"""
    )
    assert p.string_split("list", p.string(":")) == """list.split(":")"""
