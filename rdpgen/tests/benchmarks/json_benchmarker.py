import random
import time
import json
from tempfile import NamedTemporaryFile
import subprocess
import requests
import os
from pathlib import Path
import shutil
import csv

ENDPOINTS = [
    "beer/random_beer",
    "coffee/random_coffee",
    "bank/random_bank",
    "computer/random_computer",
    "food/random_food",
    "users/random_user",
]

times = {}


def timer(what: str, size: int, json_length: int, endpoint: str):
    def inner_timer(func):
        def wrap(*args, **kwargs):
            start = time.time()
            value = func(*args, **kwargs)
            end = time.time()
            runtime = end - start
            # msg = "{func} took {time} seconds to complete its execution."
            # print(msg.format(func=func.__name__, time=runtime))
            # times.append([what, size, json_length, endpoint, runtime])
            if str(size) not in times:
                times[str(size)] = {}
            times[str(size)][what] = {
                "time": runtime,
                "length": json_length,
            }
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
    for endpoint in ENDPOINTS[0:1]:
        for size in range(10, 110, 10):
            resp = requests.get(
                f"https://random-data-api.com/api/{endpoint}", params={"size": size}
            )
            data = resp.text

            f = NamedTemporaryFile("w", suffix=".json", delete=False)
            f.write(data)
            f.close()

            # create the functions with their timers
            bison = timer("bison", size, len(data), endpoint)(bench_flex_bison)
            antlr = timer("antlr", size, len(data), endpoint)(bench_antlr)
            rdpgen_py = timer("rdpgen_python", size, len(data), endpoint)(
                bench_rdpgen_python
            )
            rdpgen_go = timer("rdpgen_go", size, len(data), endpoint)(bench_rdpgen_go)
            rdpgen_cpp = timer("rdpgen_cpp", size, len(data), endpoint)(
                bench_rdpgen_cpp
            )

            # bench the functions
            bison(f.name)
            antlr(f.name)

            # clean pre-made stuff for rdpgen so it's fair
            for func in [rdpgen_py, rdpgen_go, rdpgen_cpp]:
                subprocess.run(
                    "make --silent --ignore-errors --directory rdpgen-json/lexer cleanall",
                    shell=True,
                )
                cwd = os.getcwd()
                os.chdir(os.path.join(cwd, "rdpgen-json"))
                func(f.name)
                os.chdir(cwd)

            os.remove(f.name)

    # print(times)
    with open("benchmarks.csv", "w") as outfile:
        writer = csv.writer(outfile)
        parsers = ["bison", "antlr", "rdpgen_python", "rdpgen_go", "rdpgen_cpp"]
        writer.writerow(["size", *parsers])
        for size, value in times.items():
            timings = [value[p]["time"] for p in parsers]
            row = [size, *timings]
            writer.writerow(row)


if __name__ == "__main__":
    here = Path(__file__).parent
    os.chdir(here)
    main()
