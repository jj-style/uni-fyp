%{
#include <stdio.h>    
int yylex(void);
int yyerror(const char* s);
#include "lexer.h"
%}

%define parse.error verbose

%token STRING NUMBER TRUE FALSE NULL__T ANY COMMA COLON L_BRACE R_BRACE L_BRACKET R_BRACKET
%start json

%%

json          : object | array {};
object        : L_BRACE pairs R_BRACE {};
pairs         : pair pairs_tail | %empty {};
pair          : STRING COLON value {};
pairs_tail    : COMMA pairs | %empty {};

value         : STRING | NUMBER | TRUE | FALSE | NULL__T | object | array {};
array         : L_BRACKET elements R_BRACKET {};

elements      : value elements_tail | %empty {};
elements_tail : COMMA elements | %empty {};

%%

int main(int argc, char **argv) {
    if (argc > 1) {
      yyin = fopen(argv[1], "r");
      if (yyin == NULL){
         printf("syntax: %s filename\n", argv[0]);
      }
   }
   /*yydebug = 1;*/
   yyparse();
   return 0;
}

int yyerror(const char *s) {
    printf("error: %s\n", s);
}
