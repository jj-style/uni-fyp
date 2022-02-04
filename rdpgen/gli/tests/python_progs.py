HELLO_WORLD = """def main():
  print("hello world")"""

PRINT_VARIABLES = """def variables(arg1: int, arg2: str):
  x: int
  x = 25
  print("x is ", x, end="")
  print("arguments to function are ", arg1, arg2)"""

INNER_FUNC = """def function():
  def inner(arg1: str):
    print("inner function")"""

FOR_LOOP_GENERIC = """i = 0
while True:
  if not (i < 10):
    break
  print("i is ", i)
  i = doSomething(i)"""

FOR_LOOP_RANGED_INC = """for i in range(0, 10, 1):
  print("in a classic python for loop")"""

FOR_LOOP_RANGED_DEC = """for i in range(10, 0, -1):
  print("in a decreasing python for loop")"""

IF_ELSE = """if i == 0:
  print("i is zero")
else:
  print("i is not zero")"""

IF_NO_ELSE = """if mode == "debug":
  print("=== RUNNING IN DEBUG MODE ===")"""

ARRAY_DECLARE_ASSIGN = """def main():
  mylist: List[int]
  mylist = [1, 2, 3]
  print("mylist is ", mylist)"""

HELLO_WORLD_PRELUDE = """

"""

PROG_HELLO_WORLD = """

def main():
  print("hello world")

if __name__ == "__main__":
  main()"""

MULTI_LINE_COMMENT = """\"\"\"
i am first line
i am second line
i am third line
\"\"\"
"""

INFINITE_LOOP = """while True:
  print("i am in an infinite loop")"""

WHILE_CONDITIONAL_LOOP = """def main():
  x: int
  x = 0
  while True:
    if not (x < 10):
      break
    print("x is", x)
    x = x + 1"""

BUBBLE_SORT_PROG = """from typing import List
from typing import get_type_hints


def bubblesort(arr: List[int]) -> List[int]:
  i: int
  j: int
  temp: int
  for i in range(0, len(arr), 1):
    for j in range(0, len(arr) - i - 1, 1):
      if arr[j + 1] < arr[j]:
        temp = arr[j]
        arr[j] = arr[j + 1]
        arr[j + 1] = temp
  return arr

def main():
  original: List[int]
  original = [5, 2, 4, 1, 3]
  sorted: List[int]
  sorted = bubblesort(original)
  i: int
  for i in range(0, len(sorted), 1):
    print(sorted[i], " ", end="")
  print()

if __name__ == "__main__":
  main()"""
