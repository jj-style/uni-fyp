Feature: Generate Parser for G1
    Background: Generate Parser in Languages
    Given I have a grammar G1
    When I generate a parser in <language>
    Then I see a file parser.<extension>
    
    Examples:
    | language | extension | command          |
    | python   | py        | python           |
    | go       | go        | go run           |
    | c++      | cpp       | g++ _ && ./a.out |
    
    Scenario Outline: Parser Accepts Valid Input
    When I run the parser with "<command>" and input:
        x = 10
        number = 3
        _varz = 123
    Then I get a 0 return code

    Scenario Outline: Parser Rejects Invalid Input
    When I run the parser with "<command>" and input:
        x = 10
        number = 3
        2x = 5
    Then I get a 1 return code

    