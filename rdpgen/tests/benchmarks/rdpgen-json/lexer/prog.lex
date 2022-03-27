%{
#include <stdio.h>
int lno = 1;
FILE *fp;
%}

STRING \"([^\\\"]|\\.)*\"
NUMBER -?[0-9]+(\.[0-9]+)?
TRUE true
FALSE false
NULL null
ANY [a-zA-Z\[\]\{\}:,]

newline \n
whitespace  [ \t\r]+

%%
{whitespace} continue;
{newline} ++lno;
{STRING} fprintf(fp,"STRING\a%s\a%d\n",yytext,lno);
{NUMBER} fprintf(fp,"NUMBER\a%s\a%d\n",yytext,lno);
{TRUE} fprintf(fp,"TRUE\a%s\a%d\n",yytext,lno);
{FALSE} fprintf(fp,"FALSE\a%s\a%d\n",yytext,lno);
{NULL} fprintf(fp,"NULL\a%s\a%d\n",yytext,lno);
{ANY} fprintf(fp,"ANY\a%s\a%d\n",yytext,lno);
.	{printf("unknown item on line %d: '%s'\n", lno, yytext); exit(1);}
%%

int main(int argc, char**argv) {
  if (argc > 1) {
    // set lex to read from file instead of stdin
    FILE *fin = fopen(argv[1], "r");
    if (!fin) {
      perror(argv[1]);
      return 1;
    }
    yyin = fin;
  }
  fp = fopen("out.jl","w");
  yylex();
  // write sentinel EOF to token stream
  fprintf(fp,"EOF\a0\a%d\n",lno);
  fclose(fp);
  return 0;
}