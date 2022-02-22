from rdpgen.gli import *
from .python_progs import READ_LINES_PROGRAM as PY_SRC
from .go_progs import READ_LINES_PROGRAM as GO_SRC
from .cpp_progs import READ_LINES_PROGRAM as CPP_SRC
from .common import run_cmd
from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path


def create_readlines_program(lang, filename):
    prog = Program(lang)
    p = prog.lang
    main = p.function(
        "main",
        None,
        None,
        p.declare("lines", Composite.array(Primitive.String)),
        p.assign("lines", p.read_lines(p.string(filename))),
        p.declare("i", Primitive.Int),
        p.for_loop(
            "i",
            0,
            p.lt("i", p.array_length("lines")),
            p.increment("i"),
            p.println(p.index("lines", "i")),
        ),
    )
    prog.add(main)
    return prog


def test_read_lines_program():
    f1 = NamedTemporaryFile("w", delete=False)
    for l in ["line1", "line2", "line3"]:
        f1.write(l + "\n")
    f1.close()
    tests = {
        "python": {
            "lang": Python(expand_tabs=True, tab_size=2),
            "suffix": ".py",
            "cmd": "python3 _",
            "src": PY_SRC(f1.name),
        },
        "go": {
            "lang": Go(expand_tabs=True, tab_size=2),
            "suffix": ".go",
            "cmd": "go run _",
            "src": GO_SRC(f1.name),
        },
        "cpp": {
            "lang": Cpp(expand_tabs=True, tab_size=2),
            "suffix": ".cpp",
            "cmd": "cd ~ && g++ _ && ./a.out",
            "src": CPP_SRC(f1.name),
        },
    }

    for opts in tests.values():
        prog = create_readlines_program(opts["lang"], f1.name)

        # check src matches
        src = prog.generate()
        assert src == opts["src"]

        # write out and run asserting the output from the program is as expected
        f2 = NamedTemporaryFile("w", suffix=opts["suffix"], delete=False)
        prog.write_file(f2.name)

        cmd = opts["cmd"].replace("_", f2.name)
        cmd = cmd.replace("~", str(Path(f2.name).parent))
        assert run_cmd(cmd) == "line1\nline2\nline3\n"

        f2.close()
