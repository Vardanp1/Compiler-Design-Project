// parser.cpp - Syntax Analysis, Semantic Analysis and Intermediate Code
//
// Grammar (each rule is one function below):
//   program     -> statement*
//   statement   -> declaration | assignment | printStmt
//   declaration -> "int" IDENTIFIER "=" expression ";"
//   assignment  -> IDENTIFIER "=" expression ";"
//   printStmt   -> "print" expression ";"
//   expression  -> term (("+" | "-") term)*
//   term        -> factor (("*" | "/") factor)*
//   factor      -> NUMBER | IDENTIFIER | "(" expression ")"
//
// Operator precedence comes from the grammar itself: '*' and '/' are handled
// in term(), one level deeper than '+' and '-', so they are grouped first.
#include "parser.h"

#include <algorithm>
#include <cctype>
#include <climits>

static const char* SYNTAX   = "Syntax Analysis";
static const char* SEMANTIC = "Semantic Analysis";

[[noreturn]] static void fail(int line, const std::string& phase, const std::string& message,
                 const std::string& suggestion) {
    throw CompileError{line, phase, message, suggestion};
}

// How a token is shown inside an error message.
static std::string describe(const Token& t) {
    if (t.type == TokenType::END_OF_FILE) return "the end of the file";
    return "'" + t.text + "'";
}

static bool isOperator(TokenType t) {
    return t == TokenType::PLUS || t == TokenType::MINUS ||
           t == TokenType::STAR || t == TokenType::SLASH;
}

// Edit distance: how many single-letter changes turn a into b.
// Used to suggest "Did you mean ...?" for typos.
static size_t editDistance(const std::string& a, const std::string& b) {
    std::vector<size_t> row(b.size() + 1);
    for (size_t j = 0; j <= b.size(); j++) row[j] = j;
    for (size_t i = 1; i <= a.size(); i++) {
        size_t diag = row[0];
        row[0] = i;
        for (size_t j = 1; j <= b.size(); j++) {
            size_t old = row[j];
            row[j] = std::min({row[j] + 1, row[j - 1] + 1, diag + (a[i - 1] != b[j - 1])});
            diag = old;
        }
    }
    return row[b.size()];
}

// Names are "similar" if they differ by 1 letter (2 for longer names).
static bool looksLike(const std::string& word, const std::string& target) {
    size_t allowed = target.size() <= 3 ? 1 : 2;
    return word != target && editDistance(word, target) <= allowed;
}

Parser::Parser(const std::vector<Token>& toks) : tokens(toks) {
    for (const Token& t : tokens)
        if (t.type == TokenType::IDENTIFIER) userNames.insert(t.text);
}

const Token& Parser::advance() {
    const Token& t = tokens[pos];
    if (t.type != TokenType::END_OF_FILE) pos++;
    return t;
}

// Temporaries are named t1, t2, ... skipping any name the programmer already
// uses, so a temporary can never be confused with a real variable.
std::string Parser::newTemp() {
    std::string name;
    do { name = "t" + std::to_string(++tempCount); } while (userNames.count(name));
    return name;
}

std::string Parser::similarVariable(const std::string& name) const {
    for (const auto& entry : symbolTable)  // very short names give silly hints, so skip them
        if (entry.first.size() >= 3 && looksLike(name, entry.first)) return entry.first;
    return "";
}

// program -> statement*
void Parser::parseProgram() {
    if (check(TokenType::END_OF_FILE))
        fail(1, SYNTAX, "The program is empty. There is nothing to compile.",
             "Write at least one statement, for example 'int x = 5;'.");
    while (!check(TokenType::END_OF_FILE)) {
        statement();
        statements++;
    }
}

// statement -> declaration | assignment | printStmt
// We look at the first token to decide which rule applies.
void Parser::statement() {
    switch (peek().type) {
        case TokenType::KW_INT:   declaration();    return;
        case TokenType::KW_PRINT: printStatement(); return;
        case TokenType::IDENTIFIER:
            // tokens[pos + 1] exists: END_OF_FILE always follows an identifier.
            if (tokens[pos + 1].type == TokenType::ASSIGN) { assignment(); return; }
            unknownStatementError();
        default:
            unknownStatementError();
    }
}

