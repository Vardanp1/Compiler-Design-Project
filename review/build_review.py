#!/usr/bin/env python3
# build_review.py - builds ErrorBuddy_Review.pdf, the review deck (16:9, PDF).
#
#   python3 review/build_review.py
#
# Program outputs come from ./errorbuddy and the gcc comparison from
# case_study/run_study.py (cached in review/cases.json by make_cases()).
import html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "review")
OUT_HTML = os.path.join(HERE, "review.html")
OUT_PDF = os.path.join(ROOT, "ErrorBuddy_Review.pdf")
TEAM = [("Vardan Pandya", "24BCE2608"), ("Kunal Sharma", "24BCE2641")]
REPO = "github.com/Vardanp1/Compiler-Design-Project"
PAGES = "vardanp1.github.io/Compiler-Design-Project"
NAV = ["PROBLEM", "IDEA", "ARCHITECTURE", "PHASES", "ERRORS", "PROOF"]
esc = html.escape


def make_cases():
    sys.path.insert(0, os.path.join(ROOT, "case_study"))
    import run_study as R
    from corpus import CASES
    exe = os.path.join(ROOT, "errorbuddy")
    out = []
    for c in CASES:
        g, e = R.run_gcc(c["c"]), R.run_eb(exe, c["eb"])
        out.append(dict(id=c["id"], name=c["name"], fix=c["fix"], eb=c["eb"], c=c["c"],
                        eb_line=e["line"], eb_msg=e["msg"], eb_sugg=e["sugg"], eb_phase=e["phase"],
                        gcc_line=g["line"], gcc_kind=g["kind"], gcc_msg=g["msg"]))
    json.dump(out, open(os.path.join(HERE, "cases.json"), "w"), indent=1)
    return out


subprocess.run(["make", "-s"], cwd=ROOT, check=True)
CASES = {c["id"]: c for c in make_cases()}
q = lambda s: s.replace("‘", "'").replace("’", "'")


def run(path):
    r = subprocess.run(["./errorbuddy", path], cwd=ROOT, capture_output=True, text=True)
    return r.stdout, r.returncode


def code(src, numbers=True, cls=""):
    rows = src.rstrip("\n").split("\n")
    if not numbers:
        return f'<pre class="code {cls}">{esc(src.rstrip())}</pre>'
    g = "".join(f"<i>{i + 1}</i>" for i in range(len(rows)))
    return f'<div class="code {cls}"><div class="gut">{g}</div><pre>{esc(chr(10).join(rows))}</pre></div>'


def tag(t, dark=True):
    return f'<span class="tag{"" if dark else " light"}">{esc(t)}</span>'


TOTAL = 23
slides = []


def slide(nav, body, dark=False):
    n = len(slides) + 1
    head = "" if dark else (
        '<div class="top"><div class="brand"><b>EB;</b><span>ERRORBUDDY</span></div><div class="nav">' +
        "".join(f'<span class="{"on" if x == nav else ""}">{x}</span>' for x in NAV) +
        '</div><div class="ready">● TESTS: 10/10 PASS</div></div>')
    foot = "" if dark else (f'<div class="foot"><span>SLIDE {n:02d} / {TOTAL}</span>'
                            f'<span>ERRORBUDDY · 5-PHASE COMPILER + FRIENDLY ERRORS</span></div>')
    slides.append(f'<section class="slide{" dark" if dark else ""}">{head}<div class="body">{body}</div>{foot}</section>')


def heading(eyebrow, title, sub=""):
    return (f'<div class="eyebrow">{esc(eyebrow)}</div><h1>{title}</h1>' +
            (f'<p class="sub">{sub}</p>' if sub else ""))


# ---------------------------------------------------------------- 1 title
slide(None, f"""
<div class="title-grid">
  <div>
    <div class="eyebrow dim">COMPILER DESIGN PROJECT</div>
    <div class="mark">Error<br>Buddy<span>;</span></div>
    <div class="bar"></div>
    <h2 class="big">The Compiler That Explains<br>Its Own Errors</h2>
    <p class="dimtext">A beginner compiler in C++17 that reports every mistake on the line where<br>the fix belongs, in plain words, with one concrete fix.</p>
    <div class="chips">{tag("5 PHASES · 3 SOURCE FILES", False)}{tag("C++17", False)}{tag("24 / 24 ON THE FIX LINE", False)}</div>
  </div>
  <div>
    <div class="panel-dark"><div class="lbl">PROGRAM</div>
{code(CASES["M01"]["eb"], numbers=False, cls="bare")}
      <div class="alert"><div class="alert-h"><b>✕ ERROR</b><span>LINE 2 · SYNTAX</span></div>
        <div>Expected ';' at the end of the statement.<br>Suggestion: Add a semicolon after '10'.</div></div>
    </div>
    <div class="team"><div class="lbl">TEAM</div>
      {"<hr>".join(f'<div class="who">{n}</div><div class="reg">{r}</div>' for n, r in TEAM)}
    </div>
  </div>
</div>""", dark=True)

