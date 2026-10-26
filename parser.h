// parser.h - Phases 2, 3 and 4: Syntax Analysis, Semantic Analysis and
// Intermediate Code Generation.
//
// The parser walks through the tokens using RECURSIVE DESCENT: one C++
// function per grammar rule. While it recognises each statement it also
//   - checks the meaning of the statement (semantic analysis), and
//   - emits three-address code for it (intermediate code generation).
// Doing all three in one pass is called SYNTAX-DIRECTED TRANSLATION.
#ifndef PARSER_H
#define PARSER_H

#include "lexer.h"

#include <map>
#include <set>
#include <string>
#include <vector>

// One entry in the symbol table.
struct Symbol {
    int declaredLine;  // where the variable was declared
    long long value;   // its value at this point (used to spot division by zero)
};

class Parser {
public:
    explicit Parser(const std::vector<Token>& tokens);

    // Parses the whole program. Throws CompileError on the first problem.
    void parseProgram();

    const std::vector<std::string>& code() const { return tac; }
    const std::map<std::string, Symbol>& symbols() const { return symbolTable; }
    int statementCount() const { return statements; }

private:
    // The result of an expression: where its value lives in the TAC
    // ("5", "x" or a temporary like "t1") and the value it has.
    struct Operand {
        std::string place;
        long long value;
    };

    // Grammar rules - one function each.
    void statement();
    void declaration();
    void assignment();
    void printStatement();
    Operand expression();
    Operand term();
    Operand factor();

    // Helpers.
    const Token& peek() const { return tokens[pos]; }
    const Token& previous() const { return tokens[pos > 0 ? pos - 1 : 0]; }
    bool check(TokenType type) const { return peek().type == type; }
    const Token& advance();
    void expectSemicolon();
    Operand binary(const Operand& left, const Token& op, const Operand& right);
    std::string newTemp();
    [[noreturn]] void factorError();
    [[noreturn]] void unknownStatementError();
    std::string similarVariable(const std::string& name) const;

    std::vector<Token> tokens;
    size_t pos = 0;
    int statements = 0;

    std::map<std::string, Symbol> symbolTable;  // name -> info
    std::set<std::string> userNames;            // every identifier in the source
    std::string declaring;                      // variable currently being declared

    std::vector<std::string> tac;               // generated three-address code
    int tempCount = 0;

    int depth = 0;                              // current '(' nesting level
    static const int MAX_DEPTH = 200;
};

#endif