// declaration -> "int" IDENTIFIER "=" expression ";"
void Parser::declaration() {
    advance();  // 'int'
    const Token& name = peek();

    if (name.type == TokenType::KW_INT || name.type == TokenType::KW_PRINT)
        fail(name.line, SYNTAX, "'" + name.text + "' is a reserved keyword and cannot be used as a variable name.",
             "Choose a different name, for example 'value'.");
    if (name.type != TokenType::IDENTIFIER)
        fail(previous().line, SYNTAX, "Expected a variable name after 'int', but found " + describe(name) + ".",
             "Write a name after 'int', for example 'int count = 0;'.");
    advance();

    // Semantic check: a name may only be declared once.
    auto existing = symbolTable.find(name.text);
    if (existing != symbolTable.end())
        fail(name.line, SEMANTIC, "Variable '" + name.text + "' has already been declared (on line " +
             std::to_string(existing->second.declaredLine) + ").",
             "Use a different variable name, or assign a new value with '" + name.text + " = ...;'.");

    if (check(TokenType::SEMICOLON))
        fail(name.line, SYNTAX, "Variable '" + name.text + "' is declared without a starting value.",
             "Give it a value, for example 'int " + name.text + " = 0;'.");
    if (!check(TokenType::ASSIGN))
        fail(name.line, SYNTAX, "Expected '=' after 'int " + name.text + "', but found " + describe(peek()) + ".",
             "Write it as 'int " + name.text + " = <value>;'.");
    advance();  // '='

    declaring = name.text;
    Operand value = expression();
    declaring.clear();
    expectSemicolon();

    // Only now is the variable added to the symbol table, so it cannot be
    // used inside its own initial value.
    symbolTable[name.text] = {name.line, value.value};
    tac.push_back(name.text + " = " + value.place);
}

// assignment -> IDENTIFIER "=" expression ";"
void Parser::assignment() {
    const Token& name = advance();

    // Semantic check: you can only assign to a declared variable.
    if (!symbolTable.count(name.text)) {
        std::string similar = similarVariable(name.text);
        if (!similar.empty())
            fail(name.line, SEMANTIC, "Variable '" + name.text + "' has not been declared.",
                 "Did you mean '" + similar + "'? If '" + name.text + "' is a new variable, write 'int " +
                 name.text + " = ...;'.");
        fail(name.line, SEMANTIC, "Variable '" + name.text + "' has not been declared.",
             "Declare it by adding 'int' in front: 'int " + name.text + " = ...;'.");
    }

    advance();  // '='
    Operand value = expression();
    expectSemicolon();

    symbolTable[name.text].value = value.value;
    tac.push_back(name.text + " = " + value.place);
}

// printStmt -> "print" expression ";"
void Parser::printStatement() {
    advance();  // 'print'
    if (check(TokenType::SEMICOLON))
        fail(peek().line, SYNTAX, "'print' needs something to print.",
             "Write a variable or expression after 'print', for example 'print x;'.");
    Operand value = expression();
    expectSemicolon();
    tac.push_back("print " + value.place);
}

// expression -> term (("+" | "-") term)*
// The loop makes the operators LEFT-associative: a - b - c = (a - b) - c.
Parser::Operand Parser::expression() {
    Operand left = term();
    while (check(TokenType::PLUS) || check(TokenType::MINUS)) {
        const Token& op = advance();
        Operand right = term();
        left = binary(left, op, right);
    }
    return left;
}

// term -> factor (("*" | "/") factor)*
Parser::Operand Parser::term() {
    Operand left = factor();
    while (check(TokenType::STAR) || check(TokenType::SLASH)) {
        const Token& op = advance();
        Operand right = factor();
        left = binary(left, op, right);
    }
    return left;
}

