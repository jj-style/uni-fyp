import subprocess
import sys
from typing import List
from typing import get_type_hints
from rdpgen.gli import *


def read_lines(file: str) -> List[str]:
    f = open(file, "r")
    text = f.read()
    f.close()
    return text.splitlines()


tokens: List[List[str]]

symtab = {}
current_f = ""


def generate_tokens(file: str):
    command: str
    command = "cd lexer && make --silent && ./lexer "
    command = command + file
    response = subprocess.run(command, shell=True)
    if response.returncode != 0:
        exit(1)


def load_tokens():
    global tokens
    tokens = []
    token_lines: List[str]
    token_lines = read_lines("lexer/out.jl")
    idx: int
    for idx in range(len(token_lines)):
        tokens.append(token_lines[idx].split(""))


def peek() -> List[str]:
    if len(tokens) > 0:
        return tokens[0]
    return []


def get_token() -> List[str]:
    if len(tokens) > 0:
        next: List[str]
        next = tokens[0]
        tokens.pop(0)
        return next
    return []


def expect(line_num: str, e: str):
    print("Error: line ", line_num, "- expected ", e)
    exit(1)


def program():
    # program ::= function function_star
    function()
    function_star()


def function_star():
    # function_star ::= function function_star | "¬"
    next_token: List[str]
    next_token = peek()
    if next_token[0] == "type":
        function()
        function_star()


def function():
    # function ::= <type> "function" <identifier> "(" params ")" "{" block "}"
    next_token: List[str]
    next_token = get_token()
    if next_token[0] == "type":
        ret = next_token[1]
    else:
        expect(next_token[2], "type")
    next_token: List[str]
    next_token = get_token()
    if next_token[1] == "function":
        pass
    else:
        expect(next_token[2], "function")
    next_token: List[str]
    next_token = get_token()
    if next_token[0] == "identifier":
        ident = next_token[1]
        global current_f
        current_f = ident
        symtab[current_f] = {"args": []}
    else:
        expect(next_token[2], "identifier")
    next_token: List[str]
    next_token = get_token()
    if next_token[1] == "(":
        params()
    else:
        expect(next_token[2], "(")
    next_token: List[str]
    next_token = get_token()
    if next_token[1] == ")":
        pass
    else:
        expect(next_token[2], ")")
    next_token: List[str]
    next_token = get_token()
    if next_token[1] == "{":
        block()
    else:
        expect(next_token[2], "{")
    next_token: List[str]
    next_token = get_token()
    if next_token[1] == "}":
        pass
    else:
        expect(next_token[2], "}")

    tmap = {
        "int": Primitive.Int,
        "float": Primitive.Float,
        "string": Primitive.String,
        "bool": Primitive.Bool,
    }

    args = {arg["id"]: tmap[arg["type"]] for arg in symtab[current_f]["args"]}
    langs = [Go(), Python(expand_tabs=True), Cpp()]
    for l in langs:
        print(l.function(ident, tmap[ret], args, l.do_nothing()))


def params():
    # params ::= param param_star | "¬"
    next_token: List[str]
    next_token = peek()
    if next_token[0] == "type":
        param()
        param_star()


def param_star():
    # param_star ::= "," param param_star | "¬"
    next_token: List[str]
    next_token = peek()
    if next_token[1] == ",":
        next_token: List[str]
        next_token = get_token()
        if next_token[1] == ",":
            param()
            param_star()
        else:
            expect(next_token[2], ",")


def param():
    # param ::= <type> <identifier>
    next_token: List[str]
    next_token = get_token()
    param = {}
    if next_token[0] == "type":
        param["type"] = next_token[1]
    else:
        expect(next_token[2], "type")
    next_token: List[str]
    next_token = get_token()
    if next_token[0] == "identifier":
        param["id"] = next_token[1]
    else:
        expect(next_token[2], "identifier")
    symtab[current_f]["args"].append(param)


def block():
    # block ::= statement_star
    statement_star()


def statement_star():
    # statement_star ::= statement statement_star | "¬"
    next_token: List[str]
    next_token = peek()
    if next_token[0] == "identifier":
        statement()
        statement_star()


def statement():
    # statement ::= <identifier> ";"
    next_token: List[str]
    next_token = get_token()
    if next_token[0] == "identifier":
        pass
    else:
        expect(next_token[2], "identifier")
    next_token: List[str]
    next_token = get_token()
    if next_token[1] == ";":
        pass
    else:
        expect(next_token[2], ";")


def parse(file: str):
    generate_tokens(file)
    load_tokens()
    program()


def main():
    if len(sys.argv) < 2:
        print("usage: parser FILE")
        exit(1)
    filename: str
    filename = sys.argv[1]
    parse(filename)
    next_token: List[str]
    next_token = get_token()
    if next_token[0] != "EOF":
        expect(next_token[2], "EOF")


if __name__ == "__main__":
    main()
