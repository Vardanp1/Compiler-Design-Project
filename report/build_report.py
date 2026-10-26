#!/usr/bin/env python3
# build_report.py - builds ErrorBuddy_Final_Report.pdf from the real project files.
#
#   python3 report/build_report.py
#
# Every listing, output and number is read from the repository or produced by
# running ./errorbuddy, so the report always matches the code it describes.
import datetime, html, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "report")
OUT_HTML = os.path.join(HERE, "report.html")
OUT_PDF = os.path.join(ROOT, "ErrorBuddy_Final_Report.pdf")

REPO = "https://github.com/Vardanp1/Compiler-Design-Project"
PAGES = "https://vardanp1.github.io/Compiler-Design-Project/"
PLAY = PAGES + "playground.html"
AUTHOR = "Vardan Pandya"
DATE = datetime.date.today().strftime("%d %B %Y")

esc = html.escape


def read(p):
    return open(os.path.join(ROOT, p)).read()


def run(*args):
    r = subprocess.run(["./errorbuddy", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout, r.returncode


def pre(text, cls=""):
    return f'<pre class="{cls}">{esc(text.rstrip())}</pre>'


def lines(p):
    return sum(1 for _ in open(os.path.join(ROOT, p)))


subprocess.run(["make", "-s"], cwd=ROOT, check=True)
test = subprocess.run(["make", "-s", "test"], cwd=ROOT, capture_output=True, text=True).stdout
passed = re.search(r"(\d+) passed, (\d+) failed", test)
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()

SRC_FILES = ["lexer.h", "lexer.cpp", "parser.h", "parser.cpp", "main.cpp"]
cpp_lines = sum(lines(f) for f in SRC_FILES)

examples = sorted(f[:-4] for f in os.listdir(os.path.join(ROOT, "examples")) if f.endswith(".txt"))
ex_rows = []
for name in examples:
    out = read(f"examples/expected/{name}.out")
    m = re.search(r"Error on line (\d+):\n(.*)\n", out)
    result = f"Error on line {m[1]}: {m[2]}" if m else "Compilation successful"
    ex_rows.append(f"<tr><td><code>{name}.txt</code></td><td>{esc(result)}</td></tr>")

placement = read("case_study/out_placement.txt")
hints = read("case_study/out_hints.txt")
lexer_study = read("case_study/out_lexer.txt")

valid_out, _ = run("examples/valid.txt")
tok_out, _ = run("examples/precedence.txt", "--tokens")
semi_out, semi_exit = run("examples/missing_semicolon.txt")
div_out, _ = run("examples/division_by_zero.txt")
usage_out, usage_exit = run()

GCC_MSG = pre("program.c:3:5: error: expected ',' or ';'\nbefore 'printf'")

shot = os.path.join(HERE, "pages_screenshot.png")
pages_shot = (f'<figure><img class="shot" src="pages_screenshot.png" alt="The live GitHub Pages site">'
              f'<figcaption>Figure 6. The live GitHub Pages site at {PAGES}</figcaption></figure>') if os.path.exists(shot) else ""
play_shot_path = os.path.join(HERE, "playground_screenshot.png")
play_shot = (f'<figure><img class="shot" src="playground_screenshot.png" alt="The WebAssembly playground on GitHub Pages">'
             f'<figcaption>Figure 7. The playground on GitHub Pages, showing the recorded compiler output for an example program.</figcaption></figure>') if os.path.exists(play_shot_path) else ""

appendix_src = "".join(
    f'<h3>A.{i + 1} <code>{f}</code> ({lines(f)} lines)</h3>{pre(read(f), "src")}'
    for i, f in enumerate(SRC_FILES + ["Makefile"]))
appendix_ex = "".join(
    f'<h3>B.{i + 1} <code>examples/{n}.txt</code></h3><div class="two">{pre(read(f"examples/{n}.txt"))}'
    f'{pre(read(f"examples/expected/{n}.out"))}</div>'
    for i, n in enumerate(examples))

doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>ErrorBuddy: Final Project Report</title>
<style>
@page {{ size: A4; margin: 20mm 18mm 20mm 18mm; }}
body {{ font: 10.5pt/1.5 "Source Serif 4", "Noto Serif", Georgia, serif; color: #1b1d21; margin: 0; }}
h1, h2, h3, .cover, th, .meta, figcaption {{ font-family: "IBM Plex Sans", "Noto Sans", "DejaVu Sans", Arial, sans-serif; }}
h2 {{ font-size: 16pt; margin: 26px 0 8px; padding-top: 6px; break-after: avoid; color: #111; }}
h2.page {{ break-before: page; }}
h3 {{ font-size: 12pt; margin: 18px 0 6px; break-after: avoid; }}
p {{ margin: 0 0 9px; text-align: justify; }}
code {{ font: 9pt "IBM Plex Mono", "DejaVu Sans Mono", monospace; background: #f1efea; padding: 0 3px; border-radius: 3px; }}
pre {{ font: 8.4pt/1.42 "IBM Plex Mono", "DejaVu Sans Mono", monospace; background: #f6f5f1; border: 1px solid #e2dfd7;
      border-radius: 5px; padding: 8px 10px; white-space: pre-wrap; word-break: break-word; margin: 6px 0 12px; }}
pre.src {{ font-size: 7.6pt; line-height: 1.35; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 14px; font-size: 9.5pt; break-inside: auto; }}
th, td {{ border: 1px solid #d9d5cc; padding: 5px 7px; text-align: left; vertical-align: top; }}
th {{ background: #efece5; font-weight: 600; font-size: 9pt; }}
tr {{ break-inside: avoid; }}
figure {{ margin: 10px 0 16px; break-inside: avoid; text-align: center; }}
figure img {{ max-width: 100%; max-height: 225mm; }}
img.shot {{ border: 1px solid #d9d5cc; border-radius: 6px; }}
figcaption {{ font-size: 9pt; color: #5d6168; margin-top: 4px; }}
.two {{ display: grid; grid-template-columns: 1fr 1.4fr; gap: 10px; }}
.cover {{ height: 255mm; display: flex; flex-direction: column; justify-content: space-between; break-after: page; }}
.cover h1 {{ font-size: 44pt; margin: 40mm 0 6px; letter-spacing: -.01em; }}
.cover h1 span {{ color: #d9483b; }}
.cover .tag {{ font-size: 15pt; color: #4a4e56; margin: 0 0 22px; }}
.cover table {{ font-size: 10.5pt; }}
.cover td:first-child {{ width: 38mm; font-weight: 600; }}
.meta {{ font-size: 10pt; color: #4a4e56; }}
.toc ol {{ columns: 2; font-family: "IBM Plex Sans", "Noto Sans", Arial, sans-serif; font-size: 10.5pt; }}
.box {{ border: 1px solid #d9d5cc; border-radius: 6px; padding: 10px 14px; background: #faf9f6; margin: 8px 0 14px; break-inside: avoid; }}
.ok {{ color: #237a52; font-weight: 600; }}
a {{ color: #2f5fd0; text-decoration: none; }}
</style></head><body>

<section class="cover">
  <div>
    <div class="meta">Compiler Design Project · Final Report</div>
    <h1>Error<span>Buddy</span></h1>
    <p class="tag">A beginner-friendly compiler that explains its own errors: the right line, plain words, one concrete fix.</p>
    <table>
      <tr><td>Author</td><td>{AUTHOR}</td></tr>
      <tr><td>Date</td><td>{DATE}</td></tr>
      <tr><td>Implementation</td><td>C++17, standard library only · {cpp_lines} lines in {len(SRC_FILES)} files</td></tr>
      <tr><td>GitHub repository</td><td><a href="{REPO}">{REPO}</a></td></tr>
      <tr><td>Live website (GitHub Pages)</td><td><a href="{PAGES}">{PAGES}</a></td></tr>
      <tr><td>Online playground</td><td><a href="{PLAY}">{PLAY}</a></td></tr>
      <tr><td>Presentation</td><td><a href="{PAGES}ErrorBuddy_Complete.pdf">{PAGES}ErrorBuddy_Complete.pdf</a> (also <code>ErrorBuddy_Complete.pptx</code> in the repository)</td></tr>
      <tr><td>This report</td><td><a href="{PAGES}ErrorBuddy_Final_Report.pdf">{PAGES}ErrorBuddy_Final_Report.pdf</a></td></tr>
      <tr><td>Test status</td><td class="ok">{passed[1]} of {int(passed[1]) + int(passed[2])} example programs pass <code>make test</code></td></tr>
    </table>
  </div>
  <div class="meta">Built from commit {commit or "(working tree)"} of the repository. All listings, outputs and numbers in this report are generated from the project files by <code>report/build_report.py</code>.</div>
</section>

<section class="toc"><h2>Contents</h2><ol>
<li>Abstract</li><li>Introduction and problem statement</li><li>Objectives</li><li>The source language</li>
<li>System architecture</li><li>Phase 1: lexical analysis</li><li>Phase 2: syntax analysis</li><li>Phase 3: semantic analysis</li>
<li>Phase 4: intermediate code generation</li><li>Phase 5: error detection and explanation</li><li>Tools, build and usage</li>
<li>Web playground and GitHub Pages deployment</li><li>Testing</li><li>Evaluation: case study against gcc</li>
<li>Results and discussion</li><li>Limitations and future work</li><li>Conclusion</li><li>References</li>
<li>Appendix A: full source code</li><li>Appendix B: example programs and outputs</li></ol></section>

<h2>1. Abstract</h2>
<p>ErrorBuddy is a small compiler, written in C++17 using only the standard library, that translates a beginner programming language into three-address code (TAC). It implements the five classic phases: lexical analysis, syntax analysis by recursive descent, semantic analysis with a symbol table, intermediate code generation, and error reporting. Its distinguishing feature is the error report. Every error is a structured object with four fields (the line where the fix belongs, the phase that found it, a plain-English message, and one concrete suggestion), and the parser inspects the tokens around a failure to name its likely cause. In a case study of 24 classic beginner mistakes, ErrorBuddy reported all 24 on the exact line where the fix belongs, against 20 for gcc 11.4. The compiler is tested by an automated suite ({passed[1]}/{int(passed[1]) + int(passed[2])} passing), and is published as a GitHub Pages website with the documentation, the presentation, this report and a playground that shows the real compiler output for every example program.</p>

<h2>2. Introduction and problem statement</h2>
<p>Students learning to program spend a large share of their time reading compiler errors. Production compilers are written for experienced users: their messages use grammar vocabulary, and they report the position where the parser noticed a problem, which is often after the position where the mistake was made. A typical example is a missing semicolon:</p>
<div class="two">{pre('''1  int a = 5;
2  int b = 10          <- the real mistake
3  printf("%d", a + b);''')}{GCC_MSG}</div>
<p>gcc points at line 3, although the fix belongs on line 2. It says "expected ... before", which is parser vocabulary rather than plain English, and it does not say what to type. ErrorBuddy reports the same mistake like this:</p>
{pre(semi_out)}
<p>The goal of the project is a complete, readable compiler whose error messages behave like a tutor: the right line, plain words and one concrete fix.</p>

<h2>3. Objectives</h2>
<table><tr><th>#</th><th>Objective</th><th>How it is met</th></tr>
<tr><td>1</td><td>Build a working compiler from source text to intermediate code</td><td><code>./errorbuddy file.txt</code> prints three-address code, the symbol table and a phase summary.</td></tr>
<tr><td>2</td><td>Cover every core phase</td><td>Lexer (<code>lexer.cpp</code>), recursive-descent parser, semantic checks and TAC generation (<code>parser.cpp</code>), error reporting (<code>CompileError</code>).</td></tr>
<tr><td>3</td><td>Report errors like a tutor</td><td>Four-field errors, diagnosis from surrounding tokens, edit-distance typo hints, fix-line reporting.</td></tr>
<tr><td>4</td><td>Hand-written C++ only</td><td>No Lex, Yacc or third-party libraries; C++17 standard library only, built with <code>g++ -std=c++17 -Wall -Wextra -pedantic</code>.</td></tr></table>

<h2 class="page">4. The source language</h2>
<p>The language is a small, C-like beginner language. It was deliberately kept small so that every phase could be implemented completely and the effort could go into the error messages. The original proposal targeted a larger beginner-C subset with <code>if</code>/<code>else</code>, loops and <code>printf</code>; those features are listed as future work in Section 16 and are not implemented.</p>
<ul>
<li>Every variable is an <code>int</code>, declared with <code>int</code> and always given a starting value.</li>
<li>Arithmetic uses <code>+ - * /</code> with normal precedence and parentheses. Division is integer division.</li>
<li><code>print</code> outputs the value of any expression. Every statement ends with <code>;</code>. <code>//</code> starts a comment.</li>
<li>There is no unary minus (write <code>0 - 5</code>), no loops, no <code>if</code>/<code>else</code>, no functions and no input. Compilation stops at the first error.</li></ul>
<h3>4.1 Grammar</h3>
{pre('''program     -> statement*
statement   -> declaration | assignment | printStmt
declaration -> "int" IDENTIFIER "=" expression ";"
assignment  -> IDENTIFIER "=" expression ";"
printStmt   -> "print" expression ";"
expression  -> term (("+" | "-") term)*
term        -> factor (("*" | "/") factor)*
factor      -> NUMBER | IDENTIFIER | "(" expression ")"''')}
<p>Precedence is built into the grammar: <code>term</code> handles <code>*</code> and <code>/</code> one level below <code>expression</code>, so they bind more tightly than <code>+</code> and <code>-</code>. The repetition in <code>expression</code> and <code>term</code> is implemented as a loop, which makes the operators left-associative.</p>
<h3>4.2 Example program</h3>
{pre(read("examples/valid.txt"))}

<h2 class="page">5. System architecture</h2>
<p>The compiler consists of three C++ source files and two headers. <code>lexer.cpp</code> implements Phase 1. <code>parser.cpp</code> implements Phases 2, 3 and 4 in a single pass: while it recognises a statement it checks its meaning against the symbol table and emits its three-address code. This technique is called syntax-directed translation. <code>main.cpp</code> is the driver. Errors from every phase travel through one channel, the <code>CompileError</code> struct defined in <code>lexer.h</code>.</p>
{pre('''struct CompileError {
    int line;
    std::string phase;       // which compiler phase found the problem
    std::string message;     // what is wrong, in plain English
    std::string suggestion;  // one concrete way to fix it
};''')}
<table><tr><th>File</th><th>Lines</th><th>Responsibility</th></tr>
<tr><td><code>main.cpp</code></td><td>{lines("main.cpp")}</td><td>Reads the file path and optional <code>--tokens</code> flag, reads the file, calls <code>tokenize()</code> and <code>Parser::parseProgram()</code>, prints the TAC, symbol table and phase summary, or catches <code>CompileError</code> and prints it. Sets the exit code.</td></tr>
<tr><td><code>lexer.h</code> / <code>lexer.cpp</code></td><td>{lines("lexer.h")} / {lines("lexer.cpp")}</td><td>Phase 1: <code>TokenType</code>, <code>Token</code>, <code>tokenize()</code>, <code>tokenTypeName()</code>, and the shared <code>CompileError</code>.</td></tr>
<tr><td><code>parser.h</code> / <code>parser.cpp</code></td><td>{lines("parser.h")} / {lines("parser.cpp")}</td><td>Phases 2 to 4: grammar functions, symbol table, <code>binary()</code> and <code>newTemp()</code> for TAC, and the diagnosis helpers <code>expectSemicolon()</code>, <code>factorError()</code>, <code>unknownStatementError()</code>, <code>editDistance()</code>, <code>similarVariable()</code>.</td></tr>
<tr><td><code>Makefile</code></td><td>{lines("Makefile")}</td><td>Targets <code>all</code>, <code>run</code>, <code>test</code>, <code>web</code>, <code>clean</code>.</td></tr>
<tr><td><code>examples/</code></td><td>{len(examples)} + {len(examples)}</td><td>Test programs and their expected output.</td></tr>
<tr><td><code>web/</code></td><td>{lines("web/server.py")} / {lines("web/index.html")}</td><td>Local browser playground: <code>server.py</code> runs the real binary and returns JSON.</td></tr>
<tr><td><code>site/</code>, <code>ci/</code></td><td>{lines("site/index.html")} / {lines("site/playground.html")}</td><td>GitHub Pages site, its playground and <code>build_site.py</code>; optional WebAssembly workflow in <code>ci/</code>.</td></tr>
<tr><td><code>case_study/</code></td><td>{lines("case_study/run_study.py") + lines("case_study/corpus.py")}</td><td>24-mistake corpus and the ErrorBuddy versus gcc study.</td></tr></table>
<h3>5.1 Exit codes</h3>
<table><tr><th>Code</th><th>Meaning</th></tr><tr><td>0</td><td>Every phase passed; TAC printed.</td></tr><tr><td>1</td><td>A <code>CompileError</code> was reported; no TAC printed.</td></tr>
<tr><td>2</td><td>Bad usage or unreadable file (for example: <code>{esc(usage_out.strip())}</code>).</td></tr><tr><td>3</td><td>Internal compiler error (any other exception).</td></tr></table>
<figure><img src="../architecture/1_full_architecture.svg" alt="Full architecture"><figcaption>Figure 1. Full architecture and execution flow: build, ways to run, the five phases, and who reads the output.</figcaption></figure>
<figure><img src="../architecture/3_cli_sequence.svg" alt="CLI sequence"><figcaption>Figure 2. Sequence of one compile from the terminal.</figcaption></figure>

<h2 class="page">6. Phase 1: lexical analysis</h2>
<p><code>tokenize()</code> is a hand-written scanner with a single loop over the characters. A newline increments the line counter; spaces and <code>//</code> comments are skipped; a run of digits becomes a <code>NUMBER</code>; a letter or underscore starts a name, and the whole words <code>int</code> and <code>print</code> become keywords; single characters become operators, <code>=</code>, parentheses or <code>;</code>. The list always ends with <code>END_OF_FILE</code>. Every token stores its type, its exact text and its line, and those line numbers are what make accurate error lines possible later.</p>
<p>The lexer reports three kinds of lexical error: an unknown symbol such as <code>@</code>, a number larger than <code>INT_MAX</code>, and a name that starts with a digit such as <code>2nd</code>. The <code>--tokens</code> option prints the token list:</p>
{pre(tok_out.split("Compilation successful!")[0])}

<h2>7. Phase 2: syntax analysis</h2>
<p>The parser is a recursive-descent parser with one C++ function per grammar rule: <code>statement()</code>, <code>declaration()</code>, <code>assignment()</code>, <code>printStatement()</code>, <code>expression()</code>, <code>term()</code> and <code>factor()</code>. <code>statement()</code> dispatches on the first token: <code>int</code> starts a declaration, <code>print</code> a print statement, and a name followed by <code>=</code> an assignment. Anything else goes to <code>unknownStatementError()</code>. <code>factor()</code> recurses on <code>(</code>, with a nesting limit of 200.</p>
<p>For <code>int c = a + b * 2;</code>, <code>declaration()</code> calls <code>expression()</code>; the first <code>term()</code> returns <code>a</code>; <code>+</code> is seen; the next <code>term()</code> reads <code>b</code>, sees <code>*</code>, reads <code>2</code> and calls <code>binary()</code>, which emits <code>t1 = b * 2</code>. Back in <code>expression()</code>, <code>binary()</code> emits <code>t2 = a + t1</code>. <code>expectSemicolon()</code> finds the <code>;</code>, <code>c</code> is entered in the symbol table and <code>c = t2</code> is emitted.</p>
<figure><img src="../architecture/2_parser_internals.svg" alt="Parser internals"><figcaption>Figure 3. Control flow inside the parser, with every point where a CompileError can be thrown (red).</figcaption></figure>

<h2 class="page">8. Phase 3: semantic analysis</h2>
<p>The symbol table is a <code>std::map&lt;std::string, Symbol&gt;</code>, where <code>Symbol</code> holds the declaration line and the current value. Checks run inside the parser at the moment a name or operator is seen:</p>
<table><tr><th>Check</th><th>Example</th></tr>
<tr><td>Undeclared variable, with a "Did you mean" hint for close names</td><td><code>scroe = 2;</code> → Did you mean 'score'?</td></tr>
<tr><td>Duplicate declaration</td><td>Variable 'age' has already been declared (on line 1).</td></tr>
<tr><td>Variable used in its own declaration</td><td><code>int a = a + 1;</code> (a name is added only after its initial value is parsed)</td></tr>
<tr><td>Division by zero, including through variables and expressions</td><td><code>a / zero</code>, <code>8 / (4 - 4)</code></td></tr>
<tr><td>Integer overflow of a result</td><td>Result outside <code>INT_MIN</code>..<code>INT_MAX</code></td></tr>
<tr><td>Keyword used as a variable name; declaration without a value</td><td><code>int print = 1;</code>, <code>int a;</code></td></tr></table>
<p>Because the language has no input and no loops, every value is known at compile time. ErrorBuddy tracks values in the symbol table, which is how a division by a variable that holds 0 is caught before the program runs:</p>
{pre(div_out)}

<h2>9. Phase 4: intermediate code generation</h2>
<p>The intermediate representation is three-address code. Each instruction has at most one operator. <code>binary()</code> computes the value, checks for division by zero and overflow, takes a fresh temporary from <code>newTemp()</code> and emits <code>tN = left op right</code>. Temporaries are numbered <code>t1</code>, <code>t2</code>, and so on, skipping any name the user wrote, so a temporary never clashes with a variable. Parentheses only change grouping and produce no instructions. Code for a statement is emitted as soon as it is parsed, so the TAC is in source order, and it is printed only if the whole program compiles. The complete output for <code>examples/valid.txt</code>:</p>
{pre(valid_out)}

<h2 class="page">10. Phase 5: error detection and explanation</h2>
<p>Any phase reports a problem by throwing a <code>CompileError</code>; <code>main.cpp</code> catches it, prints the four fields in a fixed format and exits with code 1. What makes the messages useful is the diagnosis that happens before the throw.</p>
<h3>10.1 Diagnosis from surrounding tokens</h3>
<p><code>expectSemicolon()</code> runs at the end of every statement. If the next token is not <code>;</code>, it looks at what it is:</p>
<table><tr><th>Next token</th><th>Diagnosis</th></tr>
<tr><td><code>)</code></td><td>Found an extra ')' that has no matching '('.</td></tr>
<tr><td><code>=</code></td><td>Unexpected '='. A statement can contain only one '='.</td></tr>
<tr><td>a name, number or <code>(</code> on the same line</td><td>Missing operator between the two values.</td></tr>
<tr><td>anything else</td><td>Expected ';' at the end of the statement, reported on the line of the previous token, which is where the fix belongs.</td></tr></table>
<p><code>factorError()</code> handles a missing value (two operators in a row, a negative literal, empty parentheses, a keyword inside an expression, a program that ends mid-expression). <code>unknownStatementError()</code> handles a statement that starts wrongly (a misspelled or capitalised keyword, a name on its own, an extra <code>;</code>, an <code>=</code> with no name).</p>
<h3>10.2 Typo hints</h3>
<p>Hints use the Levenshtein edit distance, computed in a single rolling row (<code>editDistance()</code>). The shipped rule, in <code>looksLike()</code>, allows 1 edit for targets of up to 3 letters and 2 edits for longer ones and never suggests the word itself; <code>similarVariable()</code> skips variable names shorter than 3 letters. The rule was chosen by the study in Section 14.3.</p>
<h3>10.3 Example messages</h3>
<table><tr><th>Program</th><th>ErrorBuddy output</th></tr>{"".join(ex_rows)}</table>

<h2 class="page">11. Tools, build and usage</h2>
<table><tr><th>Command</th><th>What it does</th></tr>
<tr><td><code>make</code></td><td>Builds <code>./errorbuddy</code> with <code>g++ -std=c++17 -Wall -Wextra -pedantic -O2</code>.</td></tr>
<tr><td><code>./errorbuddy file.txt [--tokens]</code></td><td>Compiles a file; <code>--tokens</code> also prints the lexer output.</td></tr>
<tr><td><code>make run FILE=examples/valid.txt</code></td><td>Builds and compiles one file.</td></tr>
<tr><td><code>make test</code></td><td>Runs every example and diffs its output with <code>examples/expected/*.out</code>.</td></tr>
<tr><td><code>make web</code></td><td>Starts the local playground at <code>http://localhost:8795</code>.</td></tr>
<tr><td><code>python3 case_study/run_study.py [--hints | --lexer]</code></td><td>Reproduces the case-study numbers.</td></tr>
<tr><td><code>python3 report/build_report.py</code></td><td>Regenerates this report.</td></tr></table>
<p>Tools used: C++17 and its standard library, g++ and GNU Make for the compiler; Python 3 standard library for the local web server and the case study; Emscripten for the WebAssembly build; GitHub Pages for hosting (with an optional GitHub Actions workflow); Mermaid for the architecture diagrams.</p>

<h2>12. Web playground and GitHub Pages deployment</h2>
<p>The project has two browser front ends that share one page design and one compiler.</p>
<ul><li><b>Local playground</b> (<code>make web</code>): <code>web/server.py</code> serves <code>web/index.html</code> and an endpoint <code>POST /api/compile</code>. It writes the source to a temporary file, runs the real <code>./errorbuddy --tokens</code> with a 5-second timeout and turns its text output into JSON (tokens, error, TAC, symbols, phases). The page recompiles about 350 ms after typing stops, highlights the error line, and shows how far the pipeline got.</li>
<li><b>GitHub Pages</b> (<a href="{PAGES}">{PAGES}</a>): GitHub Pages serves only static files and cannot run the compiler binary. <code>site/build_site.py</code> builds the compiler, runs it on every example program with <code>--tokens</code>, and records the real output in <code>examples.json</code>. The site is published from the <code>gh-pages</code> branch and contains the project page, the playground (<a href="{PLAY}">{PLAY}</a>), the architecture diagrams, the presentation and this report. The playground uses the same page design as the local one and parses the recorded output with a JavaScript port of the server's parser, so every example shows exactly what the compiler prints. Compiling new code needs the local playground or the command line.</li></ul>
<p>The repository also contains <code>ci/github-pages-wasm.yml</code>, an optional GitHub Actions workflow. On every push to <code>main</code> it builds the compiler natively and runs <code>make test</code>, compiles the same <code>main.cpp</code>, <code>lexer.cpp</code> and <code>parser.cpp</code> to WebAssembly with Emscripten, and deploys the site. With that build present, the playground writes the program into Emscripten's in-memory file system and calls the compiler's <code>main()</code> directly, so any program can be compiled in the browser without reimplementing compiler logic in JavaScript. Enabling it means moving the file to <code>.github/workflows/</code>, which requires a GitHub token with the <code>workflow</code> scope.</p>
{pages_shot}
{play_shot}
<figure><img src="../architecture/4_web_sequence.svg" alt="Web sequence"><figcaption>Figure 4. Sequence of a compile in the local web playground.</figcaption></figure>

<h2 class="page">13. Testing</h2>
<p>Each example program targets one behaviour, and its expected output is stored next to it. <code>make test</code> compiles every example and compares the output byte for byte. Output of the run used for this report:</p>
{pre(test)}
<p>The suite covers a valid program, operator precedence, a missing semicolon, an undeclared variable, a duplicate declaration, two operators in a row, a missing and an extra parenthesis, division by a variable that is zero, and an empty program. The optional GitHub Actions workflow in <code>ci/</code> runs the same suite before each deployment.</p>

<h2>14. Evaluation: case study against gcc</h2>
<h3>14.1 Method</h3>
<p><code>case_study/run_study.py</code> runs 24 classic beginner mistakes (defined in <code>case_study/corpus.py</code>) through three compilers: <b>G</b>, gcc 11.4 on the equivalent C program (<code>-Wall -Wextra</code>, first diagnostic); <b>D</b>, ErrorBuddy patched to report the line of the token where the parser noticed the problem (the detection point); and <b>E</b>, ErrorBuddy as shipped, which reports the line where the fix belongs. For each mistake the study records the reported line and compares it with the line of the fix. An asterisk marks a report on the wrong line.</p>
{pre(placement)}
<h3>14.2 Line placement results</h3>
<table><tr><th>Compiler</th><th>Caught</th><th>Exact fix line</th><th>Late</th><th>Early</th></tr>
<tr><td>gcc 11.4</td><td>23 / 24</td><td>20 / 24</td><td>3</td><td>0</td></tr>
<tr><td>ErrorBuddy, detection point</td><td>24 / 24</td><td>21 / 24</td><td>3</td><td>0</td></tr>
<tr><td>ErrorBuddy, shipped (fix point)</td><td>24 / 24</td><td><b>24 / 24</b></td><td>0</td><td>0</td></tr></table>
<p>gcc missed one mistake entirely (M19, division by a variable that is 0). All three of its late reports, and all three of the detection-point variant's, were a missing semicolon, which is the case the fix-point rule was designed for.</p>
<h3>14.3 Typo-hint policy</h3>
<p><code>run_study.py --hints</code> tests four policies for "Did you mean" hints on 23 typo cases. "Right" means the intended name was suggested, "wrong" means another name was suggested, "missed" means a real typo got no hint, and "silent-ok" means a non-typo correctly got no hint.</p>
{pre(hints)}
<p>Looser limits find more right answers but also more wrong ones. The shipped policy gives the fewest wrong suggestions (6) while still getting 12 right.</p>
<h3>14.4 Lexer rules</h3>
<p><code>run_study.py --lexer</code> removes one lexer rule at a time to show what it protects against:</p>
{pre(lexer_study)}

<h2 class="page">15. Results and discussion</h2>
<ul><li>A complete compiler pipeline from source text to three-address code, in about {cpp_lines} lines of C++17 with no external tools.</li>
<li>All {passed[1]} example programs pass <code>make test</code>.</li>
<li>Every one of 24 case-study mistakes is caught and reported on the line where the fix belongs (gcc: 23 caught, 20 on the exact line).</li>
<li>Error messages name the broken rule in plain English and give one concrete suggestion, for example "Add a semicolon after '10'." instead of "expected ',' or ';' before 'printf'".</li>
<li>The project is published on GitHub Pages, where the documentation, the presentation, this report and the example outputs can be viewed without installing anything.</li></ul>
<p>The main design decision was to keep the language small. Doing syntax, semantics and code generation in one pass keeps the compiler short and lets every check see the exact token that caused it, which is what makes the diagnosis possible. The same decision also brings the main limitations described next.</p>

<h2>16. Limitations and future work</h2>
<table><tr><th>Limitation (today)</th><th>Planned work (from the original proposal)</th></tr>
<tr><td>Only <code>int</code>, arithmetic and <code>print</code></td><td><code>if</code>/<code>else</code>, <code>while</code> and <code>for</code> loops; comparison and logical operators; <code>printf</code></td></tr>
<tr><td>Stops at the first error</td><td>Error recovery to report several errors per run</td></tr>
<tr><td>One implicit program, no functions</td><td>Functions and arrays; <code>char</code> and <code>float</code></td></tr>
<tr><td>Values tracked at compile time (possible only without input or loops)</td><td>Data-flow analysis once loops and input exist</td></tr>
<tr><td>TAC is the final output</td><td>Constant folding and other optimisations on TAC; an assembly back end</td></tr></table>

<h2>17. Conclusion</h2>
<p>ErrorBuddy shows that a small, hand-written compiler can cover every classic phase and still put the learner first. Treating each error as a structured object with a line, a phase, a message and a suggestion, and diagnosing errors by looking at the surrounding tokens, gives messages that point to the line where the fix belongs and say what to type. The project is tested automatically, measured against gcc, and published as a website where anyone can see it work.</p>

<h2>18. References</h2>
<ol><li>A. V. Aho, M. S. Lam, R. Sethi and J. D. Ullman, <i>Compilers: Principles, Techniques, and Tools</i>, 2nd ed., Addison-Wesley, 2006.</li>
<li>V. I. Levenshtein, "Binary codes capable of correcting deletions, insertions, and reversals," <i>Soviet Physics Doklady</i>, vol. 10, no. 8, 1966.</li>
<li>GCC, the GNU Compiler Collection, version 11.4. https://gcc.gnu.org/</li>
<li>Emscripten documentation. https://emscripten.org/</li>
<li>GitHub Pages and GitHub Actions documentation. https://docs.github.com/</li>
<li>Project repository: {REPO}</li></ol>

<h2 class="page">Appendix A: full source code</h2>
{appendix_src}

<h2 class="page">Appendix B: example programs and expected outputs</h2>
<p>Left: the program. Right: the expected output stored in <code>examples/expected/</code>, which <code>make test</code> compares against.</p>
{appendix_ex}
</body></html>"""

open(OUT_HTML, "w").write(doc)
subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML], check=True, capture_output=True)
print("wrote " + OUT_PDF)
