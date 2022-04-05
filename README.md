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
### Parser Generator
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
rdpgen grammar.toml output/directory [python|go|c++]
cd output/directory
python parser.py $(realpath file/to/parse)
go run parser.go $(realpath file/to/parse)
g++ parser.cpp && ./a.out $(realpath file/to/parse)
```

### Abstract Language Interface (ALI)
```python
from rdpgen.ali import Program, Primitive, Composite, Python, Go, Cpp

languages = [Python(), Go(), Cpp()]
for l in languages:
    prog = Program(l)
    main = l.function("main", None, None,
        l.println(l.s("hello world!"))
    )
    prog.add(main)
    print(prog.generate())


"""
def main():
        print("hello world!")

if __name__ == "__main__":
        main()

package main

import (
    "fmt"
)

func main() {
    fmt.Println("hello world!")
}


#include <iostream>

int main(int argc, char* argv[]) {
  std::cout << "hello world!" << std::endl;
  return 0;
}
"""
```

## Warning
Please note, this is an exploratory project and the code generation is not tested for production code.  
 
If you wish to use this library for code generation, you are strongly advised to review and test the generated code before running it.  
By using this project, you are responsible and I take no responsibility for the resultant action of generated code.