// factor -> NUMBER | IDENTIFIER | "(" expression ")"
Parser::Operand Parser::factor() {
    const Token& t = peek();

    if (t.type == TokenType::NUMBER) {
        advance();
        return {t.text, std::stoll(t.text)};  // the lexer already checked the range
    }

    if (t.type == TokenType::IDENTIFIER) {
        advance();
        auto it = symbolTable.find(t.text);
        if (it != symbolTable.end()) return {t.text, it->second.value};

        // Semantic check failed: the variable is not in the symbol table.
        if (t.text == declaring)
            fail(t.line, SEMANTIC, "Variable '" + t.text + "' is used in its own declaration, before it has a value.",
                 "Give it a starting value that does not use '" + t.text + "', for example 'int " + t.text + " = 0;'.");
        std::string similar = similarVariable(t.text);
        if (!similar.empty())
            fail(t.line, SEMANTIC, "Variable '" + t.text + "' has not been declared.",
                 "Did you mean '" + similar + "'? Otherwise declare it first using 'int " + t.text + " = 0;'.");
        fail(t.line, SEMANTIC, "Variable '" + t.text + "' has not been declared.",
             "Declare it using 'int " + t.text + " = 0;' before this line.");
    }

    if (t.type == TokenType::LPAREN) {
        const Token& open = advance();
        // Each '(' makes the parser call itself again; a limit keeps
        // absurdly deep nesting from overflowing the call stack.
        if (++depth > MAX_DEPTH)
            fail(open.line, SYNTAX, "Parentheses are nested too deeply (more than " + std::to_string(MAX_DEPTH) + " levels).",
                 "Split the expression into smaller statements using extra variables.");
        Operand inner = expression();
        if (!check(TokenType::RPAREN))
            fail(previous().line, SYNTAX, "Missing ')' to close the '(' opened on line " + std::to_string(open.line) + ".",
                 "Add ')' after " + describe(previous()) + ".");
        advance();  // ')'
        depth--;
        return inner;  // parentheses only group; they produce no code
    }

    factorError();
}

// Generates one TAC instruction "temp = left op right".
// The value is also computed so that division by zero and overflow can be
// caught at compile time (the language has no input or loops, so every value is
// known while compiling).
Parser::Operand Parser::binary(const Operand& left, const Token& op, const Operand& right) {
    long long result = 0;
    switch (op.type) {
        case TokenType::PLUS:  result = left.value + right.value; break;
        case TokenType::MINUS: result = left.value - right.value; break;
        case TokenType::STAR:  result = left.value * right.value; break;
        case TokenType::SLASH:
            if (right.value == 0) {
                std::string why;
                if (std::isdigit(static_cast<unsigned char>(right.place[0])))
                    why = "You are dividing by the number 0.";
                else if (symbolTable.count(right.place))
                    why = "Variable '" + right.place + "' is 0 at this point, so dividing by it is impossible.";
                else
                    why = "The expression on the right of '/' works out to 0.";
                fail(op.line, SEMANTIC, "Division by zero. " + why,
                     "Make sure the value on the right of '/' is not zero.");
            }
            result = left.value / right.value;
            break;
        default: break;
    }
    if (result > INT_MAX || result < INT_MIN)
        fail(op.line, SEMANTIC, "The result of '" + op.text + "' here is too large to fit in an int.",
             "Use smaller numbers. An int must be between " + std::to_string(INT_MIN) + " and " +
             std::to_string(INT_MAX) + ".");

    std::string temp = newTemp();
    tac.push_back(temp + " = " + left.place + " " + op.text + " " + right.place);
    return {temp, result};
}

// Called at the end of every statement. If the ';' is missing we try to
// work out WHY, to give the most helpful message.
void Parser::expectSemicolon() {
    if (check(TokenType::SEMICOLON)) { advance(); return; }
    const Token& t = peek();
    const Token& prev = previous();

    if (t.type == TokenType::RPAREN)
        fail(t.line, SYNTAX, "Found an extra ')' that has no matching '('.",
             "Remove the extra ')' or add a matching '(' earlier.");
    if (t.type == TokenType::ASSIGN)
        fail(t.line, SYNTAX, "Unexpected '='. A statement can contain only one '=' (and there is no '==').",
             "Split it into separate statements, one assignment each.");
    if ((t.type == TokenType::IDENTIFIER || t.type == TokenType::NUMBER || t.type == TokenType::LPAREN) &&
        t.line == prev.line)
        fail(t.line, SYNTAX, "Missing operator between " + describe(prev) + " and " + describe(t) + ".",
             "Put an operator such as '+' or '*' between them, or end the statement with ';'.");

    // Report the line where the ';' should have been, not the next line.
    fail(prev.line, SYNTAX, "Expected ';' at the end of the statement.",
         "Add a semicolon after " + describe(prev) + ".");
}

