import random
import time
import json
from tempfile import NamedTemporaryFile
import subprocess
import requests
import os
from pathlib import Path
import shutil

times = []


def timer(what: str, size: int, json_length: int, endpoint: str):
    def inner_timer(func):
        def wrap(*args, **kwargs):
            start = time.time()
            value = func(*args, **kwargs)
            end = time.time()
            runtime = end - start
            # msg = "{func} took {time} seconds to complete its execution."
            # print(msg.format(func=func.__name__, time=runtime))
            times.append([what, size, json_length, endpoint, runtime])
            return value

        return wrap

    return inner_timer


def bench_flex_bison(file: str):
    r = subprocess.run(
        f"./flex-bison-json/parser {file}", shell=True
    ).check_returncode()


def bench_antlr(file: str):
    subprocess.run(
        f'CLASSPATH="./antlr-json:/usr/local/lib/antlr-4.9.2-complete.jar:$CLASSPATH" java org.antlr.v4.gui.TestRig Json json {file}',
        shell=True,
    ).check_returncode()


def bench_rdpgen_python(file: str):
    subprocess.run(f"python parser.py {file}", shell=True).check_returncode()


def bench_rdpgen_cpp(file: str):
    subprocess.run(f"./parser_cpp {file}", shell=True).check_returncode()


def bench_rdpgen_go(file: str):
    subprocess.run(f"./parser_go {file}", shell=True).check_returncode()


def main():
    size = 1
    endpoint = "beer/random_beer"
    resp = requests.get(
        f"https://random-data-api.com/api/{endpoint}", params={"size": size}
    )
    data = resp.text
    print(data)
    f = NamedTemporaryFile("w", suffix=".json", delete=False)
    f.write(data)
    f.close()

    bison = timer("bison", size, len(data), endpoint)(bench_flex_bison)
    antlr = timer("antlr", size, len(data), endpoint)(bench_antlr)
    rdpgen_py = timer("rdpgen_python", size, len(data), endpoint)(bench_rdpgen_python)
    rdpgen_go = timer("rdpgen_go", size, len(data), endpoint)(bench_rdpgen_go)
    rdpgen_cpp = timer("rdpgen_cpp", size, len(data), endpoint)(bench_rdpgen_cpp)

    # bench the functions
    # bison(f.name)
    # antlr(f.name)

    subprocess.run("make --directory rdpgen-json/lexer cleanall", shell=True)
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, "rdpgen-json"))
    # rdpgen_py(f.name)
    # rdpgen_go(f.name)
    # rdpgen_cpp(f.name)
    os.chdir(cwd)

    print(times)

    os.remove(f.name)


if __name__ == "__main__":
    main()
