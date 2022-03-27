#include <fstream>
#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <string>
#include <vector>

std::vector<std::string> get_token();
std::vector<std::string> peek();
std::vector<std::string> read_lines(std::string file);
std::vector<std::string> split_string(std::string s, char delim);
void array();
void elements();
void elements_tail();
void expect(std::string line_num, std::string e);
void generate_tokens(std::string file);
void json();
void load_tokens();
void object();
void pair();
void pairs();
void pairs_tail();
void parse(std::string file);
void value();

std::vector<std::string> read_lines(std::string file) {
  std::fstream f;
  std::vector<std::string> lines;
  f.open(file, std::ios::in);
  if (f.is_open()) {
    std::string line;
    while (getline(f, line)) {
      lines.push_back(line);
    }
    f.close();
  } else {
    exit(1);
  }
  return lines;
}

std::vector<std::string> split_string(std::string s, char delim) {
  std::string tmp;
  std::stringstream ss(s);
  std::vector<std::string> words;
  while (std::getline(ss, tmp, delim)) {
    words.push_back(tmp);
  }
  return words;
}

std::vector<std::vector<std::string>> tokens;

void generate_tokens(std::string file) {
  std::string command;
  command = "cd lexer && make --silent && ./lexer ";
  command = command + file;
  std::string cmd;
  cmd = command;
  int rc;
  rc = system(cmd.c_str());
  if (rc != 0) {
    exit(1);
  }
}

void load_tokens() {
  tokens = {};
  std::vector<std::string> token_lines;
  token_lines = read_lines("lexer/out.jl");
  int idx;
  for (idx = 0; idx < token_lines.size(); idx = idx + 1) {
    tokens.push_back(split_string(token_lines[idx], ''));
  }
}

std::vector<std::string> peek() {
  if (tokens.size() > 0) {
    return tokens[0];
  }
  return {};
}

std::vector<std::string> get_token() {
  if (tokens.size() > 0) {
    std::vector<std::string> next;
    next = tokens[0];
    tokens.erase(tokens.begin() + 0);
    return next;
  }
  return {};
}

void expect(std::string line_num, std::string e) {
  std::cout << "Error: line " << line_num << "- expected " << e << std::endl;
  exit(1);
}

void json() {
  // json ::= object | array
  std::vector<std::string> next_token;
  next_token = peek();
  if (next_token[1] == "{") {
    object();
  } else if (next_token[1] == "[") {
    array();
  } else {
    expect(next_token[2], "{,[");
  }
}

void object() {
  // object ::= "{" pairs "}"
  std::vector<std::string> next_token;
  next_token = get_token();
  if (next_token[1] == "{") {
    pairs();
  } else {
    expect(next_token[2], "{");
  }
  std::vector<std::string> next_token1;
  next_token1 = get_token();
  if (next_token1[1] == "}") {
    
  } else {
    expect(next_token1[2], "}");
  }
}

void pairs() {
  // pairs ::= pair pairs_tail | "¬"
  std::vector<std::string> next_token;
  next_token = peek();
  if (next_token[0] == "STRING") {
    pair();
    pairs_tail();
  }
}

void pair() {
  // pair ::= <STRING> ":" value
  std::vector<std::string> next_token2;
  next_token2 = get_token();
  if (next_token2[0] == "STRING") {
    
  } else {
    expect(next_token2[2], "STRING");
  }
  std::vector<std::string> next_token3;
  next_token3 = get_token();
  if (next_token3[1] == ":") {
    value();
  } else {
    expect(next_token3[2], ":");
  }
}

void pairs_tail() {
  // pairs_tail ::= "," pairs | "¬"
  std::vector<std::string> next_token;
  next_token = peek();
  if (next_token[1] == ",") {
    std::vector<std::string> next_token4;
    next_token4 = get_token();
    if (next_token4[1] == ",") {
      pairs();
    } else {
      expect(next_token4[2], ",");
    }
  }
}

void value() {
  // value ::= <STRING> | <NUMBER> | <TRUE> | <FALSE> | <NULL> | object | array
  std::vector<std::string> next_token;
  next_token = peek();
  if (next_token[0] == "STRING") {
    std::vector<std::string> next_token5;
    next_token5 = get_token();
    if (next_token5[0] == "STRING") {
      
    } else {
      expect(next_token5[2], "STRING");
    }
  } else if (next_token[0] == "NUMBER") {
    std::vector<std::string> next_token6;
    next_token6 = get_token();
    if (next_token6[0] == "NUMBER") {
      
    } else {
      expect(next_token6[2], "NUMBER");
    }
  } else if (next_token[0] == "TRUE") {
    std::vector<std::string> next_token7;
    next_token7 = get_token();
    if (next_token7[0] == "TRUE") {
      
    } else {
      expect(next_token7[2], "TRUE");
    }
  } else if (next_token[0] == "FALSE") {
    std::vector<std::string> next_token8;
    next_token8 = get_token();
    if (next_token8[0] == "FALSE") {
      
    } else {
      expect(next_token8[2], "FALSE");
    }
  } else if (next_token[0] == "NULL") {
    std::vector<std::string> next_token9;
    next_token9 = get_token();
    if (next_token9[0] == "NULL") {
      
    } else {
      expect(next_token9[2], "NULL");
    }
  } else if (next_token[1] == "{") {
    object();
  } else if (next_token[1] == "[") {
    array();
  } else {
    expect(next_token[2], "STRING,NUMBER,TRUE,FALSE,NULL,{,[");
  }
}

void array() {
  // array ::= "[" elements "]"
  std::vector<std::string> next_token10;
  next_token10 = get_token();
  if (next_token10[1] == "[") {
    elements();
  } else {
    expect(next_token10[2], "[");
  }
  std::vector<std::string> next_token11;
  next_token11 = get_token();
  if (next_token11[1] == "]") {
    
  } else {
    expect(next_token11[2], "]");
  }
}

void elements() {
  // elements ::= value elements_tail | "¬"
  std::vector<std::string> next_token;
  next_token = peek();
  if (next_token[0] == "STRING") {
    value();
    elements_tail();
  } else if (next_token[0] == "NUMBER") {
    value();
    elements_tail();
  } else if (next_token[0] == "TRUE") {
    value();
    elements_tail();
  } else if (next_token[0] == "FALSE") {
    value();
    elements_tail();
  } else if (next_token[0] == "NULL") {
    value();
    elements_tail();
  } else if (next_token[1] == "{") {
    value();
    elements_tail();
  } else if (next_token[1] == "[") {
    value();
    elements_tail();
  }
}

void elements_tail() {
  // elements_tail ::= "," elements | "¬"
  std::vector<std::string> next_token;
  next_token = peek();
  if (next_token[1] == ",") {
    std::vector<std::string> next_token12;
    next_token12 = get_token();
    if (next_token12[1] == ",") {
      elements();
    } else {
      expect(next_token12[2], ",");
    }
  }
}

void parse(std::string file) {
  generate_tokens(file);
  load_tokens();
  json();
}

int main(int argc, char* argv[]) {
  if (argc < 2) {
    std::cout << "usage: parser FILE" << std::endl;
    exit(1);
  }
  std::string filename;
  filename = argv[1];
  parse(filename);
  std::vector<std::string> next_token;
  next_token = get_token();
  if (next_token[0] != "EOF") {
    expect(next_token[2], "EOF");
  }
  return 0;
}

