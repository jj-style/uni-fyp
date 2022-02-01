HELLO_WORLD = """void main() {
  std::cout << "hello world" << std::endl;
}"""

PRINT_VARIABLES = """void variables(int arg1, std::string arg2) {
  int x;
  x = 25;
  std::cout << "x is " << x;
  std::cout << "arguments to function are " << arg1 << arg2 << std::endl;
}"""


FOR_LOOP = """for (i = 0; i < 10; i = i + 1) {
  std::cout << "i is " << i << std::endl;
}"""

IF_ELSE = """if (i == 0) {
  std::cout << "i is zero" << std::endl;
} else {
  std::cout << "i is not zero" << std::endl;
}"""

IF_NO_ELSE = """if (mode == "debug") {
  std::cout << "=== RUNNING IN DEBUG MODE ===" << std::endl;
}"""

ARRAY_DECLARE_ASSIGN = """void main() {
  std::vector<int> mylist;
  mylist = {1, 2, 3};
  std::cout << "mylist is " << mylist << std::endl;
}"""

HELLO_WORLD_PRELUDE = """#include <iostream>

"""

PROG_HELLO_WORLD = """#include <iostream>

void main() {
  std::cout << "hello world" << std::endl;
}"""

MULTI_LINE_COMMENT = """/*
i am first line
i am second line
i am third line
*/
"""

INFINITE_LOOP = """while (1) {
  std::cout << "i am in an infinite loop" << std::endl;
}"""

WHILE_CONDITIONAL_LOOP = """void main() {
  int x;
  x = 0;
  while (x < 10) {
    std::cout << "x is" << x << std::endl;
    x = x + 1;
}
}"""
