HELLO_WORLD = """int main() {
  std::cout << "hello world" << std::endl;
  return 0;
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

ARRAY_DECLARE_ASSIGN = """int main() {
  std::vector<int> mylist;
  mylist = {1, 2, 3};
  std::cout << "mylist is " << mylist << std::endl;
  return 0;
}"""

HELLO_WORLD_PRELUDE = """#include <iostream>

"""

PROG_HELLO_WORLD = """#include <iostream>

int main() {
  std::cout << "hello world" << std::endl;
  return 0;
}

"""

MULTI_LINE_COMMENT = """/*
i am first line
i am second line
i am third line
*/
"""

INFINITE_LOOP = """while (1) {
  std::cout << "i am in an infinite loop" << std::endl;
}"""

WHILE_CONDITIONAL_LOOP = """int main() {
  int x;
  x = 0;
  while (x < 10) {
    std::cout << "x is" << x << std::endl;
    x = x + 1;
}
  return 0;
}"""

BUBBLE_SORT_PROG = """#include <iostream>
#include <vector>

std::vector<int> bubblesort(std::vector<int> arr) {
  int i;
  int j;
  int temp;
  for (i = 0; i < arr.size(); i = i + 1) {
    for (j = 0; j < arr.size() - i - 1; j = j + 1) {
      if (arr[j + 1] < arr[j]) {
        temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
}
}
}
  return arr;
}

int main() {
  std::vector<int> original;
  original = {5, 2, 4, 1, 3};
  std::vector<int> sorted;
  sorted = bubblesort(original);
  int i;
  for (i = 0; i < sorted.size(); i = i + 1) {
    std::cout << sorted[i] << " ";
}
  std::cout << std::endl;
  return 0;
}

"""

COMMAND_OUTPUT = """system("ls -l");"""
COMMAND_NO_OUTPUT = """system("ls -l > /dev/null 2>&1");"""
COMMAND_OUTPUT_WITH_EXIT = """int rc;
rc = system("ls -l");
if (rc != 0) {
  exit(1);
}"""

COMMAND_NO_OUTPUT_WITH_EXIT = """int rc;
rc = system("ls -l > /dev/null 2>&1");
if (rc != 0) {
  exit(1);
}"""