# ---------------------------------------------------------------- 2 problem statement
slide("PROBLEM", f"""
<div class="eyebrow dim">PROBLEM STATEMENT</div>
<h1 class="huge">Compilers tell beginners that something is wrong.<br><span class="ul">Not where to fix it, or how.</span></h1>
<div class="quote">A student forgets one semicolon. The compiler points at the next line, says <i>"expected ',' or ';' before 'printf'"</i>
and stops. The message is accurate for someone who knows the grammar. For a beginner it names the wrong line, uses parser vocabulary
and never says what to type. Some real mistakes, like dividing by a variable that is zero, get no message at all.</div>
<div class="checks">{''.join(f'<div>✕ &nbsp;{t}</div>' for t in ["Wrong line", "Grammar words", "No fix suggested", "Some mistakes not reported"])}</div>
<div class="rq"><div class="lbl">RESEARCH QUESTION</div>How can a compiler report each beginner mistake on the line where the fix belongs, in plain words, with one concrete fix?</div>
""", dark=True)

# ---------------------------------------------------------------- 3 the problem
c2, c8, c19 = CASES["M02"], CASES["M08"], CASES["M19"]
slide("PROBLEM", heading("THE PROBLEM", "Real mistakes. Unhelpful messages.",
                         "Three beginner programs (C equivalents), compiled with gcc 11.4 -Wall -Wextra. The first diagnostic is shown.") + f"""
<div class="cards3">
  <div class="card topline"><h3>A missing semicolon</h3>{code(c2["c"])}
    <p class="note">gcc: line {c2["gcc_line"]}: {esc(q(c2["gcc_msg"]))}</p>{tag(f"WRONG LINE · FIX IS ON {c2['fix']}")}</div>
  <div class="card topline"><h3>Two operators in a row</h3>{code(c8["c"])}
    <p class="note">gcc: {esc(q(c8["gcc_msg"]))}</p>{tag("GRAMMAR WORDS, NO FIX")}</div>
  <div class="card topline"><h3>Dividing by a variable that is 0</h3>{code(c19["c"])}
    <p class="note">gcc: no error and no warning. The program crashes or misbehaves when it runs.</p>{tag("NOT REPORTED")}</div>
</div>
<div class="banner"><b>20 of 24 on the right line. 1 not reported at all.</b><span>We ran 24 classic beginner mistakes through gcc 11.4 and ErrorBuddy (slide 17).</span></div>""")

# ---------------------------------------------------------------- 4 what compilers report
slide("PROBLEM", heading("THE PROBLEM", "Where does a compiler report a mistake?",
                         "Every phase checks one thing. The report goes where the parser noticed the problem, not where the student must edit.") + """
<div class="steps">
  <div><b>1</b>Lexical<small>are the words valid?</small></div><div><b>2</b>Syntax<small>does the grammar fit?</small></div>
  <div><b>3</b>Semantic<small>do the names exist?</small></div><div><b>4</b>Code<small>generate output</small></div>
  <div class="q"><b>5</b>Explain?<small>where is the fix, and what is it?</small></div>
</div>
<div class="cols2">
  <div class="card"><div class="lbl">THE DETECTION POINT</div><p>A parser only knows a <code>;</code> is missing when it reads the <b>next</b> token. If that token is on line 3,
  line 3 is reported, although the fix belongs at the end of line 2. When the next statement is after blank lines or comments, the report moves even further away
  (gcc reported line 5 for a fix on line 2).</p>
  <pre class="mini">2  int b = 10        &lt;- fix belongs here
3
4  // show the total
5  printf(...)       &lt;- gcc reports here</pre></div>
  <div class="card"><div class="lbl">THE ANALOGY</div><p>A teacher marking an essay circles the word that is misspelled and writes the right spelling in the margin.
  A compiler that reports the next line and says "expected ... before" is like a teacher circling the next word on the page and writing "unexpected word".</p>
  <p>Beginners need the <b>first</b> kind of feedback: the place, the rule and the fix.</p></div>
</div>""")

