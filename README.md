# ErrorBuddy: a beginner-friendly compiler

**Live site:** https://vardanp1.github.io/Compiler-Design-Project/ ·
**Playground:** https://vardanp1.github.io/Compiler-Design-Project/playground.html ·
**Final report:** [ErrorBuddy_Final_Report.pdf](ErrorBuddy_Final_Report.pdf) ·
**Presentation:** [ErrorBuddy_Complete.pdf](ErrorBuddy_Complete.pdf) / [.pptx](ErrorBuddy_Complete.pptx)

ErrorBuddy compiles a small beginner language into **three-address code (TAC)**.
Its main feature is that it explains errors in plain English, gives the line
number, and suggests one fix.

## Objective

Show the main phases of a compiler in a small C++17 program that can be read
in one sitting:

1. Lexical analysis
2. Syntax analysis
3. Semantic analysis
4. Intermediate code generation
5. Error detection and explanation

## The language

```text
int age = 20;              // declaration (must have a starting value)
int score = 10;
score = score + age * 2;   // assignment
print (score - 5) / 3;     // print any expression
```

- Every variable is an `int`. You declare it with `int` and must give it a value.
- Arithmetic uses `+ - * /`, follows normal precedence, and allows parentheses.
- Every statement ends with `;`.
- `//` starts a comment that runs to the end of the line.

### Grammar

```text
program     -> statement*
statement   -> declaration | assignment | printStmt
declaration -> "int" IDENTIFIER "=" expression ";"
assignment  -> IDENTIFIER "=" expression ";"
printStmt   -> "print" expression ";"
expression  -> term (("+" | "-") term)*
term        -> factor (("*" | "/") factor)*
factor      -> NUMBER | IDENTIFIER | "(" expression ")"
```

### Limitations (on purpose)

- No negative literals (write `0 - 5`), no unary minus.
- No functions, loops, if/else, arrays, strings, or other types.
- Compilation stops at the **first** error.
- Division is integer division, so `7 / 2` is `3`.

## Files

| File | Role |
|------|------|
| `lexer.h` / `lexer.cpp` | **Phase 1.** Turns source text into tokens (type, text, line). Also defines `CompileError`, the friendly error that every phase uses. |
| `parser.h` / `parser.cpp` | **Phases 2–4.** A recursive-descent parser with one function per grammar rule. While it parses, it also checks meaning against the symbol table and emits TAC. |
| `main.cpp` | Reads the file, runs the phases, then prints either the TAC or the error explanation. |
| `examples/` | Test programs. `examples/expected/` holds the output each one should produce. |
| `Makefile` | Build, run, test and clean commands. |

## How each phase works

**1. Lexical analysis (`tokenize`).** The lexer scans the text one character at a time.
It skips spaces and comments and counts newlines so it always knows the line number.
It groups characters into tokens such as `KEYWORD int`, `IDENTIFIER age`, `NUMBER 20`
and `OPERATOR +`. It catches unknown symbols like `@`, numbers too big for an `int`,
and names that start with a digit like `2nd`.
Run `./errorbuddy file --tokens` to see the token list.

**2. Syntax analysis (recursive descent).** Each grammar rule is a C++ function:
`statement()`, `declaration()`, `expression()`, `term()`, `factor()`. A function
calls the functions for the pieces inside its rule. Precedence comes from the
grammar itself. `expression()` handles `+ -` and calls `term()`, and `term()`
handles `* /`. So in `a + b * 2`, the `b * 2` part is finished inside `term()`
before the `+` is applied. The `while` loops make operators left-associative:
`10 - 4 - 3` is `(10 - 4) - 3`.

**3. Semantic analysis (symbol table).** A `std::map<std::string, Symbol>` records
each declared variable, the line it was declared on, and its current value.
The parser uses it to catch these errors:
- a variable used or assigned before it is declared, including inside its own declaration
- a variable declared twice
- division by zero, including cases like `a / zero` or `8 / (4 - 4)`
- results that do not fit in an `int`

This language has no input and no loops, so every value is known while compiling.
That is why the compiler can find these errors even when the divisor is a variable.

**4. Intermediate code generation (TAC).** Each operator becomes one instruction of
the form `temp = left op right`. The temporaries are named `t1`, `t2`, and so on,
and skip any name the program already uses. The code for a statement is emitted
as soon as that statement is parsed, so the TAC is always in source order.
Parentheses only change the grouping and produce no instructions.

