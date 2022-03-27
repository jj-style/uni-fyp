%{
#include <stdio.h>
#include "parser.h"
%}

%option noyywrap
%option never-interactive

STRING \"([^\\\"]|\\.)*\"
NUMBER -?[0-9]+(\.[0-9]+)?
TRUE true
FALSE false
NULL null

newline \n
whitespace  [ \t\r]+

%%
{whitespace} {};
{newline}    {};
{STRING} {return STRING;}
{NUMBER} {return NUMBER;}
{TRUE} {return TRUE;}
{FALSE} {return FALSE;}
{NULL} {return NULL__T;}
":" {return COLON;}
"," {return COMMA;}
"{" {return L_BRACE;}
"}" {return R_BRACE;}
"[" {return L_BRACKET;}
"]" {return R_BRACKET;}
.	{printf("unknown item: '%s'\n", yytext); exit(1);}
%%

/*int main(int argc, char**argv) {*/
  /*if (argc > 1) {*/
    /*// set lex to read from file instead of stdin*/
    /*FILE *fin = fopen(argv[1], "r");*/
    /*if (!fin) {*/
      /*perror(argv[1]);*/
      /*return 1;*/
    /*}*/
    /*yyin = fin;*/
  /*}*/
  /*yylex();*/
  /*return 0;*/
/*}*/
