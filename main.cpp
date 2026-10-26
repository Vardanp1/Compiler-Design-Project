// main.cpp - ErrorBuddy driver
//
// Reads a source file, runs the compiler phases in order and prints either
// the generated three-address code or a friendly error explanation.
//
// Usage: ./errorbuddy <file> [--tokens]
#include "lexer.h"
#include "parser.h"

#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

static void printTokens(const std::vector<Token>& tokens) {
    std::cout << "Tokens (output of the lexer):\n";
    std::cout << "  " << std::left << std::setw(6) << "Line" << std::setw(12) << "Type" << "Text\n";
    for (const Token& t : tokens) {
        if (t.type == TokenType::END_OF_FILE) break;
        std::cout << "  " << std::setw(6) << t.line << std::setw(12) << tokenTypeName(t.type) << t.text << "\n";
    }
    std::cout << "\n";
}

int main(int argc, char* argv[]) {
    std::string path;
    bool showTokens = false;
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--tokens") showTokens = true;
        else path = arg;
    }
    if (path.empty()) {
        std::cout << "Usage: " << argv[0] << " <source-file> [--tokens]\n";
        return 2;
    }

    std::ifstream file(path, std::ios::binary);
    if (!file) {
        std::cout << "ErrorBuddy could not open the file '" << path << "'.\n"
                  << "Suggestion: Check the file name and path.\n";
        return 2;
    }
    std::stringstream buffer;
    buffer << file.rdbuf();

    std::cout << "ErrorBuddy - compiling " << path << "\n\n";

    try {
        // Phase 1: Lexical analysis
        std::vector<Token> tokens = tokenize(buffer.str());
        if (showTokens) printTokens(tokens);

        // Phases 2-4: Syntax analysis, semantic analysis, code generation
        Parser parser(tokens);
        parser.parseProgram();

        // Reaching this point means every phase succeeded.
        std::cout << "Compilation successful!\n\n";

        std::cout << "Intermediate Code (Three-Address Code):\n";
        for (const std::string& line : parser.code()) std::cout << "    " << line << "\n";

        std::cout << "\nSymbol Table:\n";
        for (const auto& entry : parser.symbols())
            std::cout << "    " << std::left << std::setw(12) << entry.first
                      << "int   (declared on line " << entry.second.declaredLine << ")\n";

        std::cout << "\nPhases completed:\n"
                  << "    [OK] 1. Lexical Analysis    - " << tokens.size() - 1 << " tokens\n"
                  << "    [OK] 2. Syntax Analysis     - " << parser.statementCount() << " statements\n"
                  << "    [OK] 3. Semantic Analysis   - " << parser.symbols().size() << " variables, no errors\n"
                  << "    [OK] 4. Intermediate Code   - " << parser.code().size() << " instructions\n";
        return 0;
    } catch (const CompileError& e) {
        // Phase 5: ErrorBuddy's friendly error explanation.
        std::cout << "Error on line " << e.line << ":\n"
                  << e.message << "\n"
                  << "Suggestion: " << e.suggestion << "\n\n"
                  << "(Found during: " << e.phase << ")\n"
                  << "Compilation stopped. No intermediate code was generated.\n";
        return 1;
    } catch (const std::exception& e) {
        // Should never happen; reported clearly instead of crashing.
        std::cout << "Internal compiler error: " << e.what() << "\n";
        return 3;
    }
}
