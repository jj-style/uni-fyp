from rdpgen.gli import *
from .python_progs import READ_FILE_PROGRAM as PY_SRC
from .go_progs import READ_FILE_PROGRAM as GO_SRC
from .cpp_progs import READ_FILE_PROGRAM as CPP_SRC
from .common import run_cmd
from tempfile import NamedTemporaryFile
import subprocess
from pathlib import Path


def create_readfile_program(lang, filename):
    prog = Program(lang)
    p = prog.lang
    main = p.function(
        "main",
        None,
        None,
        p.declare("text", Primitive.String),
        p.assign("text", p.read_file(p.string(filename))),
        p.println("text"),
    )
    prog.add(main)
    return prog


def test_read_file_program():
    f1 = NamedTemporaryFile("w", delete=False)
    for l in ["line1", "line2", "line3"]:
        f1.write(l + "\n")
    f1.close()
    tests = {
        "python": {
            "lang": Python(Context(expand_tabs=True)),
            "suffix": ".py",
            "cmd": "python3 _",
            "src": PY_SRC(f1.name),
        },
        "go": {
            "lang": Go(Context(expand_tabs=True)),
            "suffix": ".go",
            "cmd": "go run _",
            "src": GO_SRC(f1.name),
        },
        "cpp": {
            "lang": Cpp(Context(expand_tabs=True)),
            "suffix": ".cpp",
            "cmd": "cd ~ && g++ _ && ./a.out",
            "src": CPP_SRC(f1.name),
        },
    }

    for opts in tests.values():
        prog = create_readfile_program(opts["lang"], f1.name)

        # check src matches
        src = prog.generate()
        assert src == opts["src"]

        # write out and run asserting the output from the program is as expected
        f2 = NamedTemporaryFile("w", suffix=opts["suffix"], delete=False)
        prog.write_file(f2.name)

        cmd = opts["cmd"].replace("_", f2.name)
        cmd = cmd.replace("~", str(Path(f2.name).parent))
        assert run_cmd(cmd) == "line1\nline2\nline3\n\n"

        f2.close()
