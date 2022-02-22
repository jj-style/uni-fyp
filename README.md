# uni-fyp
University Final Year Project - Generating a Recursive Descent Parser

[![CI](https://github.com/jj-style/uni-fyp/actions/workflows/ci.yml/badge.svg)](https://github.com/jj-style/uni-fyp/actions/workflows/ci.yml)

## External Dependencies
- [flex](https://github.com/westes/flex)

## Installing
TODO (add setup.py)

## Usage
Create a grammar config file with token and grammar rules for the lexer and parser respectively.
```toml
[tokens]
IDENTIFIER = "[a-zA-Z_][a-zA-Z0-9_]*"
NUMBER = "[0-9]+"
SYMBOLS = "[=]"

[grammar]
PROGRAM = 'ASSIGN ASSIGN_PRIME'
ASSIGN_PRIME = 'ASSIGN ASSIGN_PRIME | "¬"'
ASSIGN = '<IDENTIFIER> "=" <NUMBER>'
```
Note in the tokens section, the `SYMBOLS` rule, you must add any rule with all the possible terminals that could occur to prevent a lexer error of unknown character. Alternatively you could specify all terminals as tokens.  

The grammar must be in BNF and the user is responsible for checking it is valid (e.g. not left-recursive).  
Use the terminal `"¬"` to represent *epsilon* (this character doesn't need to be defined in the lexer part).

```bash
parsergen grammar.toml output/directory [python|go|c++]
python parser.py $(realpath file/to/parse)
go run parser.go $(realpath file/to/parse)
g++ parser.cpp && ./a.out $(realpath file/to/parse)
```
