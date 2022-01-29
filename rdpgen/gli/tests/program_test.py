from rdpgen.gli import Program, Language, Go, Context
from .go_progs import *
from .common import file_contains
from tempfile import NamedTemporaryFile


def test_go_prog_hello_world():
    go = Go(Context(expand_tabs=True))
    prog = Program(go)
    prog.add(go.function("main", None, None, go.println(go.string("hello world"))))
    assert prog.generate() == PROG_HELLO_WORLD


def test_prog_writes_file():
    go = Go(Context(expand_tabs=True))
    prog = Program(go)
    prog.add(go.function("main", None, None, go.println(go.string("hello world"))))

    outfile = NamedTemporaryFile("w")
    prog.write_file(outfile.name)

    assert file_contains(outfile.name, PROG_HELLO_WORLD)

    outfile.close()
