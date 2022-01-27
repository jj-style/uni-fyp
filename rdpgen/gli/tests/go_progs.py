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
