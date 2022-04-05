from rdpgen.ali import *


def test_language_convert_case():
    py_camel = Python(case="camel", expand_tabs=True, tab_size=2)
    py_snake = Python(case="snake", expand_tabs=True, tab_size=2)

    assert py_camel.declare("my_var", Primitive.Int) == "myVar: int"
    assert py_snake.declare("my_var", Primitive.Int) == "my_var: int"

    f1 = py_camel.function("doSomething", None, None, py_camel.do_nothing())
    assert f1 == "def doSomething():\n  pass"

    f2 = py_snake.function("doSomething", None, None, py_camel.do_nothing())
    assert f2 == "def do_something():\n  pass"


def test_language_expand_tabs():
    py_space = Python(expand_tabs=True, tab_size=4)
    py_tab = Python(expand_tabs=False)

    f1 = py_space.function("do_something", None, None, py_space.do_nothing())
    assert f1 == "def do_something():\n    pass"

    f2 = py_tab.function("do_something", None, None, py_tab.do_nothing())
    assert f2 == "def do_something():\n\tpass"


def test_language_tabs_size():
    py2 = Python(expand_tabs=True, tab_size=2)
    py4 = Python(expand_tabs=True, tab_size=4)

    f1 = py2.function("do_something", None, None, py2.do_nothing())
    assert f1 == "def do_something():\n  pass"

    f2 = py4.function("do_something", None, None, py4.do_nothing())
    assert f2 == "def do_something():\n    pass"
