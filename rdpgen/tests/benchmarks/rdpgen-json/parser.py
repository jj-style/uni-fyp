import subprocess
import sys
from typing import List
from typing import get_type_hints


def read_lines(file: str) -> List[str]:
	f = open(file, "r")
	text = f.read()
	f.close()
	return text.splitlines()

tokens: List[List[str]]

def generate_tokens(file: str):
	command: str
	command = "cd lexer && make --silent && ./lexer "
	command = command + file
	response = subprocess.run(command, shell=True)
	if response.returncode != 0:
		exit(1)

def load_tokens():
	global tokens
	tokens = []
	token_lines: List[str]
	token_lines = read_lines("lexer/out.jl")
	idx: int
	for idx in range(len(token_lines)):
		tokens.append(token_lines[idx].split(""))

def peek() -> List[str]:
	if len(tokens) > 0:
		return tokens[0]
	return []

def get_token() -> List[str]:
	if len(tokens) > 0:
		next: List[str]
		next = tokens[0]
		tokens.pop(0)
		return next
	return []

def expect(line_num: str, e: str):
	print("Error: line ", line_num, "- expected ", e)
	exit(1)

def json():
	# json ::= object | array
	next_token: List[str]
	next_token = peek()
	if next_token[1] == "{":
		object()
	elif next_token[1] == "[":
		array()
	else:
		expect(next_token[2], "{,[")

def object():
	# object ::= "{" pairs "}"
	next_token: List[str]
	next_token = get_token()
	if next_token[1] == "{":
		pairs()
	else:
		expect(next_token[2], "{")
	next_token: List[str]
	next_token = get_token()
	if next_token[1] == "}":
		pass
	else:
		expect(next_token[2], "}")

def pairs():
	# pairs ::= pair pairs_tail | "¬"
	next_token: List[str]
	next_token = peek()
	if next_token[0] == "STRING":
		pair()
		pairs_tail()

def pair():
	# pair ::= <STRING> ":" value
	next_token: List[str]
	next_token = get_token()
	if next_token[0] == "STRING":
		pass
	else:
		expect(next_token[2], "STRING")
	next_token: List[str]
	next_token = get_token()
	if next_token[1] == ":":
		value()
	else:
		expect(next_token[2], ":")

def pairs_tail():
	# pairs_tail ::= "," pairs | "¬"
	next_token: List[str]
	next_token = peek()
	if next_token[1] == ",":
		next_token: List[str]
		next_token = get_token()
		if next_token[1] == ",":
			pairs()
		else:
			expect(next_token[2], ",")

def value():
	# value ::= <STRING> | <NUMBER> | <TRUE> | <FALSE> | <NULL> | object | array
	next_token: List[str]
	next_token = peek()
	if next_token[0] == "STRING":
		next_token: List[str]
		next_token = get_token()
		if next_token[0] == "STRING":
			pass
		else:
			expect(next_token[2], "STRING")
	elif next_token[0] == "NUMBER":
		next_token: List[str]
		next_token = get_token()
		if next_token[0] == "NUMBER":
			pass
		else:
			expect(next_token[2], "NUMBER")
	elif next_token[0] == "TRUE":
		next_token: List[str]
		next_token = get_token()
		if next_token[0] == "TRUE":
			pass
		else:
			expect(next_token[2], "TRUE")
	elif next_token[0] == "FALSE":
		next_token: List[str]
		next_token = get_token()
		if next_token[0] == "FALSE":
			pass
		else:
			expect(next_token[2], "FALSE")
	elif next_token[0] == "NULL":
		next_token: List[str]
		next_token = get_token()
		if next_token[0] == "NULL":
			pass
		else:
			expect(next_token[2], "NULL")
	elif next_token[1] == "{":
		object()
	elif next_token[1] == "[":
		array()
	else:
		expect(next_token[2], "STRING,NUMBER,TRUE,FALSE,NULL,{,[")

def array():
	# array ::= "[" elements "]"
	next_token: List[str]
	next_token = get_token()
	if next_token[1] == "[":
		elements()
	else:
		expect(next_token[2], "[")
	next_token: List[str]
	next_token = get_token()
	if next_token[1] == "]":
		pass
	else:
		expect(next_token[2], "]")

def elements():
	# elements ::= value elements_tail | "¬"
	next_token: List[str]
	next_token = peek()
	if next_token[0] == "STRING":
		value()
		elements_tail()
	elif next_token[0] == "NUMBER":
		value()
		elements_tail()
	elif next_token[0] == "TRUE":
		value()
		elements_tail()
	elif next_token[0] == "FALSE":
		value()
		elements_tail()
	elif next_token[0] == "NULL":
		value()
		elements_tail()
	elif next_token[1] == "{":
		value()
		elements_tail()
	elif next_token[1] == "[":
		value()
		elements_tail()

def elements_tail():
	# elements_tail ::= "," elements | "¬"
	next_token: List[str]
	next_token = peek()
	if next_token[1] == ",":
		next_token: List[str]
		next_token = get_token()
		if next_token[1] == ",":
			elements()
		else:
			expect(next_token[2], ",")

def parse(file: str):
	generate_tokens(file)
	load_tokens()
	json()

def main():
	if len(sys.argv) < 2:
		print("usage: parser FILE")
		exit(1)
	filename: str
	filename = sys.argv[1]
	parse(filename)
	next_token: List[str]
	next_token = get_token()
	if next_token[0] != "EOF":
		expect(next_token[2], "EOF")

if __name__ == "__main__":
	main()