# ---------------------------------------------------------------- 5 introducing
slide("IDEA", heading("THE IDEA", "Introducing ErrorBuddy", "A small compiler whose main output, when something is wrong, is a lesson.") + """
<div class="cols2 w">
  <div class="blackbox"><div class="lbl">THE THESIS</div><div class="thesis">A compiler should not just <u>detect</u> a mistake.
  It should <u>explain</u> it: the line, the rule and the fix.</div>
  <p>Every error is a structured object with four fields, built by the phase that found it, and printed in one fixed format.</p>
  <div class="chips">""" + tag("LINE", False) + tag("PHASE", False) + tag("MESSAGE", False) + tag("SUGGESTION", False) + """</div></div>
  <div class="numbered">
    <div><b>1</b><div><h4>Report on the fix line</h4><p>A missing ';' is reported on the line of the token before it.</p></div></div>
    <div><b>2</b><div><h4>Name the rule in plain English</h4><p>"Two operators in a row: '+' followed by '*'."</p></div></div>
    <div><b>3</b><div><h4>Give one concrete fix</h4><p>"Add a semicolon after '10'." Not a grammar lesson.</p></div></div>
    <div><b>4</b><div><h4>Say which phase found it</h4><p>Lexical, Syntax or Semantic Analysis.</p></div></div>
    <div><b>5</b><div><h4>Stop before generating code</h4><p>No partial three-address code is printed for a broken program.</p></div></div>
  </div>
</div>""")

# ---------------------------------------------------------------- 6 unique
slide("IDEA", heading("THE IDEA", "What makes it different", "Ordinary compilers stop at detection. ErrorBuddy adds a diagnosis step before every error.") + """
<div class="grid2x2">
  <div class="tile"><span>01</span><div><h4>Four-field errors</h4><p>CompileError { line, phase, message, suggestion } is the only way any phase reports a problem.</p></div></div>
  <div class="tile"><span>02</span><div><h4>Diagnosis from nearby tokens</h4><p>Before reporting, the parser looks at the previous and next token to name the likely cause: extra ')', missing operator, extra '='.</p></div></div>
  <div class="tile"><span>03</span><div><h4>Measured typo hints</h4><p>"Did you mean 'score'?" uses Levenshtein distance with a limit chosen by testing four policies on 23 typo cases.</p></div></div>
  <div class="tile"><span>04</span><div><h4>Compile-time values</h4><p>The symbol table tracks each variable's value, so division by a variable that is 0 is caught before the program runs.</p></div></div>
</div>""")

# ---------------------------------------------------------------- 7 language
slide("IDEA", heading("THE IDEA", "The language at a glance", "A small C-like language, kept small on purpose so that every phase is complete.") + f"""
<div class="cols2 lang">
  <div><div class="lbl">EXAMPLE PROGRAM · examples/valid.txt</div>{code(open(os.path.join(ROOT, "examples/valid.txt")).read())}
    <div class="blackstrip"><span>OUTPUT</span><b>12</b> TAC instructions · <b>3</b> variables · exit 0</div></div>
  <table class="kv">
    <tr><td>TYPES</td><td><code>int</code> only; every variable needs a starting value</td></tr>
    <tr><td>STATEMENTS</td><td><code>int x = e;</code> &nbsp; <code>x = e;</code> &nbsp; <code>print e;</code></td></tr>
    <tr><td>OPERATORS</td><td><code>+ - * /</code> with precedence, and <code>( )</code></td></tr>
    <tr><td>COMMENTS</td><td><code>// to the end of the line</code></td></tr>
    <tr><td>RULES</td><td>every statement ends with <code>;</code> · integer division</td></tr>
    <tr><td>NOT INCLUDED</td><td>unary minus, if/else, loops, functions, input</td></tr>
    <tr><td>ON ERROR</td><td>stops at the first error; no TAC is printed</td></tr>
  </table>
</div>""")

# ---------------------------------------------------------------- 8 architecture
slide("ARCHITECTURE", heading("ARCHITECTURE", "The architecture: five phases",
                              "Three C++ files. Phases 2 to 4 run together in one pass of the parser (syntax-directed translation).") + """
<div class="arch">
  <div class="ph"><b>1</b><h4>Lexical analysis</h4><code>lexer.cpp</code><p>characters → tokens with line numbers</p><div class="io">OUT · vector&lt;Token&gt;</div></div>
  <div class="arrow">→</div>
  <div class="ph group"><div class="glbl">parser.cpp · ONE PASS</div>
    <div class="row3"><div><b>2</b><h4>Syntax</h4><p>recursive descent</p></div><div><b>3</b><h4>Semantic</h4><p>symbol table checks</p></div><div><b>4</b><h4>TAC</h4><p>t1 = a op b</p></div></div></div>
  <div class="arrow">→</div>
  <div class="ph"><b>D</b><h4>Driver</h4><code>main.cpp</code><p>prints TAC, symbol table and phase summary</p><div class="io">EXIT 0</div></div>
</div>
<div class="errbar"><b>5</b><div><h4>Error reporting · CompileError { line, phase, message, suggestion }</h4>
<p>Defined in lexer.h. Any phase throws it at the first problem; main.cpp catches it, prints it and exits with code 1. No TAC is shown.</p></div></div>
<div class="legend"><span>■ phase</span><span>□ shared error channel</span><span>exit codes: 0 ok · 1 compile error · 2 usage · 3 internal</span></div>""")

