all: lexer

lexer: lex.yy.c
	gcc -lfl -o lexer lex.yy.c

lex.yy.c: prog.lex
	flex prog.lex

.PHONY: clean
clean:
	rm lex.yy.c