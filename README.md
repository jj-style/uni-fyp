# uni-fyp
University Final Year Project - Generating a Recursive Descent Parser

[![CI](https://github.com/jj-style/uni-fyp/actions/workflows/ci.yml/badge.svg)](https://github.com/jj-style/uni-fyp/actions/workflows/ci.yml)

## External Dependencies
- [flex](https://github.com/westes/flex)
- [libfl-dev]

## Installing
### From Source
```bash
git clone https://github.com/jj-style/uni-fyp
cd uni-fyp
pip install -e .
```

## Usage
Create a grammar config file with token and grammar rules for the lexer and parser respectively.
```toml
start = "program"   # optionally set start symbol of the grammar, defaults to the first one under [tokens]

[tokens]
IDENTIFIER = "[a-zA-Z_][a-zA-Z0-9_]*"
NUMBER = "[0-9]+"
SYMBOLS = "[=]"

[grammar]
PROGRAM = 'ASSIGN ASSIGN_PRIME'
ASSIGN_PRIME = 'ASSIGN ASSIGN_PRIME | "¬"'
ASSIGN = '<IDENTIFIER> "=" <NUMBER>'

[language_options]
expand_tabs=true
tab_size=4
case="camel" # snake

# language specific settings
[language_options.python]
declare_vars=false
```
Note in the tokens section, the `SYMBOLS` rule, you must add any rule with all the possible terminals that could occur to prevent a lexer error of unknown character. Alternatively you could specify all terminals as tokens.  

The grammar must be in BNF and the user is responsible for checking it is valid (e.g. not left-recursive).  
Use the terminal `"¬"` to represent *epsilon* (this character doesn't need to be defined in the lexer part).

```bash
parsergen grammar.toml output/directory [python|go|c++]
cd output/directory
python parser.py $(realpath file/to/parse)
go run parser.go $(realpath file/to/parse)
g++ parser.cpp && ./a.out $(realpath file/to/parse)
```
