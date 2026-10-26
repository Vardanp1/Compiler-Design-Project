// lexer.h - Phase 1: Lexical Analysis
//
// The lexer (also called a scanner) reads the raw source text character by
// character and groups the characters into TOKENS - the "words" of the
// language, such as keywords, names, numbers and symbols.
#ifndef LEXER_H
#define LEXER_H

#include <string>
#include <vector>

// Every kind of token ErrorBuddy understands.
enum class TokenType {
    KW_INT,      // keyword 'int'
    KW_PRINT,    // keyword 'print'
    IDENTIFIER,  // variable name, e.g. score
    NUMBER,      // integer literal, e.g. 42
    PLUS, MINUS, STAR, SLASH,  // + - * /
    ASSIGN,      // =
    LPAREN,      // (
    RPAREN,      // )
    SEMICOLON,   // ;
    END_OF_FILE  // marks the end of the token list
};

struct Token {
    TokenType type;
    std::string text;  // exact characters from the source
    int line;          // line number where the token appears
};

// A friendly compiler error. Any phase can throw it; main.cpp catches it
// and prints it in the ErrorBuddy format.
struct CompileError {
    int line;
    std::string phase;       // which compiler phase found the problem
    std::string message;     // what is wrong, in plain English
    std::string suggestion;  // one concrete way to fix it
};

// Converts source text into a list of tokens (always ends with END_OF_FILE).
// Throws CompileError on characters or numbers that are not valid.
std::vector<Token> tokenize(const std::string& source);

// Human-readable name of a token type (used by the --tokens option).
std::string tokenTypeName(TokenType type);

#endif