# ---------------------------------------------------------------- 9 phases 1-3
def phase_card(n, name, file, items, inp, out):
    li = "".join(f"<li>{x}</li>" for x in items)
    return (f'<div class="card topline pc"><div class="pn"><b>{n}</b><h3>{name}</h3></div><code class="file">{file}</code>'
            f'<ul>{li}</ul><div class="iorow"><span>IN</span>{inp}</div><div class="iorow"><span>OUT</span>{out}</div></div>')


slide("PHASES", heading("PHASES", "Phases 1 to 3 in detail", "From raw text to checked statements.") + '<div class="cards3">' +
      phase_card(1, "Lexical analysis", "lexer.cpp · tokenize()",
                 ["One loop over the characters", "Counts newlines, so every token has a line", "Skips spaces and // comments",
                  "<code>int</code>, <code>print</code> only as whole words", "Rejects <code>@</code>, <code>2nd</code>, numbers above INT_MAX"],
                 "source string", "tokens ending in END_OF_FILE") +
      phase_card(2, "Syntax analysis", "parser.cpp · statement() …",
                 ["Recursive descent: one function per rule", "<code>expression → term → factor</code> gives precedence",
                  "While loops give left associativity", "Nesting limit of 200 for <code>(</code>", "Diagnoses a missing ';' before reporting"],
                 "tokens", "recognised statements") +
      phase_card(3, "Semantic analysis", "parser.cpp · symbolTable",
                 ["<code>map&lt;name, {line, value}&gt;</code>", "Undeclared names, with 'Did you mean'", "Duplicate declarations",
                  "Use inside its own declaration", "Division by zero and int overflow"],
                 "each name and operator", "checked operands") + "</div>")

# ---------------------------------------------------------------- 10 phases 4-5
slide("PHASES", heading("PHASES", "Phases 4 and 5 in detail", "Generating code when the program is right, explaining it when it is not.") + f"""
<div class="cols2">
  {phase_card(4, "Three-address code", "parser.cpp · binary(), newTemp()",
              ["At most one operator per instruction", "Temporaries t1, t2… skip names the user wrote", "Parentheses add grouping, not instructions",
               "Emitted as each statement is parsed", "Printed only if every phase passes"], "operands and operators", "TAC list in source order")}
  {phase_card(5, "Error reporting", "lexer.h · CompileError",
              ["Thrown by any phase at the first problem", "<code>expectSemicolon()</code>, <code>factorError()</code>, <code>unknownStatementError()</code> diagnose the cause",
               "Edit-distance typo hints", "Reported on the line where the fix belongs", "main.cpp prints it and exits with 1"], "the failing token and its neighbours", "line · phase · message · suggestion")}
</div>""")

# ---------------------------------------------------------------- 11 structure
slide("ARCHITECTURE", heading("ARCHITECTURE", "Structure: files and shared parts", "Every file has one job. Four data structures are shared between phases.") + """
<div class="cols2 w">
  <table class="layers">
    <tr><th>LAYER</th><th>FILE</th><th>JOB</th></tr>
    <tr><td>Front end</td><td><code>lexer.h / lexer.cpp</code></td><td>Phase 1 and the shared CompileError</td></tr>
    <tr><td>One pass</td><td><code>parser.h / parser.cpp</code></td><td>Phases 2–4 and the diagnosis helpers</td></tr>
    <tr><td>Driver</td><td><code>main.cpp</code></td><td>Run phases, print result or error, exit code</td></tr>
    <tr><td>Build &amp; test</td><td><code>Makefile</code>, <code>examples/</code></td><td>make, make test (10 programs)</td></tr>
    <tr><td>Front ends</td><td><code>web/</code>, <code>site/</code></td><td>Local playground, GitHub Pages site</td></tr>
    <tr><td>Evaluation</td><td><code>case_study/</code></td><td>24 mistakes vs gcc, hint and lexer studies</td></tr>
  </table>
  <div class="shared"><div class="lbl">SHARED COMPONENTS</div>
    <div><h4>Token</h4><p>type, exact text and line number; made by the lexer, read by every later phase.</p></div>
    <div><h4>CompileError</h4><p>line, phase, message, suggestion; the single error channel.</p></div>
    <div><h4>Symbol table</h4><p>name → declaration line and current value.</p></div>
    <div><h4>TAC list</h4><p>instructions in source order, printed by main.cpp.</p></div>
  </div>
</div>""")

