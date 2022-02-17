# uni-fyp
University Final Year Project - Generating a Recursive Descent Parser

[![CI](https://github.com/jj-style/uni-fyp/actions/workflows/ci.yml/badge.svg)](https://github.com/jj-style/uni-fyp/actions/workflows/ci.yml)

## External Dependencies
- [flex](https://github.com/westes/flex)

## Installing
TODO (add setup.py)

```
parsergen grammar.toml output/directory [python|go|c++]
python parser.py $(realpath file/to/parse)
go run parser.go $(realpath file/to/parse)
g++ parser.cpp && ./a.out $(realpath file/to/parse)
```
