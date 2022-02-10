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
}

"""

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
      if arr[j + 1] < arr[j] {
        temp = arr[j]
        arr[j] = arr[j + 1]
        arr[j + 1] = temp
      }
    }
  }
  return arr
}

func main() {
  var original []int
  original = []int{9, 6, 7, 4, 5}
  var sorted []int
  sorted = bubblesort(original)
  var i int
  for i, _ = range sorted {
    fmt.Print(sorted[i], " ")
  }
  fmt.Println()
}

"""

COMMAND_NO_OUTPUT = """var cmd *exec.Cmd
cmd = exec.Command("ls", "-l")
_ = cmd.Run()"""

COMMAND_NO_OUTPUT_WITH_EXIT = """var cmd *exec.Cmd
var err error
cmd = exec.Command("ls", "-l")
err = cmd.Run()
if err != nil {
  os.Exit(1)
}"""

COMMAND_OUTPUT = """var out []byte
out, _ = exec.Command("ls", "-l").Output()
fmt.Println(string(out))"""

COMMAND_OUTPUT_WITH_EXIT = """var out []byte
var err error
out, err = exec.Command("ls", "-l").Output()
if err != nil {
  os.Exit(1)
}
fmt.Println(string(out))"""

READ_LINES_FUNC = """func readLines(file string) []string {
  var f *os.File
  var err error
  f, err = os.Open(file)
  if err != nil {
    os.Exit(1)
  }
  var scanner *bufio.Scanner
  scanner = bufio.NewScanner(f)
  scanner.Split(bufio.ScanLines)
  var lines []string
  for scanner.Scan() {
    lines = append(lines, scanner.Text())
  }
  f.Close()
  return lines
}"""


def READ_LINES_PROGRAM(fname: str):
    return (
        """package main

import (
  "bufio"
  "fmt"
  "os"
)

func readLines(file string) []string {
  var f *os.File
  var err error
  f, err = os.Open(file)
  if err != nil {
    os.Exit(1)
  }
  var scanner *bufio.Scanner
  scanner = bufio.NewScanner(f)
  scanner.Split(bufio.ScanLines)
  var lines []string
  for scanner.Scan() {
    lines = append(lines, scanner.Text())
  }
  f.Close()
  return lines
}

func main() {
  var lines []string
  lines = readLines("%s")
  var i int
  for i = 0; i < len(lines); i = i + 1 {
    fmt.Println(lines[i])
  }
}

"""
        % fname
    )


def READ_FILE_PROGRAM(fname: str):
    return (
        """package main

import (
  "fmt"
  "io/ioutil"
  "os"
)

func readFile(file string) string {
  var content []byte
  var err error
  content, err = ioutil.ReadFile(file)
  if err != nil {
    fmt.Println(err)
    os.Exit(1)
  }
  return string(content)
}

func main() {
  var text string
  text = readFile("%s")
  fmt.Println(text)
}

"""
        % fname
    )