# ---------------------------------------------------------------- 12 compileerror
semi_out, _ = run("examples/missing_semicolon.txt")
STRUCT = code("struct CompileError {\n    int line;\n    std::string phase;\n    std::string message;\n    std::string suggestion;\n};", numbers=False)
HINTEX = code("scroe -> score   2 edits\nprnt  -> print   1 edit\nmx    -> max     1 edit", numbers=False)
slide("ERRORS", heading("ERRORS", "What is a CompileError?", "Four fields, filled by the phase that found the problem, printed in one fixed format.") + f"""
<div class="cols2 w">
  <div>{STRUCT}
    <div class="lbl" style="margin-top:18px">ACTUAL OUTPUT · examples/missing_semicolon.txt</div>
    <pre class="term">{esc(semi_out.split(chr(10), 2)[2].strip())}</pre></div>
  <div class="fields">
    <div><span>LINE</span><b>2</b><p>where the fix belongs, not where parsing stopped</p></div>
    <div><span>PHASE</span><b>Syntax Analysis</b><p>which phase found it: Lexical, Syntax or Semantic</p></div>
    <div><span>MESSAGE</span><b>Expected ';' at the end of the statement.</b><p>the rule that was broken, in plain English</p></div>
    <div><span>SUGGESTION</span><b>Add a semicolon after '10'.</b><p>one concrete thing to type</p></div>
  </div>
</div>""")

# ---------------------------------------------------------------- 13 diagnosis
slide("ERRORS", heading("ERRORS", "How diagnosis works, and why it runs before the report",
                        "expectSemicolon() runs at the end of every statement. If the next token is not ';', it asks what it is instead.") + """
<div class="flow">
  <div><b>1</b><h4>Statement parsed</h4><p>the next token should be ';'</p></div>
  <div><b>2</b><h4>Look at it</h4><p>what is the token instead?</p></div>
  <div><b>3</b><h4>Match a cause</h4><p>check the rules below, in order</p></div>
  <div><b>4</b><h4>Pick the line</h4><p>where the fix belongs</p></div>
  <div><b>5</b><h4>Throw</h4><p>CompileError with a fix</p></div>
</div>
<table class="rules">
  <tr><th>NEXT TOKEN</th><th>DIAGNOSIS</th><th>REPORTED ON</th></tr>
  <tr><td><code>)</code></td><td>Found an extra ')' that has no matching '('.</td><td>that token's line</td></tr>
  <tr><td><code>=</code></td><td>Unexpected '='. A statement can contain only one '='.</td><td>that token's line</td></tr>
  <tr><td>name, number or <code>(</code> on the same line</td><td>Missing operator between the two values.</td><td>that token's line</td></tr>
  <tr><td>anything else</td><td>Expected ';' at the end of the statement. Add a semicolon after the last token.</td><td><b>the previous token's line</b></td></tr>
</table>
<div class="banner sm"><b>The last rule is the fix-point rule.</b><span>It moved ErrorBuddy from 21 to 24 of 24 mistakes on the exact line (slide 18).</span></div>""")

