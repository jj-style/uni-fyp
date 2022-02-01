HELLO_WORLD = """func main() {
  fmt.Println("hello world")
}"""

PRINT_VARIABLES = """func variables(arg1 int, arg2 string) {
  var x int
  x = 25
  fmt.Print("x is ", x)
  fmt.Println("arguments to function are ", arg1, arg2)
}"""

INNER_FUNC = """func function() {
  func inner(arg1 string) {
    fmt.Println("inner function")
}
}"""

FOR_LOOP = """for i = 0; i < 10; i = i + 1 {
  fmt.Println("i is ", i)
}"""

IF_ELSE = """if i == 0 {
  fmt.Println("i is zero")
} else {
  fmt.Println("i is not zero")
}"""

IF_NO_ELSE = """if mode == "debug" {
  fmt.Println("=== RUNNING IN DEBUG MODE ===")
}"""

ARRAY_DECLARE_ASSIGN = """func main() {
  var mylist []int
  mylist = []int{1, 2, 3}
  fmt.Println("mylist is ", mylist)
}"""

HELLO_WORLD_PRELUDE = """package main

import (
  "fmt"
)

"""

PROG_HELLO_WORLD = """package main

import (
  "fmt"
)

func main() {
  fmt.Println("hello world")
}"""

MULTI_LINE_COMMENT = """/*
i am first line
i am second line
i am third line
*/
"""

INFINITE_LOOP = """for {
  fmt.Println("i am in an infinite loop")
}"""

WHILE_CONDITIONAL_LOOP = """func main() {
  var x int
  x = 0
  for {
    if !(x < 10) {
      break
}
    fmt.Println("x is", x)
    x = x + 1
}
}"""

BUBBLE_SORT_PROG = """package main

import (
  "fmt"
)

func bubblesort(arr []int) []int {
  var i int
  var j int
  var temp int
  for i = 0; i < len(arr); i = i + 1 {
    for j = 0; j < len(arr) - i - 1; j = j + 1 {
      if arr[j+1] < arr[j] {
        temp = arr[j]
        arr[j] = arr[j+1]
        arr[j+1] = temp
      } 
    }
  }
  return arr
}

func main() {
  var original []int
  original = []int{5, 2, 4, 1, 3}
  var sorted []int
  sorted = bubblesort(original)
  var i int
  for i = 0; i < len(sorted); i = i + 1 {
    fmt.Print(sorted[i], " ")
  }
  fmt.Println()
}
"""