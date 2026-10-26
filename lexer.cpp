// lexer.cpp - Phase 1: Lexical Analysis
#include "lexer.h"

#include <cctype>
#include <climits>

std::string tokenTypeName(TokenType type) {
    switch (type) {
        case TokenType::KW_INT:      return "KEYWORD";
        case TokenType::KW_PRINT:    return "KEYWORD";
        case TokenType::IDENTIFIER:  return "IDENTIFIER";
        case TokenType::NUMBER:      return "NUMBER";
        case TokenType::PLUS:
        case TokenType::MINUS:
        case TokenType::STAR:
        case TokenType::SLASH:       return "OPERATOR";
        case TokenType::ASSIGN:      return "ASSIGN";
        case TokenType::LPAREN:      return "LPAREN";
        case TokenType::RPAREN:      return "RPAREN";
        case TokenType::SEMICOLON:   return "SEMICOLON";
        case TokenType::END_OF_FILE: return "EOF";
    }
    return "UNKNOWN";
}

// The cast to unsigned char avoids undefined behaviour for non-ASCII bytes.
static bool isLetter(char c) { return std::isalpha(static_cast<unsigned char>(c)) || c == '_'; }
static bool isDigit(char c)  { return std::isdigit(static_cast<unsigned char>(c)) != 0; }

std::vector<Token> tokenize(const std::string& src) {
    std::vector<Token> tokens;
    int line = 1;
    size_t i = 0;

    while (i < src.size()) {
        char c = src[i];

        // 1. Whitespace: skipped, but newlines advance the line counter.
        if (c == '\n') { line++; i++; continue; }
        if (std::isspace(static_cast<unsigned char>(c))) { i++; continue; }

        // 2. Comments: '//' until the end of the line are ignored.
        if (c == '/' && i + 1 < src.size() && src[i + 1] == '/') {
            while (i < src.size() && src[i] != '\n') i++;
            continue;
        }

        // 3. Integer literals: a run of digits.
        if (isDigit(c)) {
            size_t start = i;
            long long value = 0;
            bool tooBig = false;
            while (i < src.size() && isDigit(src[i])) {
                value = value * 10 + (src[i] - '0');
                if (value > INT_MAX) { tooBig = true; value = INT_MAX; }  // stop growing, avoid overflow
                i++;
            }
            // A digit immediately followed by a letter, e.g. "2nd", is a bad name.
            if (i < src.size() && isLetter(src[i])) {
                while (i < src.size() && (isLetter(src[i]) || isDigit(src[i]))) i++;
                throw CompileError{line, "Lexical Analysis",
                    "'" + src.substr(start, i - start) + "' is not a valid name. Variable names cannot start with a digit.",
                    "Start the name with a letter, for example 'value1' instead of '1value'."};
            }
            std::string text = src.substr(start, i - start);
            if (tooBig) {
                throw CompileError{line, "Lexical Analysis",
                    "The number " + text + " is too large. An int can be at most " + std::to_string(INT_MAX) + ".",
                    "Use a smaller number."};
            }
            tokens.push_back({TokenType::NUMBER, text, line});
            continue;
        }

        // 4. Identifiers and keywords: a letter or '_' followed by letters, digits or '_'.
        if (isLetter(c)) {
            size_t start = i;
            while (i < src.size() && (isLetter(src[i]) || isDigit(src[i]))) i++;
            std::string word = src.substr(start, i - start);
            TokenType type = TokenType::IDENTIFIER;
            if (word == "int")   type = TokenType::KW_INT;
            if (word == "print") type = TokenType::KW_PRINT;
            tokens.push_back({type, word, line});
            continue;
        }

        // 5. Single-character symbols.
        TokenType type;
        switch (c) {
            case '+': type = TokenType::PLUS;      break;
            case '-': type = TokenType::MINUS;     break;
            case '*': type = TokenType::STAR;      break;
            case '/': type = TokenType::SLASH;     break;
            case '=': type = TokenType::ASSIGN;    break;
            case '(': type = TokenType::LPAREN;    break;
            case ')': type = TokenType::RPAREN;    break;
            case ';': type = TokenType::SEMICOLON; break;
            default: {
                // Anything else is a character the language does not know.
                std::string shown = std::isprint(static_cast<unsigned char>(c))
                    ? "'" + std::string(1, c) + "'"
                    : "a non-printable or non-English character";
                throw CompileError{line, "Lexical Analysis",
                    "Unknown symbol " + shown + ". ErrorBuddy only understands letters, digits and + - * / = ( ) ;",
                    "Remove the symbol or replace it with one of the supported symbols."};
            }
        }
        tokens.push_back({type, std::string(1, c), line});
        i++;
    }

    tokens.push_back({TokenType::END_OF_FILE, "", line});
    return tokens;
}