The parser does phases 2, 3 and 4 in one pass. This approach is called
**syntax-directed translation**. The TAC is only printed after the whole program
has passed, so a program with an error never shows any code.

**5. ErrorBuddy error explanations.** Every error is a `CompileError` with four
parts: the line, the phase, a plain-English message and one suggestion. The
parser looks at nearby tokens to work out the *likely cause* of an error,
instead of printing a generic "syntax error". For example:

| Situation | ErrorBuddy says |
|-----------|-----------------|
| `int b = 10` with no `;` | Expected ';' at the end of the statement. (It reports the line of the `10`, not the next line.) |
| `x + * 3` | Two operators in a row: '+' followed by '*'. |
| `(x + 3` | Missing ')' to close the '(' opened on line 2. |
| `5)` | Found an extra ')' that has no matching '('. |
| `int a = -5;` | Negative numbers such as '-5' are not supported directly. Write `0 - 5`. |
| `scroe = 2;` | Variable 'scroe' has not been declared. Did you mean 'score'? |
| `prnt x;` | Unknown word 'prnt'. Did you mean the keyword 'print'? |
| `int a = a + 1;` | Variable 'a' is used in its own declaration. |
| `int a;` | Variable 'a' is declared without a starting value. |

The "Did you mean" hints use *edit distance*, which counts the single-letter
changes needed to turn one word into another.

## Build and run

You need `g++` with C++17 support and `make`.

```bash
make                                   # build ./errorbuddy
make run                               # compile examples/valid.txt
make run FILE=examples/missing_semicolon.txt
./errorbuddy examples/valid.txt --tokens   # also show the tokens
make test                              # run all examples and check their output
make clean
```

The exit code is `0` on success, `1` for a compile error, and `2` for a bad command line or a missing file.

## Web playground

```bash
make web        # then open http://localhost:8795
```

`web/server.py` (Python standard library only) runs the real `./errorbuddy` binary on
whatever you type and shows the result: the error line highlighted in the editor, the
message and suggestion, which phase failed, or the TAC, symbol table and tokens. It
recompiles as you type; the example buttons load the programs from `examples/`.

## Case study

`ErrorBuddy_Case_Study.pdf` studies which line an error should report. Everything in it
is reproducible with `python3 case_study/run_study.py` (plus `--hints` and `--lexer`);
`python3 case_study/make_case_study.py` rebuilds the PDF.

## Test programs

| File | Expected result |
|------|-----------------|
| `valid.txt` | Success, with TAC |
| `precedence.txt` | Success. TAC shows `b * 2` computed before `a + ...` |
| `undeclared_variable.txt` | Line 2: 'marks' has not been declared |
| `duplicate_declaration.txt` | Line 4: 'age' already declared on line 1 |
| `missing_semicolon.txt` | Line 2: expected ';' |
| `invalid_expression.txt` | Line 2: two operators in a row |
| `incorrect_parentheses.txt` | Line 2: missing ')' |
| `extra_parenthesis.txt` | Line 2: extra ')' |
| `division_by_zero.txt` | Line 3: 'zero' is 0, division by zero |
| `empty.txt` | The program is empty |

## Example

Input (`examples/precedence.txt`):

```text
int a = 5;
int b = 10;
int c = a + b * 2;
print c;
```

Output:

```text
Compilation successful!

Intermediate Code (Three-Address Code):
    a = 5
    b = 10
    t1 = b * 2
    t2 = a + t1
    c = t2
    print c

Symbol Table:
    a           int   (declared on line 1)
    b           int   (declared on line 2)
    c           int   (declared on line 3)

Phases completed:
    [OK] 1. Lexical Analysis    - 22 tokens
    [OK] 2. Syntax Analysis     - 4 statements
    [OK] 3. Semantic Analysis   - 3 variables, no errors
    [OK] 4. Intermediate Code   - 6 instructions
```

Error example (`examples/undeclared_variable.txt`):

```text
Error on line 2:
Variable 'marks' has not been declared.
Suggestion: Declare it using 'int marks = 0;' before this line.

(Found during: Semantic Analysis)
Compilation stopped. No intermediate code was generated.
```

## Why ErrorBuddy's messages help

A typical compiler error such as `error: expected ';' before 'print'` uses
grammar terms and often points to the line *after* the mistake. ErrorBuddy
instead:

- points to the line where the fix belongs
- names the variable, operator or bracket involved
- explains the rule that was broken in everyday words
- gives one concrete fix, often as code you can copy
- notices likely typos and suggests the intended word
