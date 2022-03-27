Feature: Generate Parser for JSON
    Background: Generate Parser in Languages
    Given I have a grammar json
    When I generate a parser in <language>
    Then I see a file parser.<extension>
    
    Examples:
    | language | extension | command          |
    | python   | py        | python           |
    | go       | go        | go run           |
    | c++      | cpp       | g++ _ && ./a.out |
    
    Scenario Outline: Parser Accepts Valid Input
    When I run the parser with "<command>" and input:
        <input>
    Then I get a 0 return code
    Examples:
    | input                                                                     |
    | {}                                                                        |
    | {"hello": "world"}                                                        |
    | {"age": 10}                                                               |
    | {"bool": true}                                                            |
    | {"data": [1,2,true,null]}                                                 |
    | {"id1": {"name": "jj", "age": 21, "interests": ["coding", "movies"]} }    |
    | [{"data":"in"}, {"arrays":"!"}]                                           |

    Scenario Outline: Parser Rejects Invalid Input
    When I run the parser with "<command>" and input:
        <input>
    Then I get a 1 return code
    Examples:
    | input                                      |
    | {                                          |
    | {hello: world}                             |
    | {"invalid : 10}                            |
    | {"name": }                                 |
    | {"bad-value": invalid }                    |
    | [{"forgot": "to close the array... oops!"} |    