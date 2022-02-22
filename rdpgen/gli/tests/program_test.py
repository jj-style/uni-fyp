from rdpgen.gli import Program, Language, Go, Cpp, Composite, Primitive, Python
from .common import file_contains, run_cmd
from tempfile import NamedTemporaryFile
from pathlib import Path

from .go_progs import PROG_HELLO_WORLD as GO_PROG_HELLO_WORLD
from .go_progs import BUBBLE_SORT_PROG as GO_BUBBLE_SORT_PROG
from .cpp_progs import PROG_HELLO_WORLD as CPP_PROG_HELLO_WORLD
from .cpp_progs import BUBBLE_SORT_PROG as CPP_BUBBLE_SORT_PROG
from .python_progs import BUBBLE_SORT_PROG as PYTHON_BUBBLE_SORT_PROG
from .python_progs import PROG_HELLO_WORLD as PYTHON_HELLO_WORLD


def test_go_prog_hello_world():
    go = Go(expand_tabs=True, tab_size=2)
    prog = Program(go)
    prog.add(go.function("main", None, None, go.println(go.string("hello world"))))
    assert prog.generate() == GO_PROG_HELLO_WORLD


def test_go_prog_writes_file():
    go = Go(expand_tabs=True, tab_size=2)
    prog = Program(go)
    prog.add(go.function("main", None, None, go.println(go.string("hello world"))))

    outfile = NamedTemporaryFile("w")
    prog.write_file(outfile.name)

    assert file_contains(outfile.name, GO_PROG_HELLO_WORLD)

    outfile.close()


def test_cpp_prog_hello_world():
    cpp = Cpp(expand_tabs=True, tab_size=2)
    prog = Program(cpp)
    prog.add(cpp.function("main", None, None, cpp.println(cpp.string("hello world"))))
    assert prog.generate() == CPP_PROG_HELLO_WORLD


def test_cpp_prog_writes_file():
    cpp = Cpp(expand_tabs=True, tab_size=2)
    prog = Program(cpp)
    prog.add(cpp.function("main", None, None, cpp.println(cpp.string("hello world"))))

    outfile = NamedTemporaryFile("w")
    prog.write_file(outfile.name)

    assert file_contains(outfile.name, CPP_PROG_HELLO_WORLD)

    outfile.close()


def test_python_prog_hello_world():
    p = Python(expand_tabs=True, tab_size=2)
    prog = Program(p)
    prog.add(p.function("main", None, None, p.println(p.string("hello world"))))
    assert prog.generate() == PYTHON_HELLO_WORLD


def test_bubblesort():
    go = Go(expand_tabs=True, tab_size=2)
    cpp = Cpp(expand_tabs=True, tab_size=2)
    py = Python(expand_tabs=True, tab_size=2)
    language_source = {
        go: {
            "src": GO_BUBBLE_SORT_PROG,
            "cmd": "go run _",
            "out": "4 5 6 7 9 \n",
            "suffix": ".go",
        },
        cpp: {
            "src": CPP_BUBBLE_SORT_PROG,
            "cmd": "cd ~ && g++ _ && ./a.out",
            "out": "4 5 6 7 9 \n",
            "suffix": ".cpp",
            "clean": ["~/a.out"],
        },
        py: {
            "src": PYTHON_BUBBLE_SORT_PROG,
            "cmd": "python3 _",
            "out": "4  5  6  7  9  \n",
            "suffix": ".py",
        },
    }
    for g, test in language_source.items():
        prog = Program(g)
        main = g.function(
            "main",
            None,
            None,
            g.declare("original", Composite.array(Primitive.Int)),
            g.assign("original", g.array(Primitive.Int, [9, 6, 7, 4, 5])),
            g.declare("sorted", Composite.array(Primitive.Int)),
            g.assign("sorted", g.call("bubblesort", "original")),
            g.array_iterate(
                "sorted", "i", g.print(g.index("sorted", "i"), g.string(" "))
            ),
            g.println(),
        )
        bubblesort = g.function(
            "bubblesort",
            Composite.array(Primitive.Int),
            {"arr": Composite.array(Primitive.Int)},
            g.declare("i", Primitive.Int),
            g.declare("j", Primitive.Int),
            g.declare("temp", Primitive.Int),
            g.for_loop(
                "i",
                0,
                g.lt("i", g.array_length("arr")),
                g.increment("i"),
                g.for_loop(
                    "j",
                    0,
                    g.lt("j", g.sub(g.sub(g.array_length("arr"), "i"), "1")),
                    g.increment("j"),
                    g.if_else(
                        g.lt(g.index("arr", g.add("j", 1)), g.index("arr", "j")),
                        [
                            g.assign("temp", g.index("arr", "j")),
                            g.assign(
                                g.index("arr", "j"), g.index("arr", g.add("j", 1))
                            ),
                            g.assign(g.index("arr", g.add("j", 1)), "temp"),
                        ],
                    ),
                ),
            ),
            g.do_return(expression="arr"),
        )
        prog.add(bubblesort)
        prog.add(main)
        assert prog.generate() == test["src"]

        # test execution of program
        outfile = NamedTemporaryFile("w", suffix=test["suffix"])
        prog.write_file(outfile.name)

        cmd = test["cmd"].replace("_", outfile.name)
        cmd = cmd.replace("~", str(Path(outfile.name).parent))
        assert run_cmd(cmd) == test["out"]

        to_clean = test.get("clean", [])
        for f in to_clean:
            p = Path(f.replace("~", str(Path(outfile.name).parent)))
            if p.exists():
                p.unlink()

        outfile.close()
