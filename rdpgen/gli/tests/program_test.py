from rdpgen.gli import Program, Language, Go, Context, Cpp
from .go_progs import PROG_HELLO_WORLD as GO_PROG_HELLO_WORLD
from .cpp_progs import PROG_HELLO_WORLD as CPP_PROG_HELLO_WORLD
from .common import file_contains
from tempfile import NamedTemporaryFile


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
