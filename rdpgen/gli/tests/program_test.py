from rdpgen.gli import Program, Language, Go, Context, Cpp, Composite, Primitive
from .go_progs import PROG_HELLO_WORLD as GO_PROG_HELLO_WORLD
from .go_progs import BUBBLE_SORT_PROG as GO_BUBBLE_SORT_PROG
from .cpp_progs import PROG_HELLO_WORLD as CPP_PROG_HELLO_WORLD
from .cpp_progs import BUBBLE_SORT_PROG as CPP_BUBBLE_SORT_PROG
from .common import file_contains, run_cmd
from tempfile import NamedTemporaryFile
from pathlib import Path


def test_go_prog_hello_world():
    go = Go(Context(expand_tabs=True))
    prog = Program(go)
    prog.add(go.function("main", None, None, go.println(go.string("hello world"))))
    assert prog.generate() == GO_PROG_HELLO_WORLD


def test_go_prog_writes_file():
    go = Go(Context(expand_tabs=True))
    prog = Program(go)
    prog.add(go.function("main", None, None, go.println(go.string("hello world"))))

    outfile = NamedTemporaryFile("w")
    prog.write_file(outfile.name)

    assert file_contains(outfile.name, GO_PROG_HELLO_WORLD)

    outfile.close()


def test_cpp_prog_hello_world():
    cpp = Cpp(Context(expand_tabs=True))
    prog = Program(cpp)
    prog.add(cpp.function("main", None, None, cpp.println(cpp.string("hello world"))))
    assert prog.generate() == CPP_PROG_HELLO_WORLD


def test_cpp_prog_writes_file():
    cpp = Cpp(Context(expand_tabs=True))
    prog = Program(cpp)
    prog.add(cpp.function("main", None, None, cpp.println(cpp.string("hello world"))))

    outfile = NamedTemporaryFile("w")
    prog.write_file(outfile.name)

    assert file_contains(outfile.name, CPP_PROG_HELLO_WORLD)

    outfile.close()


def test_bubblesort():
    go = Go(Context(expand_tabs=True))
    cpp = Cpp(Context(expand_tabs=True))
    language_source = {
        go: {
            "src": GO_BUBBLE_SORT_PROG,
            "cmd": "go run _",
            "out": "1 2 3 4 5 \n",
            "suffix": ".go",
        },
        cpp: {
            "src": CPP_BUBBLE_SORT_PROG,
            "cmd": "cd ~ && g++ _ && ./a.out",
            "out": "1 2 3 4 5 \n",
            "suffix": ".cpp",
            "clean": ["~/a.out"],
        },
    }
    for g, test in language_source.items():
        prog = Program(g)
        main = g.function(
            "main",
            None,
            None,
            g.declare("original", Composite.array(Primitive.Int)),
            g.assign("original", g.array(Primitive.Int, [5, 2, 4, 1, 3])),
            g.declare("sorted", Composite.array(Primitive.Int)),
            g.assign("sorted", g.call("bubblesort", "original")),
            g.declare("i", Primitive.Int),
            g.for_loop(
                "i",
                0,
                g.lt("i", g.array_length("sorted")),
                g.increment("i"),
                g.print(g.index("sorted", "i"), g.string(" ")),
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
