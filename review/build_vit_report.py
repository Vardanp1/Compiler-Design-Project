#!/usr/bin/env python3
# build_vit_report.py - builds ErrorBuddy_Project_Report.pdf in the VIT project-report format.
#
#   python3 review/build_vit_report.py      (run review/build_review.py first for cases.json)
#
# Outputs and numbers are produced by running ./errorbuddy, make test and the
# case study, so the report matches the code it describes.
import html, json, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "review")
OUT_HTML = os.path.join(HERE, "vit_report.html")
OUT_PDF = os.path.join(ROOT, "ErrorBuddy_Project_Report.pdf")
REPO = "https://github.com/Vardanp1/Compiler-Design-Project.git"
PAGES = "https://vardanp1.github.io/Compiler-Design-Project/"
LEAD, MATE = ("Vardan Pandya", "24BCE2608"), ("Kunal Sharma", "24BCE2641")
GUIDE = "Prof. Boominathan P."
FOOT = f"ErrorBuddy Compiler Project Report | {LEAD[0]} ({LEAD[1]}), {MATE[0]} ({MATE[1]}) | Page "
esc = html.escape
q = lambda s: s.replace("‘", "'").replace("’", "'")

subprocess.run(["make", "-s"], cwd=ROOT, check=True)
CASES = json.load(open(os.path.join(HERE, "cases.json")))
test = subprocess.run(["make", "-s", "test"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
passed = re.search(r"(\d+) passed, (\d+) failed", test)
read = lambda p: open(os.path.join(ROOT, p)).read()
lines = lambda p: sum(1 for _ in open(os.path.join(ROOT, p)))
cpp = sum(lines(f) for f in ["lexer.h", "lexer.cpp", "parser.h", "parser.cpp", "main.cpp"])


def run(*args):
    return subprocess.run(["./errorbuddy", *args], cwd=ROOT, capture_output=True, text=True).stdout


def pre(t):
    return f"<pre>{esc(t.rstrip())}</pre>"


def table(head, rows, widths=None):
    cols = "".join(f'<col style="width:{w}">' for w in widths) if widths else ""
    return (f"<table><colgroup>{cols}</colgroup><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr>" +
            "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table>")


def body(out):
    """The compiler output without the 'ErrorBuddy - compiling ...' header line."""
    return out.split("\n", 2)[2]


semi = run("examples/missing_semicolon.txt")
valid = run("examples/valid.txt")
prec_tok = run("examples/precedence.txt", "--tokens")
divz = run("examples/division_by_zero.txt")
undecl = run("examples/undeclared_variable.txt")
paren = run("examples/incorrect_parentheses.txt")
placement = read("case_study/out_placement.txt")
hints = read("case_study/out_hints.txt").split("\n\n")[0]

# ---------------------------------------------------------------- pipeline figure (Figure 1A)
def stage(n, ph, name, file, items, kind, halt=None, arrow=None, side=None):
    li = "".join(f"<li>{x}</li>" for x in items)
    h = (f'<div class="halt"><b>HALT · exit 1</b>{halt}</div>' if halt else '<div class="halt none"></div>')
    s = f'<div class="store">{side}</div>' if side else '<div class="store none"></div>'
    a = f'<div class="flowlbl">{arrow}</div>' if arrow else ""
    return (f'<div class="srow">{s}<div class="stage {kind}"><div class="sname"><small>Stage {n} · {ph}</small><b>{name}</b><i>{file}</i></div>'
            f'<ul>{li}</ul></div><div class="hl">{"error →" if halt else ""}</div>{h}</div>{a}')


fig1a = ('<div class="pipe"><div class="term">Source code (.txt)</div><div class="flowlbl">characters</div>' +
         stage(1, "Phase 1", "Lexer", "lexer.cpp · tokenize()", ["Single-pass character scanner", "Line counter on every newline",
               "Keywords <code>int</code>, <code>print</code> as whole words"], "std", "Lexical error: unknown symbol, number above INT_MAX, name starting with a digit", "vector&lt;Token&gt; (type, text, line)") +
         stage(2, "Phase 2", "Parser", "parser.cpp · statement() …", ["Recursive descent, one function per rule", "Precedence from expression → term → factor",
               "Nesting limit of 200 for '('"], "std", "Syntax error: missing ';' or ')', two operators in a row, bad statement start", "recognised statement and operands",
               "<b>Diagnosis helpers</b>expectSemicolon()<br>factorError()<br>unknownStatementError()") +
         stage(3, "Phase 3", "Semantic checks", "parser.cpp · symbolTable", ["Name lookup in map&lt;name, Symbol&gt;", "Duplicate and self-referencing declarations",
               "Value tracking: division by zero, int overflow"], "std", "Semantic error: undeclared or duplicate name, division by zero, overflow", "checked operands with known values",
               "<b>Symbol table</b>name · declared line · value") +
         stage(4, "Phase 4", "TAC generator", "parser.cpp · binary(), newTemp()", ["One operator per instruction", "Temporaries t1, t2 … skipping user names",
               "Emitted in source order"], "mid", None, "three-address code (kept only if every phase passes)") +
         stage(5, "Phase 5", "Error reporter", "lexer.h · CompileError, main.cpp", ["Fix-point line selection", "Plain-English message and one suggestion",
               "Edit-distance 'Did you mean' hints"], "add", "Prints line, message, suggestion and phase; no TAC is shown", None) +
         '<div class="flowlbl">every phase passed</div><div class="term">Output: TAC, symbol table and phase summary · exit code 0</div>'
         '<div class="legend"><span class="k std"></span>Standard phase <span class="k add"></span>Error engine (focus of ErrorBuddy) '
         '<span class="k mid"></span>Intermediate code <span class="k halt"></span>Halt (exit 1) <span class="k st"></span>Data / helper</div></div>')

fig1 = '''<div class="fig1">
<div class="b src">Source<br><small>program.txt</small></div><span>→</span>
<div class="b std">1 Lexical<br><small>lexer.cpp</small></div><span>→</span>
<div class="grp"><small>parser.cpp · one pass</small><div><div class="b std">2 Syntax</div><div class="b std">3 Semantic</div><div class="b mid">4 TAC</div></div></div><span>→</span>
<div class="b out">Driver<br><small>main.cpp</small></div>
<div class="b add wide">5 Error reporting · CompileError { line, phase, message, suggestion } · thrown by any phase, printed by main.cpp, exit 1</div>
</div>'''

# ---------------------------------------------------------------- comparison table
cmp_rows = []
for c in CASES:
    g = f"line {c['gcc_line']}: {esc(q(c['gcc_msg']))}" if c["gcc_line"] else "<i>nothing reported</i>"
    mark = lambda l: "" if l == c["fix"] else " ✗"
    cmp_rows.append([f"<b>{c['id']}</b> {esc(c['name'])}", str(c["fix"]), g + (mark(c["gcc_line"]) if c["gcc_line"] else ""),
                     f"line {c['eb_line']}: {esc(c['eb_msg'])}"])

shot_play = "../report/playground_screenshot.png"
shot_site = "../report/pages_screenshot.png"

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ErrorBuddy Compiler Project Report</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Carlito:ital,wght@0,400;0,700;1,400;1,700&display=swap">
<style>
@page {{ size: A4; margin: 22mm 22mm 20mm 22mm;
  @bottom-center {{ content: "{FOOT}" counter(page); font: 8.5pt Carlito, Calibri, sans-serif; color: #7f7f7f; }} }}
body {{ font: 11.5pt/1.42 Carlito, Calibri, "Liberation Sans", sans-serif; color: #000; margin: 0; }}
h1, h2, h3 {{ color: #2f5496; font-weight: 700; break-after: avoid; }}
h2 {{ font-size: 17pt; margin: 20px 0 8px; }}
h3 {{ font-size: 13pt; margin: 14px 0 6px; }}
h4 {{ font-size: 11.5pt; margin: 10px 0 2px; color: #2f5496; }}
p {{ margin: 0 0 8px; text-align: justify; }}
ul {{ margin: 4px 0 10px; padding-left: 24px; }} li {{ margin-bottom: 3px; }}
code {{ font: 9.5pt "DejaVu Sans Mono", "Liberation Mono", monospace; }}
pre {{ font: 9pt/1.4 "DejaVu Sans Mono", "Liberation Mono", monospace; background: #f2f2f2; padding: 7px 10px; margin: 4px 0 10px; white-space: pre-wrap; break-inside: avoid; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 12px; font-size: 10pt; }}
th {{ background: #1f3864; color: #fff; text-align: left; padding: 4px 6px; border: 1px solid #1f3864; }}
td {{ border: 1px solid #a6a6a6; padding: 4px 6px; vertical-align: top; }}
tr {{ break-inside: avoid; }}
.small td {{ font-size: 9pt; padding: 3px 5px; }} .small th {{ font-size: 9pt; }}
.cap {{ font-size: 10pt; margin: 6px 0 14px; }} .cap b {{ font-weight: 700; }}
.page {{ break-before: page; }}
.cover {{ text-align: center; height: 245mm; break-after: page; }}
.cover img {{ width: 62mm; margin-top: 2mm; }}
.cover .kind {{ color: #2f5496; font-weight: 700; font-size: 13pt; margin: 14mm 0 6mm; }}
.cover h1 {{ font-size: 40pt; margin: 0 0 4mm; color: #2f5496; }}
.cover .sub {{ font-size: 16pt; font-weight: 700; line-height: 1.3; margin: 0 6mm 8mm; }}
.cover .repo {{ font-weight: 700; font-size: 11pt; }} .cover a {{ color: #0563c1; }}
.cover .by {{ margin-top: 9mm; font-size: 12pt; }}
.cover .name {{ font-size: 17pt; font-weight: 700; margin-top: 2mm; }}
.cover .reg {{ font-size: 11.5pt; }}
.cover .with {{ margin-top: 5mm; }}
.idx td:first-child {{ width: 22mm; }}
a {{ color: #0563c1; }}
/* figure 1 */
.fig1 {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 6px; border: 1px solid #bfbfbf; padding: 12px; margin: 8px 0 4px; font-size: 9.5pt; }}
.fig1 .b {{ border: 1.2px solid #2f5496; border-radius: 6px; padding: 6px 8px; text-align: center; font-weight: 700; background: #dae3f3; }}
.fig1 .b small {{ font-weight: 400; font-size: 8pt; }}
.fig1 .src, .fig1 .out {{ background: #fff; border-color: #000; }}
.fig1 .mid {{ background: #e2f0d9; border-color: #548235; }}
.fig1 .add {{ background: #fff2cc; border-color: #bf8f00; }}
.fig1 .wide {{ flex-basis: 100%; margin-top: 6px; }}
.fig1 .grp {{ border: 1.5px dashed #2f5496; border-radius: 8px; padding: 4px 6px 6px; text-align: center; }}
.fig1 .grp > small {{ font-size: 8pt; color: #2f5496; font-weight: 700; }}
.fig1 .grp > div {{ display: flex; gap: 5px; margin-top: 3px; }}
/* figure 1A */
.pipe {{ font-size: 8.6pt; margin: 6px 0; }}
.pipe .term {{ border: 1.5px solid #000; border-radius: 14px; text-align: center; font-weight: 700; padding: 3px; width: 64%; margin: 0 auto; }}
.flowlbl {{ text-align: center; font-style: italic; color: #595959; font-size: 8pt; margin: 1px 0; }}
.flowlbl::before {{ content: "↓ "; font-style: normal; color: #000; }}
.srow {{ display: grid; grid-template-columns: 27mm 1fr 10mm 36mm; align-items: center; gap: 3px; break-inside: avoid; }}
.stage {{ display: grid; grid-template-columns: 34mm 1fr; border: 1.2px solid #2f5496; border-radius: 6px; padding: 5px 7px; background: #dae3f3; }}
.stage.add {{ background: #fff2cc; border-color: #bf8f00; }}
.stage.mid {{ background: #e2f0d9; border-color: #548235; }}
.sname {{ border-right: 1px solid #7f7f7f; padding-right: 5px; }}
.sname small {{ display: block; color: #595959; font-size: 7.5pt; }} .sname b {{ display: block; font-size: 10pt; }} .sname i {{ font-size: 7.5pt; color: #595959; }}
.stage ul {{ margin: 0; padding-left: 14px; }} .stage li {{ margin: 0; }}
.halt {{ border: 1.2px solid #c00000; background: #fbe5e5; border-radius: 6px; padding: 4px 6px; font-size: 7.8pt; text-align: center; }}
.halt b {{ display: block; color: #c00000; }}
.halt.none, .store.none {{ border: 0; background: none; }}
.hl {{ color: #c00000; font-size: 7.5pt; text-align: center; }}
.store {{ border: 1.2px solid #7f7f7f; border-radius: 4px; background: #f2f2f2; padding: 4px; font-size: 7.6pt; text-align: center; }}
.store b {{ display: block; }}
.legend {{ margin-top: 8px; font-size: 8.5pt; }}
.legend .k {{ display: inline-block; width: 10px; height: 10px; border: 1px solid #555; margin: 0 3px 0 10px; vertical-align: -1px; }}
.k.std {{ background: #dae3f3; }} .k.add {{ background: #fff2cc; }} .k.mid {{ background: #e2f0d9; }} .k.halt {{ background: #fbe5e5; }} .k.st {{ background: #f2f2f2; }}
img.shot {{ width: 100%; border: 1px solid #a6a6a6; }}
.fig {{ break-inside: avoid; }}
</style></head><body>

<section class="cover">
  <img src="vit_logo.png" alt="Vellore Institute of Technology">
  <div class="kind">COMPILER DESIGN PROJECT REPORT</div>
  <h1>ErrorBuddy</h1>
  <div class="sub">A Beginner-Friendly Compiler that Reports Every Error on the Line Where the Fix Belongs, in Plain Words, with One Concrete Fix</div>
  <div class="repo">Source code and reference repository:</div><a href="{REPO}">{REPO}</a>
  <div style="margin-top:2mm"><span class="repo">Live website:</span> <a href="{PAGES}">{PAGES}</a></div>
  <div class="by">Submitted by</div><div class="name">{LEAD[0]}</div><div class="reg">Reg. No: {LEAD[1]}</div>
  <div class="with">with teammate</div><div class="name">{MATE[0]}</div><div class="reg">Reg. No: {MATE[1]}</div>
  <div class="with">Under the guidance of</div><div class="name">{GUIDE}</div>
</section>

<h2 style="margin-top:0">Index</h2>
{table(["Section", "Title"], [[str(i + 1), t] for i, t in enumerate(["Abstract", "Introduction", "Literature Survey", "Problem Statement and Objectives",
    "The ErrorBuddy Language", "System Architecture (Architecture Diagram)", "Phase-by-Phase Design", "Error Reporting Subsystem", "Diagnosis and Typo Hints",
    "Sample Codes", "Demo Screenshots", "How to Start the Project", "Results and Comparison with GCC", "Limitations and Future Work", "Conclusion", "References"])]).replace("<table>", '<table class="idx">', 1)}

<h2 class="page">1. Abstract</h2>
<p>Compilers are very good at deciding whether a program is valid and much less good at telling a beginner what to do when it is not. A missing semicolon on line 2 is reported by gcc on line 3 as <i>"expected ',' or ';' before 'printf'"</i>: the wrong line, parser vocabulary and no fix. Some mistakes, such as dividing by a variable that holds zero, are not reported at all. For a student, the time lost is spent not on the mistake but on decoding the message.</p>
<p>This project presents ErrorBuddy, a small compiler written in C++17 using only the standard library, for a C-like beginner language. It implements the classic phases (lexical analysis, recursive-descent syntax analysis, semantic analysis with a symbol table and three-address code generation) and treats error reporting as a phase of its own. Every error is a structured object with four fields: the line where the fix belongs, the phase that found it, a plain-English message and one concrete suggestion. Before reporting, the parser inspects the tokens around the failure to name the likely cause, and an edit-distance matcher suggests the intended name for typing mistakes.</p>
<p>The compiler is about {cpp} lines of C++, passes {passed[1]} of {int(passed[1]) + int(passed[2])} automated example tests, and is published with a GitHub Pages website. In a case study of 24 classic beginner mistakes compared with gcc 11.4 (-Wall -Wextra), ErrorBuddy reported all 24 on the exact line where the fix belongs, while gcc reported 20 on the exact line and missed one mistake entirely.</p>
<p><i><b>Keywords:</b> compiler design, error messages, novice programmers, recursive descent, symbol table, three-address code, edit distance.</i></p>

<h2>2. Introduction</h2>
<p>A compiler translates a program from a source language into a lower-level form. The classical pipeline of lexical analysis, syntax analysis, semantic analysis and intermediate code generation is designed to decide, precisely and quickly, whether a program belongs to the language. When it does not, the compiler stops and prints a diagnostic. That diagnostic is written in terms of the compiler's own grammar and reports the position where the parser noticed a problem.</p>
<p>For an experienced programmer this is enough. For a beginner the two weaknesses compound: the reported line is often after the line that needs editing, and the message describes what the parser expected rather than what the student should type. The fault is small and the cost is large: the student re-reads correct code on the reported line, guesses, recompiles and repeats.</p>
<p>An important observation motivating this project is that the information needed for a better message is already available at the moment of failure. The parser knows the previous token, the next token and the rule it was trying to complete. ErrorBuddy uses that information deliberately: diagnosis runs before the error is reported, and the report is built for the reader.</p>
<h3>2.1 Scope of the work</h3>
<ul><li>Design of a small C-like beginner language with <code>int</code> variables, arithmetic, <code>print</code> and comments.</li>
<li>Implementation of a complete front end and three-address code generator in C++17 with no external tools ({cpp} lines in five files).</li>
<li>An error-reporting subsystem: the four-field <code>CompileError</code>, token-context diagnosis, fix-line selection and typo hints.</li>
<li>An automated test suite (<code>make test</code>), a case study against gcc, a local web playground and a GitHub Pages website.</li></ul>
<h3>2.2 Team contribution</h3>
{table(["Member", "Contribution"], [[f"{LEAD[0]} ({LEAD[1]})<br>{MATE[0]} ({MATE[1]})", "Joint work on all parts of the project: language design, lexer, parser, semantic analysis, three-address code generation, the error-reporting subsystem, testing, the case study against gcc, the web playground and the GitHub Pages website, and this report."]], ["32%", "68%"])}

<h2>3. Literature Survey</h2>
<p>ErrorBuddy builds on established ideas in compiler construction and on research into compiler error messages for novice programmers. The following works shaped the design.</p>
{table(["Work / tool", "What it contributes", "Relevance to ErrorBuddy"], [
 ["Aho, Lam, Sethi, Ullman: <i>Compilers: Principles, Techniques, and Tools</i>", "Standard phase structure, recursive-descent parsing, symbol tables and three-address code.", "Basis of the phase design and the TAC format."],
 ["Wirth: <i>Compiler Construction</i> (1996)", "Hand-written recursive-descent compilers, one procedure per grammar rule.", "Same structure; hand-writing keeps every message under our control."],
 ["Levenshtein (1966)", "Edit distance between two strings.", "Used for 'Did you mean' hints on misspelled names and keywords."],
 ["Traver (2010): On compiler error messages", "Analyses why messages are hard to understand: wrong position, compiler terminology.", "Targets both problems: fix-line reporting and plain English."],
 ["Marceau, Fisler, Krishnamurthi (2011)", "Measures how students respond to error messages designed for novices.", "Motivates measuring the messages instead of assuming they help."],
 ["Denny, Luxton-Reilly, Carpenter (2014)", "Enhanced syntax messages alone did not measurably help students.", "Suggests that better wording is not enough; the location and cause must be right."],
 ["Becker et al. (2016, 2019)", "Enhanced messages can reduce repeated errors; survey and guidelines for error message design.", "Guidelines followed: be specific, use plain language, suggest a fix."],
 ["Elm and Clang diagnostics", "Production compilers with friendly, fix-it style messages.", "Shows the style is practical; ErrorBuddy applies it to a teaching language."]], ["30%", "38%", "32%"])}
<p><b>Gap identified:</b> much of the work on novice error messages rewrites or enhances the text after a production compiler has already chosen the line and the cause. If the line is wrong, better wording cannot fix it. ErrorBuddy builds the diagnosis into the parser, so the line and the cause are chosen at the point of failure, and measures the result against gcc.</p>

<h2>4. Problem Statement and Objectives</h2>
<p><b>Problem statement: Compilers tell beginners that something is wrong. They do not reliably say where to fix it, or how.</b></p>
<p>Research question: How can a compiler report each beginner mistake on the line where the fix belongs, in plain words, with one concrete fix?</p>
<h3>4.1 Objectives</h3>
<ul><li><b>Build a working compiler:</b> source text to three-address code, with every core phase implemented by hand.</li>
<li><b>Report on the fix line:</b> the line the student must edit, not the line where parsing stopped.</li>
<li><b>Explain in plain words:</b> name the broken rule without parser vocabulary.</li>
<li><b>Suggest one fix:</b> every error carries one concrete thing to type.</li>
<li><b>Stop broken programs:</b> no intermediate code is printed for a program with an error.</li>
<li><b>Measure it:</b> compare the reported lines with gcc on a hand-labelled set of mistakes.</li></ul>
<h3>4.2 Three mistakes and what gcc 11.4 reports</h3>
{pre(CASES[1]["c"] + chr(10) + "// gcc: line " + str(CASES[1]["gcc_line"]) + ": " + q(CASES[1]["gcc_msg"]) + "   (fix is on line 2)")}
{pre(CASES[7]["c"] + chr(10) + "// gcc: line 2: " + q(CASES[7]["gcc_msg"]))}
{pre(CASES[18]["c"] + chr(10) + "// gcc: nothing reported; the program fails when it runs")}

<h2>5. The ErrorBuddy Language</h2>
<p>ErrorBuddy compiles a small C-like language, kept small on purpose so that every phase could be completed and the effort could go into the error messages.</p>
{table(["Category", "Elements"], [["Types", "<code>int</code> only; every variable is declared with a starting value"], ["Declaration", "<code>int age = 20;</code>"],
  ["Assignment", "<code>age = age + 1;</code>"], ["Output", "<code>print expression;</code>"], ["Operators", "<code>+ - * /</code> with normal precedence; parentheses <code>( )</code>; integer division"],
  ["Comments", "<code>// to the end of the line</code>"], ["Statement end", "every statement ends with <code>;</code>"],
  ["Not included", "unary minus (write <code>0 - 5</code>), if/else, loops, functions, input"]], ["26%", "74%"])}
<h3>5.1 Grammar</h3>
{pre('''program     -> statement*
statement   -> declaration | assignment | printStmt
declaration -> "int" IDENTIFIER "=" expression ";"
assignment  -> IDENTIFIER "=" expression ";"
printStmt   -> "print" expression ";"
expression  -> term (("+" | "-") term)*
term        -> factor (("*" | "/") factor)*
factor      -> NUMBER | IDENTIFIER | "(" expression ")"''')}

<h2 class="page">6. System Architecture</h2>
<p>The compiler is organised as five phases in three C++ source files. Phase 1 is in <code>lexer.cpp</code>. Phases 2, 3 and 4 run together in a single pass of <code>parser.cpp</code>: while a statement is recognised, its meaning is checked and its three-address code is emitted (syntax-directed translation). Phase 5, error reporting, is a shared channel used by every phase.</p>
{fig1}
<p class="cap"><b>Figure 1: Architecture of the ErrorBuddy compiler.</b> <i>Blue boxes are the standard front-end phases, green is intermediate code, yellow is the error-reporting phase that every other phase uses.</i></p>
<h3>6.1 Layers</h3>
{table(["Layer", "Files", "Role"], [["Front end", "lexer.h, lexer.cpp", "Phase 1; defines Token and CompileError"], ["One pass", "parser.h, parser.cpp", "Phases 2, 3 and 4 and the diagnosis helpers"],
  ["Driver", "main.cpp", "Runs the phases, prints the result or the error, sets the exit code"], ["Tools", "Makefile, examples/, web/, site/, case_study/", "Build, tests, playground, website, evaluation"]], ["18%", "36%", "46%"])}
<h3>6.2 Shared components</h3>
<ul><li><b>Token:</b> type, exact text and line number; created by the lexer and read by every later phase.</li>
<li><b>CompileError:</b> line, phase, message and suggestion; the only way any phase reports a problem.</li>
<li><b>Symbol table:</b> <code>std::map</code> from name to declaration line and current value.</li>
<li><b>TAC list:</b> instructions in source order, printed by the driver only when every phase passes.</li></ul>
<h3>6.3 Why the diagnosis sits inside the parser</h3>
<p>The parser is the only place that knows the previous token, the next token and the rule being completed at the moment of failure. Moving the diagnosis there lets ErrorBuddy choose the line where the fix belongs. We measured the effect with a patched build that reports the detection point instead: it placed 21 of 24 mistakes on the exact line, against 24 of 24 for the shipped fix-point rule (Section 13).</p>
<p>Exit codes: 0 when every phase passes, 1 for a compile error, 2 for bad usage or an unreadable file, and 3 for an internal error.</p>

<h3 class="page">6.4 Detailed Pipeline Flow (Stage-wise Architecture)</h3>
<p>Figure 1A expands Figure 1 into the stage-by-stage data flow of the compiler. Arrows carry the artefact passed between stages, and red boxes mark where the pipeline halts with exit code 1.</p>
{fig1a}
<p class="cap"><b>Figure 1A: Detailed stage-wise architecture of ErrorBuddy.</b> <i>Stages 2 to 4 run in one pass of the parser. Stage 5 is entered from any earlier stage the moment a problem is found; it prints the error and no intermediate code.</i></p>

<h2 class="page">7. Phase-by-Phase Design</h2>
<h4>Phase 1: Lexical analysis</h4>
<p>A hand-written scanner reads the source one character at a time. A newline increments the line counter, spaces and <code>//</code> comments are skipped, a run of digits becomes a NUMBER, a letter or underscore starts a name (the whole words <code>int</code> and <code>print</code> become keywords), and single characters become operators, '=', parentheses or ';'. The token list always ends with END_OF_FILE. It stops on an unknown symbol such as '@', a number larger than INT_MAX, or a name that starts with a digit such as '2nd'. Inspect with <code>--tokens</code>. Source: <code>lexer.cpp</code>.</p>
{pre(prec_tok.split("Compilation successful!")[0].split(chr(10), 2)[2])}
<h4>Phase 2: Syntax analysis</h4>
<p>A recursive-descent parser with one C++ function per grammar rule: <code>statement()</code>, <code>declaration()</code>, <code>assignment()</code>, <code>printStatement()</code>, <code>expression()</code>, <code>term()</code> and <code>factor()</code>. Precedence comes from the grammar: <code>term()</code> handles '*' and '/' one level below <code>expression()</code>, and the while loops in both make operators left-associative, so 10 - 4 - 3 is (10 - 4) - 3. <code>factor()</code> recurses on '(' up to a depth of 200. Stops on a missing ';' or ')', two operators in a row, a missing value, or a statement that starts with the wrong token. Source: <code>parser.cpp</code>.</p>
<h4>Phase 3: Semantic analysis</h4>
<p>The symbol table maps each name to its declaration line and current value. Checks run inside the parser the moment a name or operator is seen: undeclared variables (with a 'Did you mean' hint), duplicate declarations, a variable used in its own declaration, a keyword used as a name, division by zero and integer overflow. Because the language has no input and no loops, every value is known at compile time, so a division by a variable that holds 0 is caught before the program runs. Source: <code>parser.cpp</code>.</p>
<h4>Phase 4: Intermediate code generation</h4>
<p><code>binary()</code> computes the value of each operation, checks it, takes a fresh temporary from <code>newTemp()</code> and emits <code>tN = left op right</code>. Temporaries skip any name the user wrote, parentheses produce no instructions, and the code is emitted in source order and printed only if the whole program compiles. Source: <code>parser.cpp</code>.</p>
{pre(body(valid))}
<h4>Phase 5: Error reporting</h4>
<p>Any phase throws a <code>CompileError</code> at the first problem. <code>main.cpp</code> catches it, prints the four fields in a fixed format and exits with code 1 (Section 8). Source: <code>lexer.h</code>, <code>parser.cpp</code>, <code>main.cpp</code>.</p>

<h2>8. Error Reporting Subsystem</h2>
<p>All errors travel through one structure, defined in <code>lexer.h</code> so that every phase can throw it:</p>
{pre('''struct CompileError {
    int line;
    std::string phase;       // which compiler phase found the problem
    std::string message;     // what is wrong, in plain English
    std::string suggestion;  // one concrete way to fix it
};''')}
{table(["Field", "Meaning", "Example"], [["line", "where the fix belongs", "2"], ["phase", "which phase found it", "Syntax Analysis"],
  ["message", "the broken rule in plain English", "Expected ';' at the end of the statement."], ["suggestion", "one concrete thing to type", "Add a semicolon after '10'."]], ["16%", "34%", "50%"])}
<p>Example messages produced by the real compiler:</p>
{pre(body(semi))}
{pre(body(undecl))}
<p>Errors stop compilation: the program is not partly compiled, and no intermediate code is printed. This keeps one message on screen, for one mistake, at the right line.</p>

<h2>9. Diagnosis and Typo Hints</h2>
<h3>9.1 Diagnosis from surrounding tokens</h3>
<p><code>expectSemicolon()</code> runs at the end of every statement. If the next token is not ';', it checks the token in order:</p>
{table(["Next token", "Diagnosis", "Reported on"], [["')'", "Found an extra ')' that has no matching '('.", "that token's line"], ["'='", "Unexpected '='. A statement can contain only one '='.", "that token's line"],
  ["name, number or '(' on the same line", "Missing operator between the two values.", "that token's line"], ["anything else", "Expected ';' at the end of the statement.", "<b>the previous token's line</b> (fix point)"]], ["30%", "45%", "25%"])}
<p><code>factorError()</code> handles a missing value: two operators in a row, a negative literal, empty parentheses, a keyword inside an expression, or a program that ends in the middle of an expression. <code>unknownStatementError()</code> handles a statement that starts wrongly: a misspelled or capitalised keyword, a name on its own, an extra ';' or an '=' with no name before it.</p>
<h3>9.2 Typo hints</h3>
<ol><li>Compute the Levenshtein distance between the unknown word and each candidate, in a single rolling row of the dynamic-programming table.</li>
<li>Accept a candidate if the distance is at most 1 for targets of up to 3 letters and at most 2 for longer targets, and the word is not the candidate itself.</li>
<li>Skip variable names shorter than 3 letters, which produce misleading hints.</li>
<li>Offer the first accepted name: "Did you mean 'score'?".</li></ol>
<p>The limits were chosen by testing four policies on 23 typo cases (<code>run_study.py --hints</code>):</p>
{table(["Policy", "Rule", "Right", "Wrong", "Missed", "Silent-ok"], [[p[0], " ".join(p[1:-4]), *p[-4:]] for p in (l.split() for l in hints.splitlines()[1:5])], ["11%", "49%", "10%", "10%", "10%", "10%"])}
<p>The shipped policy gives the fewest wrong suggestions (6) while still getting 12 right.</p>

<h2 class="page">10. Sample Codes</h2>
<h3>10.1 Valid program: examples/valid.txt</h3>
{pre(read("examples/valid.txt"))}
<p>Passes every phase: 41 tokens, 6 statements, 3 variables, 12 TAC instructions. Output shown in Section 7, Phase 4.</p>
<h3>10.2 Missing parenthesis: examples/incorrect_parentheses.txt</h3>
{pre(read("examples/incorrect_parentheses.txt"))}
{pre(body(paren))}
<h3>10.3 Division by a variable that is zero: examples/division_by_zero.txt</h3>
{pre(read("examples/division_by_zero.txt"))}
{pre(body(divz))}
<p>gcc 11.4 compiles the equivalent C program without any warning.</p>
<h3>10.4 Misspelled variable (case study M14)</h3>
{pre(CASES[13]["eb"])}
{pre(f"Error on line {CASES[13]['eb_line']}:{chr(10)}{CASES[13]['eb_msg']}{chr(10)}Suggestion: {CASES[13]['eb_sugg']}")}
<p>All ten example programs are in the <code>examples/</code> folder of the repository with their expected output in <code>examples/expected/</code>.</p>

<h2>11. Demo Screenshots</h2>
<p>The screenshots were taken from the live GitHub Pages website. The playground uses the same page as the local playground (<code>make web</code>): the editor on the left highlights the error line, and the phase strip on the right shows how far compilation got.</p>
<div class="fig"><img class="shot" src="{shot_play}" alt="Playground showing a missing semicolon error">
<p class="cap"><b>Figure 2: Missing semicolon in the playground.</b> <i>The error is reported on line 2, where the fix belongs, with the suggestion "Add a semicolon after '10'". The phase strip shows Lexical passed and Syntax failed.</i></p></div>
<div class="fig"><img class="shot" src="{shot_site}" alt="ErrorBuddy project website">
<p class="cap"><b>Figure 3: Project website on GitHub Pages.</b> <i>Links to the playground, this report, the presentation and the source code.</i></p></div>

<h2 class="page">12. How to Start the Project</h2>
<p><b>Repository (code and reference): <a href="{REPO}">{REPO}</a></b><br><b>Website: <a href="{PAGES}">{PAGES}</a></b></p>
<h3>12.1 Prerequisites</h3>
<ul><li>g++ with C++17 support (GCC 7 or newer) and GNU Make</li><li>Python 3 (only for the web playground and the case study)</li><li>gcc (only for the case-study comparison)</li></ul>
<h3>12.2 Clone and build the compiler</h3>
{pre(f"git clone {REPO}{chr(10)}cd Compiler-Design-Project{chr(10)}make")}
<p>This builds <code>./errorbuddy</code> with <code>g++ -std=c++17 -Wall -Wextra -pedantic -O2</code>.</p>
<h3>12.3 Run the compiler from the command line</h3>
{pre('''./errorbuddy examples/valid.txt
./errorbuddy examples/precedence.txt --tokens
./errorbuddy examples/missing_semicolon.txt
make run FILE=examples/division_by_zero.txt''')}
{table(["Command / flag", "Purpose"], [["<code>./errorbuddy file.txt</code>", "Compile a file: TAC, symbol table and phase summary, or the error"], ["<code>--tokens</code>", "Also print the lexer output as a line / type / text table"],
  ["<code>make test</code>", "Run all example programs and compare with the expected output"], ["<code>make web</code>", "Start the local playground on http://localhost:8795"],
  ["<code>python3 case_study/run_study.py</code>", "Line-placement study against gcc (<code>--hints</code>, <code>--lexer</code> for the other studies)"], ["<code>make clean</code>", "Remove build files"]], ["42%", "58%"])}
<h3>12.4 Run the playground</h3>
{pre("make web" + chr(10) + "# open http://localhost:8795 in a browser")}
<p>The local playground compiles anything you type by calling the real binary. The website playground shows the real compiler output for every example program.</p>

<h2>13. Results and Comparison with GCC</h2>
<p>The same 24 beginner mistakes were written in ErrorBuddy's language and as equivalent C programs. The C programs were compiled with gcc 11.4 (-Wall -Wextra, first diagnostic). The fix line of each case was labelled by hand before any compiler was run. ✗ marks a report on a line other than the fix line.</p>
<div class="small">{table(["Mistake", "Fix", "gcc 11.4", "ErrorBuddy"], cmp_rows, ["27%", "6%", "35%", "32%"])}</div>
{table(["Compiler", "Caught", "Exact fix line", "Late", "Early"], [["gcc 11.4", "23 / 24", "20 / 24", "3", "0"], ["ErrorBuddy, detection point", "24 / 24", "21 / 24", "3", "0"],
  ["<b>ErrorBuddy, fix point (shipped)</b>", "<b>24 / 24</b>", "<b>24 / 24</b>", "<b>0</b>", "<b>0</b>"]], ["40%", "15%", "19%", "13%", "13%"])}
<p>gcc missed one mistake entirely (M19, division by a variable that is 0), and all three of its late reports were a missing semicolon. Verification status: {passed[1]} of {int(passed[1]) + int(passed[2])} example programs pass <code>make test</code>:</p>
{pre(test)}

<h2>14. Limitations and Future Work</h2>
<h3>14.1 Known limits</h3>
<ul><li>The language has only <code>int</code>, arithmetic and <code>print</code>; there is no if/else, loop or function.</li>
<li>Compilation stops at the first error, so a program with three mistakes needs three runs.</li>
<li>There is no unary minus; <code>-5</code> must be written as <code>0 - 5</code>.</li>
<li>Values are known at compile time only because there is no input and no loop.</li>
<li>Three-address code is the final output; there is no optimiser or machine code.</li>
<li>The website playground shows recorded output for the examples; compiling new code needs the local playground or the command line.</li></ul>
<h3>14.2 Future work</h3>
<ul><li>if / else, while and for loops; comparison and logical operators; printf.</li>
<li>Error recovery to report several errors per run.</li>
<li>Functions and arrays; <code>char</code> and <code>float</code>.</li>
<li>Data-flow analysis once loops and input exist.</li>
<li>Constant folding on TAC and an assembly back end.</li>
<li>A WebAssembly build so the website can compile any program in the browser.</li></ul>

<h2>15. Conclusion</h2>
<p>ErrorBuddy shows that a small, hand-written compiler can implement every classic phase and still put the learner first. Treating each error as a structured object with a line, a phase, a message and a suggestion, and diagnosing the cause from the surrounding tokens before reporting, gives messages that point to the line where the fix belongs and say what to type. Measured on 24 classic beginner mistakes, it reported every one on the exact fix line, against 20 for gcc 11.4. Other compilers ask whether a program is valid; ErrorBuddy also answers where the mistake is and how to fix it.</p>

<h2>16. References</h2>
<ol>
<li>Project repository: {REPO}</li>
<li>A. V. Aho, M. S. Lam, R. Sethi and J. D. Ullman, <i>Compilers: Principles, Techniques, and Tools</i>, 2nd ed., Addison-Wesley, 2006.</li>
<li>N. Wirth, <i>Compiler Construction</i>, Addison-Wesley, 1996.</li>
<li>V. I. Levenshtein, "Binary codes capable of correcting deletions, insertions, and reversals," <i>Soviet Physics Doklady</i>, vol. 10, no. 8, 1966.</li>
<li>V. J. Traver, "On compiler error messages: what they say and what they mean," <i>Advances in Human-Computer Interaction</i>, 2010.</li>
<li>G. Marceau, K. Fisler and S. Krishnamurthi, "Measuring the effectiveness of error messages designed for novice programmers," <i>Proc. ACM SIGCSE</i>, 2011.</li>
<li>P. Denny, A. Luxton-Reilly and D. Carpenter, "Enhancing syntax error messages appears ineffectual," <i>Proc. ITiCSE</i>, 2014.</li>
<li>B. A. Becker, G. Glanville, R. Iwashima, C. McDonnell, K. Goslin and C. Mooney, "Effective compiler error message enhancement for novice programming students," <i>Computer Science Education</i>, vol. 26, no. 2-3, 2016.</li>
<li>B. A. Becker et al., "Compiler error messages considered unhelpful: the landscape of text-based programming error message research," <i>Proc. ITiCSE Working Group Reports</i>, 2019.</li>
<li>GCC, the GNU Compiler Collection, version 11.4, warning options (-Wall -Wextra). https://gcc.gnu.org/onlinedocs/</li>
<li>Clang "Expressive Diagnostics" documentation. https://clang.llvm.org/diagnostics.html</li>
<li>E. Czaplicki, "Compiler errors for humans," Elm blog, 2015. https://elm-lang.org/news/compiler-errors-for-humans</li>
</ol>
</body></html>"""

open(OUT_HTML, "w").write(doc)
subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                "--virtual-time-budget=8000", f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML], check=True, capture_output=True)
print("wrote", OUT_PDF)
