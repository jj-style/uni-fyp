package main

import (
    "bufio"
    "fmt"
    "os"
    "os/exec"
    "strings"
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

var tokens [][]string

func generateTokens(file string) {
    var command string
    command = "cd lexer && make --silent && ./lexer "
    command = command + file
    var out []byte
    var err error
    out, err = exec.Command("bash", "-c", command).Output()
    if err != nil {
        os.Exit(1)
    }
    fmt.Println(string(out))
}

func loadTokens() {
    tokens = [][]string{}
    var tokenLines []string
    tokenLines = readLines("lexer/out.jl")
    var idx int
    for idx, _ = range tokenLines {
        tokens = append(tokens, strings.Split(tokenLines[idx], ""))
    }
}

func peek() []string {
    if len(tokens) > 0 {
        return tokens[0]
    }
    return []string{}
}

func getToken() []string {
    if len(tokens) > 0 {
        var next []string
        next = tokens[0]
        tokens = append(tokens[:0], tokens[1:]...)
        return next
    }
    return []string{}
}

func expect(line_num string, e string) {
    fmt.Println("Error: line ", line_num, "- expected ", e)
    os.Exit(1)
}

func json() {
    // json ::= object | array
    var nextToken []string
    nextToken = peek()
    if nextToken[1] == "{" {
        object()
    } else if nextToken[1] == "[" {
        array()
    } else {
        expect(nextToken[2], "{,[")
    }
}

func object() {
    // object ::= "{" pairs "}"
    var nextToken []string
    nextToken = getToken()
    if nextToken[1] == "{" {
        pairs()
    } else {
        expect(nextToken[2], "{")
    }
    var nextToken1 []string
    nextToken1 = getToken()
    if nextToken1[1] == "}" {
        
    } else {
        expect(nextToken1[2], "}")
    }
}

func pairs() {
    // pairs ::= pair pairs_tail | "¬"
    var nextToken []string
    nextToken = peek()
    if nextToken[0] == "STRING" {
        pair()
        pairsTail()
    }
}

func pair() {
    // pair ::= <STRING> ":" value
    var nextToken2 []string
    nextToken2 = getToken()
    if nextToken2[0] == "STRING" {
        
    } else {
        expect(nextToken2[2], "STRING")
    }
    var nextToken3 []string
    nextToken3 = getToken()
    if nextToken3[1] == ":" {
        value()
    } else {
        expect(nextToken3[2], ":")
    }
}

func pairsTail() {
    // pairs_tail ::= "," pairs | "¬"
    var nextToken []string
    nextToken = peek()
    if nextToken[1] == "," {
        var nextToken4 []string
        nextToken4 = getToken()
        if nextToken4[1] == "," {
            pairs()
        } else {
            expect(nextToken4[2], ",")
        }
    }
}

func value() {
    // value ::= <STRING> | <NUMBER> | <TRUE> | <FALSE> | <NULL> | object | array
    var nextToken []string
    nextToken = peek()
    if nextToken[0] == "STRING" {
        var nextToken5 []string
        nextToken5 = getToken()
        if nextToken5[0] == "STRING" {
            
        } else {
            expect(nextToken5[2], "STRING")
        }
    } else if nextToken[0] == "NUMBER" {
        var nextToken6 []string
        nextToken6 = getToken()
        if nextToken6[0] == "NUMBER" {
            
        } else {
            expect(nextToken6[2], "NUMBER")
        }
    } else if nextToken[0] == "TRUE" {
        var nextToken7 []string
        nextToken7 = getToken()
        if nextToken7[0] == "TRUE" {
            
        } else {
            expect(nextToken7[2], "TRUE")
        }
    } else if nextToken[0] == "FALSE" {
        var nextToken8 []string
        nextToken8 = getToken()
        if nextToken8[0] == "FALSE" {
            
        } else {
            expect(nextToken8[2], "FALSE")
        }
    } else if nextToken[0] == "NULL" {
        var nextToken9 []string
        nextToken9 = getToken()
        if nextToken9[0] == "NULL" {
            
        } else {
            expect(nextToken9[2], "NULL")
        }
    } else if nextToken[1] == "{" {
        object()
    } else if nextToken[1] == "[" {
        array()
    } else {
        expect(nextToken[2], "STRING,NUMBER,TRUE,FALSE,NULL,{,[")
    }
}

func array() {
    // array ::= "[" elements "]"
    var nextToken10 []string
    nextToken10 = getToken()
    if nextToken10[1] == "[" {
        elements()
    } else {
        expect(nextToken10[2], "[")
    }
    var nextToken11 []string
    nextToken11 = getToken()
    if nextToken11[1] == "]" {
        
    } else {
        expect(nextToken11[2], "]")
    }
}

func elements() {
    // elements ::= value elements_tail | "¬"
    var nextToken []string
    nextToken = peek()
    if nextToken[0] == "STRING" {
        value()
        elementsTail()
    } else if nextToken[0] == "NUMBER" {
        value()
        elementsTail()
    } else if nextToken[0] == "TRUE" {
        value()
        elementsTail()
    } else if nextToken[0] == "FALSE" {
        value()
        elementsTail()
    } else if nextToken[0] == "NULL" {
        value()
        elementsTail()
    } else if nextToken[1] == "{" {
        value()
        elementsTail()
    } else if nextToken[1] == "[" {
        value()
        elementsTail()
    }
}

func elementsTail() {
    // elements_tail ::= "," elements | "¬"
    var nextToken []string
    nextToken = peek()
    if nextToken[1] == "," {
        var nextToken12 []string
        nextToken12 = getToken()
        if nextToken12[1] == "," {
            elements()
        } else {
            expect(nextToken12[2], ",")
        }
    }
}

func parse(file string) {
    generateTokens(file)
    loadTokens()
    json()
}

func main() {
    if len(os.Args) < 2 {
        fmt.Println("usage: parser FILE")
        os.Exit(1)
    }
    var filename string
    filename = os.Args[1]
    parse(filename)
    var nextToken []string
    nextToken = getToken()
    if nextToken[0] != "EOF" {
        expect(nextToken[2], "EOF")
    }
}