# ---------------------------------------------------------------- 14 five kinds
groups = [("1", "LEXICAL", "Invalid characters and names", ["M23", "M24"], "Lexical"),
          ("2", "STRUCTURE", "Missing ; and parentheses", ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M12"], "Syntax"),
          ("3", "EXPRESSIONS", "Operators and missing values", ["M08", "M09", "M10", "M11"], "Syntax"),
          ("4", "NAMES", "Undeclared, misspelled, duplicate", ["M13", "M14", "M15", "M16", "M17"], "Syntax / Semantic"),
          ("5", "VALUES", "Division by zero and overflow", ["M18", "M19", "M20", "M21", "M22"], "Lexical / Semantic")]
rows = "".join(f'<div class="kind"><b>{n}</b><div class="kh"><h4>{k}</h4><p>{d}</p></div><div class="ids">' +
               "".join(f"<span>{i} {esc(CASES[i]['name'][:28])}</span>" for i in ids) + f'</div><em>{ph}</em></div>'
               for n, k, d, ids, ph in groups)
slide("ERRORS", heading("ERRORS", "Five kinds of beginner mistake", "The 24 mistakes in the case-study corpus, grouped by what went wrong.") +
      f'<div class="kinds">{rows}</div>')

# ---------------------------------------------------------------- 15 typo hints
hints = open(os.path.join(ROOT, "case_study/out_hints.txt")).read().split("\n\n")[0]
pol = [l.split() for l in hints.splitlines()[1:5]]
slide("ERRORS", heading("ERRORS", "Typo hints: how close is close enough?",
                        "Levenshtein distance in a single rolling row. Four limits tested on 23 typo cases from case_study/corpus.py.") + f"""
<div class="cols2 w">
  <table class="rules"><tr><th>POLICY</th><th>RULE</th><th>RIGHT</th><th>WRONG</th><th>MISSED</th></tr>
  {''.join(f'<tr class="{"hl" if p[0] == "shipped" else ""}"><td>{p[0]}</td><td>{" ".join(p[1:-4])}</td><td>{p[-4]}</td><td>{p[-3]}</td><td>{p[-2]}</td></tr>' for p in pol)}
  </table>
  <div><div class="lbl">EXAMPLES</div>{HINTEX}
    <div class="blackbox sm"><div class="lbl">SHIPPED RULE</div>1 edit for names of up to 3 letters, 2 for longer names, never the word itself,
    and no hints for variables shorter than 3 letters. <b>Fewest wrong hints (6) with 12 right.</b></div></div>
</div>""")

# ---------------------------------------------------------------- 16 semantic + tac
valid_out, _ = run("examples/valid.txt")
tac = re.search(r"\(Three-Address Code\):\n((?:    .*\n)*)", valid_out)[1]
slide("PHASES", heading("PHASES", "Meaning and code: the symbol table and TAC",
                        "No input and no loops means every value is known at compile time, so values are tracked as well as names.") + f"""
<div class="cards3 t">
  <div class="card"><div class="lbl">SYMBOL TABLE AFTER valid.txt</div>
    <table class="rules"><tr><th>NAME</th><th>DECLARED</th><th>VALUE</th></tr><tr><td>age</td><td>line 2</td><td>20</td></tr><tr><td>score</td><td>line 3</td><td>50</td></tr><tr><td>bonus</td><td>line 5</td><td>9</td></tr></table>
    <p class="note">A name is added only after its starting value is parsed, so <code>int a = a + 1;</code> is caught.</p></div>
  <div class="card"><div class="lbl">THREE-ADDRESS CODE (12)</div><pre class="term small">{esc(tac.rstrip())}</pre></div>
  <div class="card"><div class="lbl">CAUGHT BEFORE RUNNING</div>{code(open(os.path.join(ROOT, "examples/division_by_zero.txt")).read())}
    <p class="note"><b>Error on line 3:</b> Division by zero. Variable 'zero' is 0 at this point, so dividing by it is impossible.</p>{tag("GCC: NOT REPORTED")}</div>
</div>""")

# ---------------------------------------------------------------- 17 vs gcc
pick = ["M01", "M02", "M07", "M08", "M10", "M14", "M15", "M19"]
trs = "".join(f'<tr><td><b>{c["id"]}</b> {esc(c["name"])}</td><td>{"line " + str(c["gcc_line"]) + ": " + esc(q(c["gcc_msg"])) if c["gcc_line"] else "<i>nothing reported</i>"}</td>'
              f'<td>line {c["eb_line"]}: {esc(c["eb_msg"])}</td></tr>' for c in (CASES[i] for i in pick))
slide("PROOF", heading("PROOF", "Measured against GCC", "Same mistakes written as C and compiled with gcc 11.4 -Wall -Wextra (first diagnostic). ErrorBuddy output is from the real compiler.") +
      f'<table class="vs"><tr><th>MISTAKE (FIX LINE IN CORPUS)</th><th>GCC 11.4</th><th>ERRORBUDDY</th></tr>{trs}</table>'
      '<p class="note">All 24 cases with both outputs are in the appendix and in case_study/out_placement.txt.</p>')

# ---------------------------------------------------------------- 18 results
bars = [("gcc 11.4", 20), ("ErrorBuddy, detection point", 21), ("ErrorBuddy, fix point (shipped)", 24)]
slide("PROOF", heading("PROOF", "Reported on the exact fix line", "case_study/run_study.py: 24 mistakes, fix line labelled by hand before any compiler was run.") + f"""
<div class="cols2 w">
  <div class="bars">{''.join(f'<div class="brow"><span>{n}</span><div class="track"><div class="fill{" on" if v == 24 else ""}" style="width:{v / 24 * 100:.1f}%">{v} / 24</div></div></div>' for n, v in bars)}
    <p class="note">Detection point = the line of the token where the parser noticed the problem. Fix point = the shipped rule.</p></div>
  <div class="stats">
    <div><b>24/24</b><p>mistakes caught by ErrorBuddy · gcc: 23</p></div>
    <div><b>0</b><p>reports later than the fix line · gcc: 3</p></div>
    <div><b>3</b><p>late gcc reports, all a missing ';'</p></div>
  </div>
</div>""")

# ---------------------------------------------------------------- 19 end to end
prec = open(os.path.join(ROOT, "examples/precedence.txt")).read()
slide("PROOF", heading("PROOF", "One program, end to end", "examples/precedence.txt through every phase. b * 2 is computed before + because of the grammar.") + f"""
<div class="pipe4">
  <div class="card"><div class="lbl">1 · SOURCE</div>{code(prec)}</div>
  <div class="card"><div class="lbl">2 · TOKENS (22 + EOF)</div><pre class="term small">int c = a + b * 2 ;
KEYWORD IDENTIFIER ASSIGN
IDENTIFIER OPERATOR IDENTIFIER
OPERATOR NUMBER SEMICOLON</pre></div>
  <div class="card"><div class="lbl">3 · PARSE + CHECK</div><pre class="term small">expression()
  term() -> a
  +
  term() -> b * 2
     binary() t1 = b * 2
  binary()  t2 = a + t1</pre></div>
  <div class="card"><div class="lbl">4 · TAC</div><pre class="term small">a = 5
b = 10
t1 = b * 2
t2 = a + t1
c = t2
print c</pre></div>
</div>
<div class="banner sm"><b>[OK] Lexical · [OK] Syntax · [OK] Semantic · [OK] Intermediate Code</b><span>Compilation successful · 6 instructions · exit 0</span></div>""")

# ---------------------------------------------------------------- 20 website
slide("PROOF", heading("PROOF", "The website and playground", "Published on GitHub Pages with the documentation, this presentation and the final report.") + f"""
<div class="cols2 shot">
  <img src="../report/playground_screenshot.png" alt="ErrorBuddy playground on GitHub Pages">
  <div class="side">
    <div><h4>Live site</h4><p><code>{PAGES}</code></p></div>
    <div><h4>Playground</h4><p>Every example shows the compiler's real output: error line highlighted, phase strip, TAC, symbol table and tokens.</p></div>
    <div><h4>Local playground</h4><p><code>make web</code> runs <code>web/server.py</code>, which calls the real binary on anything you type.</p></div>
    <div><h4>Source</h4><p><code>{REPO}</code></p></div>
  </div>
</div>""")

# ---------------------------------------------------------------- 21 testing
test = subprocess.run(["make", "-s", "test"], cwd=ROOT, capture_output=True, text=True).stdout
slide("PROOF", heading("PROOF", "Testing: make test", "Every example program has its expected output stored next to it. make test compares them byte for byte.") + f"""
<div class="cols2 w"><pre class="term">{esc(test.strip())}</pre>
  <div class="stats one"><div><b>10/10</b><p>example programs match their expected output</p></div>
  <div class="card"><div class="lbl">COVERS</div><p>a valid program, precedence, missing ';', undeclared and duplicate variables, two operators in a row,
  missing and extra ')', division by a variable that is 0, an empty file.</p><p class="note">Built with g++ -std=c++17 -Wall -Wextra -pedantic -O2, no warnings.</p></div></div>
</div>""")

# ---------------------------------------------------------------- 22 limits
slide("PROOF", heading("PROOF", "Honest limits, and what comes next", "What ErrorBuddy does not do yet, from the original proposal.") + """
<div class="cols2 w">
  <div class="card"><div class="lbl">KNOWN LIMITS</div><ul class="x">
    <li><b>Only int, arithmetic and print.</b> No if/else, loops or functions.</li>
    <li><b>Stops at the first error.</b> A program with three mistakes needs three runs.</li>
    <li><b>No unary minus.</b> <code>-5</code> must be written as <code>0 - 5</code>.</li>
    <li><b>Values are known at compile time</b> only because there is no input or loop.</li>
    <li><b>TAC is the final output.</b> There is no optimiser or machine code.</li></ul></div>
  <div class="blackbox"><div class="lbl">NEXT STEPS</div><ul class="x">
    <li>if / else, while and for loops; comparison and logical operators; printf</li>
    <li>Error recovery: report several errors per run</li>
    <li>Functions and arrays; char and float</li>
    <li>Data-flow analysis once loops and input exist</li>
    <li>Constant folding on TAC, then an assembly back end</li></ul></div>
</div>""")

# ---------------------------------------------------------------- 23 close
slide(None, f"""
<div class="eyebrow dim">CLOSING</div><h1 class="huge">Five steps, one story</h1>
<div class="five">{''.join(f'<div><b>{i + 1}</b><h4>{h}</h4><p>{p}</p></div>' for i, (h, p) in enumerate([
    ("Read", "the lexer tags every token with its line"), ("Parse", "one function per grammar rule"),
    ("Check", "names and values in the symbol table"), ("Generate", "three-address code, all or nothing"),
    ("Explain", "the line, the rule and one fix")]))}</div>
<div class="rq c">Other compilers ask: "Is this program valid?"<br><b>ErrorBuddy also answers: "Where is the mistake, and how do I fix it?"</b></div>
<div class="closing"><div class="team row">{''.join(f'<div><div class="who">{n}</div><div class="reg">{r}</div></div>' for n, r in TEAM)}</div>
<div class="thanks">Thank you<small>{REPO}</small></div></div>""", dark=True)

# ---------------------------------------------------------------- appendix
items = []
for name in ["valid", "precedence", "missing_semicolon", "undeclared_variable", "duplicate_declaration", "invalid_expression",
             "incorrect_parentheses", "extra_parenthesis", "division_by_zero", "empty"]:
    src = open(os.path.join(ROOT, f"examples/{name}.txt")).read()
    out = open(os.path.join(ROOT, f"examples/expected/{name}.out")).read()
    m = re.search(r"Error on line (\d+):\n(.*)\nSuggestion: (.*)\n\n\(Found during: (.*)\)", out)
    items.append(dict(cat="TEST SUITE · make test", title=name.replace("_", " ").capitalize(), src=src or "(empty file)",
                      ok=not m, phase=m[4] if m else "All phases", line=m and m[1], msg=m and m[2], sugg=m and m[3],
                      extra="Matches examples/expected/" + name + ".out", tac=None if m else re.search(r"\(Three-Address Code\):\n((?:    .*\n)*)", out)[1]))
for c in CASES.values():
    g = f"gcc 11.4: line {c['gcc_line']}: {q(c['gcc_msg'])}" if c["gcc_line"] else "gcc 11.4: nothing reported"
    items.append(dict(cat=f"CASE STUDY · fix belongs on line {c['fix']}", title=f"{c['id']} {c['name'][0].upper() + c['name'][1:]}", src=c["eb"],
                      ok=False, phase=c["eb_phase"], line=c["eb_line"], msg=c["eb_msg"], sugg=c["eb_sugg"], extra=g, tac=None))
PHN = {"Lexical Analysis": "Lexer (phase 1)", "Syntax Analysis": "Parser (phase 2)", "Semantic Analysis": "Semantic (phase 3)", "All phases": "All phases"}
pages = [items[i:i + 2] for i in range(0, len(items), 2)]
for k, pair in enumerate(pages):
    cells = ""
    for it in pair:
        res = (f'<b>Compilation successful</b><pre class="tacmini">{esc(it["tac"].rstrip())}</pre>' if it["ok"] else
               f'<b>Error on line {it["line"]}: {esc(it["msg"])}</b><p>Suggestion: {esc(it["sugg"])}</p>')
        cells += (f'<div class="case"><div class="cat">{esc(it["cat"])}</div><h3>{esc(it["title"])}</h3>'
                  f'<div class="tags">{tag("OK" if it["ok"] else "ERROR")}{tag(PHN.get(it["phase"], it["phase"]), False)}{tag("EXIT 0" if it["ok"] else "EXIT 1", False)}</div>'
                  f'<div class="prog"><div class="lbl">PROGRAM</div>{code(it["src"], cls="bare light")}</div>'
                  f'<div class="out"><div class="lbl">ACTUAL OUTPUT</div>{res}<p class="g">{esc(it["extra"])}</p></div></div>')
    slides.append(f'<section class="slide app"><div class="top app"><div class="brand"><b>EB;</b><span>ERRORBUDDY</span><span class="sep">|</span><span>APPENDIX: SAMPLE PROGRAMS</span></div></div>'
                  f'<div class="body two">{cells}</div><div class="foot"><span>APPENDIX {k + 1} / {len(pages)}</span><span>ERRORBUDDY · 5-PHASE COMPILER + FRIENDLY ERRORS</span></div></section>')

assert len(slides) == TOTAL + len(pages), len(slides)

CSS = open(os.path.join(HERE, "review.css")).read()
open(OUT_HTML, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><title>ErrorBuddy Review</title><style>{CSS}</style></head><body>{"".join(slides)}</body></html>')
subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML], check=True, capture_output=True)
print("wrote", OUT_PDF, len(slides), "slides")