// Called when a value (number, variable or '(') was expected but not found.
void Parser::factorError() {
    const Token& t = peek();
    const Token& prev = previous();
    bool afterOperator = isOperator(prev.type);

    switch (t.type) {
        case TokenType::END_OF_FILE:
            fail(prev.line, SYNTAX, "The program ended in the middle of an expression.",
                 "Finish the expression and end the statement with ';'.");
        case TokenType::SEMICOLON:
            if (prev.type == TokenType::ASSIGN)
                fail(t.line, SYNTAX, "Missing value after '='.",
                     "Write a value after '=', for example 'x = 5;'.");
            if (afterOperator)
                fail(t.line, SYNTAX, "The operator '" + prev.text + "' has no value on its right side.",
                     "Add a number or variable after '" + prev.text + "', or remove the '" + prev.text + "'.");
            break;
        case TokenType::RPAREN:
            if (prev.type == TokenType::LPAREN)
                fail(t.line, SYNTAX, "Empty parentheses '()' are not allowed.",
                     "Put an expression inside them, for example '(a + 1)'.");
            if (afterOperator)
                fail(t.line, SYNTAX, "The operator '" + prev.text + "' has no value on its right side.",
                     "Add a number or variable between '" + prev.text + "' and ')'.");
            break;
        case TokenType::MINUS:
            if (!afterOperator)
                fail(t.line, SYNTAX, "Negative numbers such as '-5' are not supported directly.",
                     "Write it as a subtraction, for example '0 - 5'.");
            [[fallthrough]];
        case TokenType::PLUS:
        case TokenType::STAR:
        case TokenType::SLASH:
            if (afterOperator)
                fail(t.line, SYNTAX, "Two operators in a row: '" + prev.text + "' followed by '" + t.text + "'.",
                     "Remove one of them, or put a number or variable between them.");
            fail(t.line, SYNTAX, "An expression cannot start with the operator '" + t.text + "'.",
                 "Put a number or variable before '" + t.text + "'.");
        case TokenType::KW_INT:
        case TokenType::KW_PRINT:
            fail(prev.line, SYNTAX, "Expected a value after " + describe(prev) + ", but found the keyword '" +
                 t.text + "'.",
                 "Finish the expression and end the statement with ';'.");
        case TokenType::ASSIGN:
            fail(t.line, SYNTAX, "Unexpected '='. This language has no '==' and allows only one '=' per statement.",
                 "Remove the extra '='.");
        default: break;
    }
    fail(t.line, SYNTAX, "Expected a number, a variable or '(' but found " + describe(t) + ".",
         "Check the expression, for example 'a + (b * 2)'.");
}

// Called when a statement does not start with 'int', 'print' or 'name ='.
void Parser::unknownStatementError() {
    const Token& t = peek();

    if (t.type == TokenType::IDENTIFIER) {
        const Token& next = tokens[pos + 1];
        // A misspelled keyword, e.g. 'prnt x;' or 'Int a = 5;'
        for (const std::string kw : {"int", "print"}) {
            std::string lower = t.text;
            std::transform(lower.begin(), lower.end(), lower.begin(),
                           [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
            if (lower == kw || looksLike(t.text, kw))
                fail(t.line, SYNTAX, "Unknown word '" + t.text + "'.",
                     "Did you mean the keyword '" + kw + "'? Keywords are lowercase and followed by a space.");
        }
        if (next.type == TokenType::SEMICOLON)
            fail(t.line, SYNTAX, "'" + t.text + "' on its own is not a complete statement.",
                 "To display it write 'print " + t.text + ";'. To change it write '" + t.text + " = <value>;'.");
        fail(t.line, SYNTAX, "Expected '=' after '" + t.text + "', but found " + describe(next) + ".",
             "To assign a value, write '" + t.text + " = <expression>;'.");
    }
    if (t.type == TokenType::SEMICOLON)
        fail(t.line, SYNTAX, "Found an extra ';' with no statement before it.",
             "Remove the extra ';'.");
    if (t.type == TokenType::ASSIGN)
        fail(t.line, SYNTAX, "Missing variable name before '='.",
             "Write the variable name first, for example 'x = 5;'.");
    fail(t.line, SYNTAX, "A statement cannot start with " + describe(t) + ".",
         "Start the statement with 'int', 'print' or a variable name.");
}
