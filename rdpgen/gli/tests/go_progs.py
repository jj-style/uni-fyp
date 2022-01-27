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
