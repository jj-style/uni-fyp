CC = gcc
OPT = -O3 -std=c11 -DYYDEBUG
parser: lexer.c parser.c 
	$(CC) $(OPT) $^ -o $@

lexer.h lexer.c: lexer.l
	flex --header-file=lexer.h -o lexer.c lexer.l 

parser.h parser.c: parser.y
	bison -d -v -o parser.c parser.y

.PHONY: clean
clean:
	rm lexer.c lexer.h parser.c parser.h parser.output 2>/dev/null
