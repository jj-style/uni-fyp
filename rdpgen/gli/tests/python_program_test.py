from rdpgen.gli import *
from .python_progs import *
from .common import run_cmd
from tempfile import NamedTemporaryFile
import subprocess


def test_python_readlines_program():
    f1 = NamedTemporaryFile("w", delete=False, suffix=".py")
    for l in ["line1", "line2", "line3"]:
        f1.write(l + "\n")
    f1.close()

    prog = Program(Python(Context(expand_tabs=True)))
    p = prog.lang
    main = p.function(
        "main",
        None,
        None,
        p.declare("lines", Composite.array(Primitive.String)),
        p.assign("lines", p.read_lines(p.string(f1.name))),
        p.for_loop(
            "i",
            0,
            p.lt("i", p.array_length("lines")),
            p.increment("i"),
            p.println(p.index("lines", "i")),
        ),
    )
    prog.add(main)
    src = prog.generate()
    assert src == READ_LINES_PROGRAM(f1.name)

    f2 = NamedTemporaryFile("w")
    prog.write_file(f2.name)
    response = run_cmd(f"python3 {f2.name}")
    assert (
        response == "line1\n\nline2\n\nline3\n\n"
    )  # TODO: should we trim newline on read_lines??

    f2.close()
