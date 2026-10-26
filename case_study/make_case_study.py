#!/usr/bin/env python3
# make_case_study.py - builds ErrorBuddy_Case_Study.pdf from the saved outputs
# of run_study.py (out_placement.txt, out_hints.txt, out_lexer.txt).
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                KeepTogether, Preformatted, CondPageBreak)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "ErrorBuddy_Case_Study.pdf")

TITLE = "Where Should an Error Point?"
SUBTITLE = ("A line-placement study from the ErrorBuddy compiler: at the token where parsing "
            "failed, or at the line where the fix belongs")
AUTHORS = [("Vardan Pandya", "24BCE2608"), ("Kunal Sharma", "24BCE2641")]
GUIDE = ""                           # e.g. "Prof. Name"
FOOTER = f"{TITLE} | " + ", ".join(f"{n} ({r})" for n, r in AUTHORS)

BLUE = colors.HexColor("#1F4E99")
INK = colors.HexColor("#1A1A1A")
GREY = colors.HexColor("#666666")
HEAD_BG = colors.HexColor("#DCE6F2")
ROW_BG = colors.HexColor("#F5F8FC")
GRID = colors.HexColor("#B8C7DC")
GREEN = colors.HexColor("#4CAF50")
RED = colors.HexColor("#E05050")
AMBER = colors.HexColor("#F0A030")
RED_BG = colors.HexColor("#FBDADA")
AMBER_BG = colors.HexColor("#FDEBCB")
TERM_BG = colors.HexColor("#300A24")
TERM_FG = colors.HexColor("#E6EDF3")

body = ParagraphStyle("body", fontName="Times-Roman", fontSize=10.5, leading=13.6,
                      alignment=TA_JUSTIFY, textColor=INK, spaceAfter=5)
h1 = ParagraphStyle("h1", fontName="Times-Bold", fontSize=14, leading=18, textColor=BLUE,
                    spaceBefore=9, spaceAfter=4)
h2 = ParagraphStyle("h2", fontName="Times-Bold", fontSize=11.5, leading=14, textColor=BLUE,
                    spaceBefore=6, spaceAfter=3)
cap = ParagraphStyle("cap", parent=body, fontName="Times-Italic", fontSize=9, leading=11,
                     textColor=GREY, spaceBefore=3, spaceAfter=8, alignment=0)
cell = ParagraphStyle("cell", fontName="Times-Roman", fontSize=8.8, leading=10.6, textColor=INK)
cellc = ParagraphStyle("cellc", parent=cell, alignment=TA_CENTER)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Times-Bold")
mono = ParagraphStyle("mono", fontName="Courier", fontSize=8.2, leading=10, textColor=INK)
term = ParagraphStyle("term", fontName="Courier", fontSize=7.3, leading=8.9, textColor=TERM_FG)

W = A4[0] - 2 * 18 * mm


def P(t, s=body): return Paragraph(t, s)
def C(t, s=cell): return Paragraph(t, s)
def code(t): return f'<font face="Courier" size="9">{escape(t)}</font>'


def table(rows, widths, head=True, extra=(), style=cell):
    data = [[c if not isinstance(c, str) else C(c, cellb if (head and i == 0) else style)
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * W for w in widths], repeatRows=1 if head else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, GRID),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HEAD_BG))
        for i in range(2, len(rows), 2):
            st.append(("BACKGROUND", (0, i), (-1, i), ROW_BG))
    t.setStyle(TableStyle(st + list(extra)))
    return t


def codebox(text, width=1.0):
    t = Table([[Preformatted(text, mono)]], colWidths=[width * W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F3F5F8")),
                           ("BOX", (0, 0), (-1, -1), 0.4, GRID),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def terminal(text, prompt, style=term, width=W):
    t = Table([[Preformatted(prompt + "\n" + text.rstrip("\n"), style)]], colWidths=[width])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TERM_BG),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def read(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read()


# ---------------------------------------------------------------- figures
def pipeline_figure():
    d = Drawing(W, 92)
    boxes = ["Source", "Lexer", "Parser\n(recursive descent)", "Semantic\n(symbol table)",
             "TAC", "Error\nreport"]
    bw, gap, y = 70, (W - 6 * 70) / 5, 52
    xs = [i * (bw + gap) for i in range(6)]
    for i, (x, label) in enumerate(zip(xs, boxes)):
        fill = colors.HexColor("#4A78C2") if i < 5 else colors.HexColor("#2E7D4F")
        d.add(Rect(x, y, bw, 30, rx=3, ry=3, fillColor=fill, strokeColor=None))
        lines = label.split("\n")
        for j, ln in enumerate(lines):
            d.add(String(x + bw / 2, y + 17 - (j - (len(lines) - 1) / 2) * 9 - 3, ln,
                         fontName="Helvetica", fontSize=7.5, fillColor=colors.white, textAnchor="middle"))
        if i < 5:
            d.add(Line(x + bw, y + 15, x + bw + gap, y + 15, strokeColor=GREY, strokeWidth=0.8))
    # the two choices, both made where the parser throws CompileError
    px = xs[2] + bw / 2
    for x, col, lab1, lab2, anc in ((px - 20, AMBER, "D: line of the token", "being looked at", "end"),
                                    (px + 20, GREEN, "E: line where the", "fix belongs", "start")):
        d.add(Line(x, y - 2, x, 2, strokeColor=col, strokeWidth=1.4))
        d.add(Polygon([x - 4, y - 2, x + 4, y - 2, x, y + 4], fillColor=col, strokeColor=None))
        tx = x - 4 if anc == "end" else x + 4
        d.add(String(tx, 14, lab1, fontName="Helvetica", fontSize=7, fillColor=col, textAnchor=anc))
        d.add(String(tx, 5, lab2, fontName="Helvetica", fontSize=7, fillColor=col, textAnchor=anc))
    gx = xs[5] + bw / 2
    d.add(String(gx, 30, "G: gcc on the", fontName="Helvetica", fontSize=7, fillColor=BLUE, textAnchor="middle"))
    d.add(String(gx, 21, "equivalent C", fontName="Helvetica", fontSize=7, fillColor=BLUE, textAnchor="middle"))
    return d


def bars_figure(rows):
    # rows: (label, exact, late, missed)
    d = Drawing(W, 20 + 24 * len(rows))
    scale = (W - 230) / 24
    for i, (label, exact, late, missed, note) in enumerate(rows):
        y = 20 + 24 * (len(rows) - 1 - i)
        d.add(String(0, y + 5, label, fontName="Helvetica", fontSize=8, fillColor=INK))
        x = 150
        for n, col in ((exact, GREEN), (late, RED), (missed, AMBER)):
            if n:
                d.add(Rect(x, y, n * scale, 16, fillColor=col, strokeColor=None))
                d.add(String(x + n * scale / 2, y + 5, str(n), fontName="Helvetica-Bold", fontSize=8,
                             fillColor=colors.white, textAnchor="middle"))
                x += n * scale
        d.add(String(x + 6, y + 5, note, fontName="Helvetica", fontSize=8, fillColor=INK))
    lx = 150
    for col, lab in ((GREEN, "reported on the fix line"), (RED, "reported on a later line"),
                     (AMBER, "not reported at all")):
        d.add(Rect(lx, 2, 8, 8, fillColor=col, strokeColor=None))
        d.add(String(lx + 12, 3, lab, fontName="Helvetica", fontSize=7.5, fillColor=INK))
        lx += 115
    return d


# ---------------------------------------------------------------- page decoration
def decorate(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(18 * mm, 10 * mm, FOOTER)
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()




# ---------------------------------------------------------------- content
def build():
    s = []
    s.append(P("CASE STUDY | COMPILER DESIGN", ParagraphStyle("k", parent=body, fontSize=9.5,
               alignment=TA_CENTER, textColor=GREY, spaceAfter=6)))
    s.append(P(TITLE, ParagraphStyle("t", fontName="Times-Bold", fontSize=22, leading=27,
               alignment=TA_CENTER, textColor=BLUE, spaceAfter=4)))
    s.append(P(SUBTITLE, ParagraphStyle("st", fontName="Times-Italic", fontSize=11, leading=14,
               alignment=TA_CENTER, spaceAfter=8)))
    for name, reg in AUTHORS:
        s.append(P(f"<b>{name}</b> ({reg})", ParagraphStyle("a", fontName="Times-Roman", fontSize=11.5,
                   leading=15, alignment=TA_CENTER)))
    if GUIDE:
        s.append(P(f"Under the guidance of <b>{GUIDE}</b>", ParagraphStyle("g", fontName="Times-Roman",
                   fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=GREY)))
    s.append(Spacer(1, 6))
    s.append(Table([[""]], colWidths=[W], rowHeights=[1],
                   style=[("LINEABOVE", (0, 0), (-1, -1), 0.8, BLUE)]))

    s.append(P("<i><b>Abstract</b></i> \u2014 A compiler error message normally points at the token where the "
               "parser found the problem. For most beginner mistakes this is also the line that has to be "
               "changed, but not for all of them: a missing semicolon is only noticed at the first token of "
               "the next statement, which can be a few lines further down. ErrorBuddy is a small compiler we "
               "wrote in C++17 for a beginner language, and its main aim is error messages that a beginner "
               "can act on. This case study looks at one design question from the project: which line should "
               "an error report? We made a second version of our compiler that reports the line where the "
               "parser stopped, and compared it with the normal version and with gcc 11.4 on 24 "
               "hand-labelled beginner mistakes. The normal version reported the correct line for all 24 "
               "mistakes, the second version for 21 and gcc for 20. gcc also gave no message at all for one "
               "division by zero. All of the wrong lines came from missing semicolons. We also tested the "
               "edit-distance limit used for the 'Did you mean' hints, which showed a bug in how our hints "
               "are chosen, and three ordering choices in the lexer. We show the output of the experiments "
               "as we ran them, explain what we found out from that output, show the compiler's real "
               "messages, and state the limits of the study.",
               ParagraphStyle("abs", parent=body, fontSize=10, leading=13, spaceBefore=6)))
    s.append(P("<b>Keywords:</b> error messages, recursive descent parsing, syntax-directed translation, "
               "three-address code, edit distance, lexical analysis.",
               ParagraphStyle("kw", parent=body, fontSize=9.5, leading=12)))

    # 1
    s.append(P("1. Scope and approach", h1))
    s.append(P("Our README and presentation already describe the language, the compiler phases and the test "
               "programs, so this case study does not repeat them. It follows one thread: our claim that "
               "ErrorBuddy reports the line where the fix belongs. In the presentation this claim rested on "
               "one example, and we wanted to check it on more than one. Every number in this report comes "
               f"from the script {code('case_study/run_study.py')}. The script compiles our real C++ source "
               "files, and copies of them with small changes, and runs them on a set of test programs. So "
               "what we measure is the compiler itself and not a separate model of it."))
    s.append(P("Section 2 explains how the compiler got its current shape. Section 3 covers the lexer rules "
               "that every error message depends on. Sections 4 and 5 present the experiment and its "
               "results. Section 6 shows the output of the experiment exactly as it printed on our machine "
               "and explains what we found out from it. Section 7 draws the design conclusion, and Section 8 "
               "shows what ErrorBuddy outputs."))

    # 2
    s.append(P("2. How we arrived at the idea", h1))
    s.append(P("The starting point was a mistake that every beginner makes in C, a missing semicolon. For "
               "the program below gcc reports the error on line 5, although the mistake is on line 4. The "
               "message uses grammar words ('expected ... before') and does not say what to type."))
    s.append(codebox("4 | int b = 10\n5 | printf(\"%d\\n\", a + b);\n\nm01.c:5:1: error: expected \u2018,\u2019 "
                     "or \u2018;\u2019 before \u2018printf\u2019"))
    s.append(P("From this example we set three goals for every error message: (1) it must point to the line "
               "where the fix belongs, (2) it must use plain words, and (3) it must give one concrete fix. "
               "We then made the choices in Table 1 with these goals in mind.",
               ParagraphStyle("b2", parent=body, spaceBefore=6)))
    s.append(table([
        ["Decision", "What we chose", "Reason", "Cost"],
        ["Language", "int variables, + - * /, brackets, print, every statement ends with ;",
         "Small enough that every phase and every message could be finished and tested",
         "No if, while, for or input"],
        ["Parser", "Hand-written recursive descent, one function per grammar rule",
         "When a rule fails we know which rule it was and which tokens are around it, so the message "
         "can be specific. A generated parser gives a generic 'syntax error'",
         "Every error case is written by hand"],
        ["Passes", "Syntax, semantics and TAC in one pass", "The parser already knows the context when a "
         "check fails", "TAC is held back until the whole program has passed"],
        ["Error object", "CompileError {line, phase, message, suggestion}, used by every phase",
         "Every error must have a line and a fix, and one function prints all of them",
         "Compilation stops at the first error"],
        ["Values", "Each expression's value is computed while compiling",
         "With no input and no loops every value is known, so a / zero can be proved to be a division by "
         "zero", "Will need rework once input is added"],
    ], [0.13, 0.28, 0.38, 0.21]))
    s.append(P("Table 1. Main design decisions and what each one cost (from the README, the pitch and the "
               "source code).", cap))
    s.append(P("The biggest change during the project was the language. Our proposal was for a subset of C "
               "with if, while, for and printf. While building it we cut this back to int variables, the four "
               "arithmetic operators, brackets and print, so that every phase and every error message could "
               "be finished and tested. Control flow is now future work. The second important choice was to "
               "compute the value of each expression while compiling. Since the language has no input and "
               "no loops, every value is known at compile time, and this is what lets ErrorBuddy prove that "
               f"{code('a / zero')} divides by zero when {code('zero')} is 0."))

    # 3
    s.append(P("3. The lexical groundwork: a fixed rule order and a keyword table", h1))
    s.append(P("Every error message gives a line number and quotes tokens from the program, for example "
               + code("Add a semicolon after '10'") + ". So the messages can only be right if the lexer "
               f"produces the right tokens. Our lexer ({code('lexer.cpp')}) is a hand-written scanner. At "
               "each position it tries the rules below in a fixed order. A word is first read completely "
               "and then looked up in a small keyword table; if it is not there, it stays an identifier."))
    s.append(codebox(
        "RULES (tried in this order at every position):\n"
        "  1 newline      \\n                          line = line + 1\n"
        "  2 whitespace   space, tab, \\r\n"
        "  3 comment      // up to the end of the line\n"
        "  4 number       [0-9]+                      error if a letter follows, error if > 2147483647\n"
        "  5 word         [A-Za-z_][A-Za-z_0-9]*      then keyword lookup\n"
        "  6 symbol       + - * / = ( ) ;\n"
        "    anything else                            error: unknown symbol\n"
        "KEYWORDS = { int -> KW_INT, print -> KW_PRINT }"))
    s.append(P(f"<b>Experiment 3.1: what the rules produce.</b> For the line "
               f"{code('int bonus = (score - 5) / 5; // round down')} the lexer emits KEYWORD(int) "
               "IDENTIFIER(bonus) ASSIGN LPAREN IDENTIFIER(score) OPERATOR(-) NUMBER(5) RPAREN OPERATOR(/) "
               "NUMBER(5) SEMICOLON. The comment produces no tokens, and each token keeps the line it came "
               "from.", ParagraphStyle("e1", parent=body, spaceBefore=6)))
    s.append(P(f"<b>Experiment 3.2: comment rule after the symbol rule.</b> We moved the {code('//')} check "
               f"below the single-character symbols and compiled {code('int a = 10 / 2; // half of ten')}. "
               f"The first {code('/')} was now taken as division, the comment became the tokens "
               f"{code('/ / half of ten')}, and the program failed with \"A statement cannot start with "
               "'/'.\" The comment rule has to come first, because it is the longer match."))
    s.append(P(f"<b>Experiment 3.3: no check for a digit followed by letters.</b> We removed the check in "
               f"rule 4 and compiled {code('int 2nd = 5;')}. The lexer split the name into NUMBER(2) and "
               "IDENTIFIER(nd), and the parser then reported \"Expected a variable name after 'int', but "
               "found '2'.\" With the check in place the error comes from the lexer and says what is "
               "actually wrong: \"'2nd' is not a valid name. Variable names cannot start with a digit.\""))
    s.append(P(f"<b>Experiment 3.4: keyword checked before the whole word is read.</b> We matched "
               f"{code('int')} and {code('print')} as prefixes before rule 5 and compiled "
               f"{code('int interest = 5; int printer = 2;')}. The variable interest was cut into the "
               "keyword int plus erest, and printer into print plus er, so the program failed with \"'int' "
               "is a reserved keyword and cannot be used as a variable name.\" With the word read first and "
               "looked up afterwards, both names stay whole."))
    s.append(P("<b>Why this matters for error messages.</b> In 3.3 and 3.4 the changed lexer still gives an "
               "error, but the error is about something the student did not write. A wrong token boundary "
               "changes which explanation the student gets. Each token also stores its line number, which is "
               "how a message such as 'Error on line 2' can point to the right place."))

    # 4
    s.append(CondPageBreak(70 * mm))
    s.append(P("4. The placement question and how we tested it", h1))
    s.append(P("When our parser cannot continue, it is looking at one token, the lookahead. The simplest rule "
               "is to report the line of that token. We call this the <i>detection point</i>. Our parser "
               f"does something different for some errors. In {code('expectSemicolon()')} a missing "
               f"semicolon is reported on {code('previous().line')}, the line of the last token of the "
               f"unfinished statement, and a missing {code(')')} is also reported on the line of the token it "
               "should follow. We call this the <i>fix point</i>. The question is which of the two is right "
               "more often. Figure 1 shows where the line is chosen."))
    s.append(pipeline_figure())
    s.append(P("Figure 1. Where the reported line is chosen. D and E use the same lexer, parser, checks and "
               "messages and differ only in the line stored in CompileError. G is gcc on the same mistake "
               "written in C.", cap))
    s.append(table([
        ["Variant", "What runs", "Which line it reports"],
        ["G", "gcc 11.4.0 with -std=c11 -Wall -Wextra -O2, on the same program written in C inside main()",
         "The line of gcc's first error or warning"],
        ["D", "ErrorBuddy built from our source files with a 4-line change",
         "Always the line of the lookahead token when the error was found (lexer errors keep their own "
         "line)"],
        ["E", "ErrorBuddy as submitted", "The fix point, chosen for each error as described above"],
    ], [0.1, 0.5, 0.4]))
    s.append(P("Table 2. The three variants.", cap))
    s.append(P("<b>Corpus and ground truth.</b> We wrote 24 short programs (listed in Table 3), each with one "
               "mistake: missing semicolons in four positions, bracket and operator mistakes, undeclared and "
               "misspelled names, a duplicate declaration, a variable used in its own declaration, three "
               "kinds of division by zero, two overflows and two lexical mistakes. For each program the fix "
               "line, the line the student has to change, was decided by hand before running any variant. "
               "A report counts as correct only if its line equals the fix line. Each program was written "
               f"twice, once in our language and once in C, where {code('print x;')} becomes "
               + code('printf("%d\\n", x);') + " and the misspelled keyword becomes " + code("prinft") +
               ". Mistakes that are legal C, such as a declaration without a value, were left out. The "
               "script is 232 lines of Python and the corpus 157 lines; both are supplied with this report "
               "so that every number below can be reproduced."))

    # 5
    s.append(P("5. What happened", h1))
    s.append(bars_figure([
        ("G  gcc 11.4", 20, 3, 1, "correct line on 20/24"),
        ("D  detection point", 21, 3, 0, "correct line on 21/24"),
        ("E  fix point (submitted)", 24, 0, 0, "correct line on 24/24"),
    ]))
    s.append(P("Figure 2. Summary of reported lines per variant on the 24-program corpus.", cap))

    rows = [["Program", "Mistake", "Fix line", "G", "D", "E"]]
    extra = []
    for ln in read("out_placement.txt").splitlines()[1:25]:
        cid, rest = ln[:5].strip(), ln[5:]
        name = rest[:42].strip()
        fix, g, dd, e, kind = rest[42:].split()
        r = len(rows)
        for col, v in ((3, g), (4, dd), (5, e)):
            if v.endswith("*"):
                extra.append(("BACKGROUND", (col, r), (col, r), RED_BG))
            elif v == "-":
                extra.append(("BACKGROUND", (col, r), (col, r), AMBER_BG))
        rows.append([cid, escape(name), fix, g.rstrip("*") + (" (warning)" if kind == "warning" else ""),
                     dd.rstrip("*"), e.rstrip("*")])
    s.append(table(rows, [0.09, 0.47, 0.1, 0.14, 0.1, 0.1], extra=extra))
    s.append(P("Table 3. Reported line per program. Red: a later line than the fix line. Amber: no report. "
               "(warning): gcc only warned, so the C program still compiles.", cap))

    s.append(P("5.1 The fix point (E) was exact", h2))
    s.append(P("The submitted compiler reported all 24 mistakes on their fix lines. M06 was the case we "
               "expected to be difficult: the expression is split over two lines, the ( is on line 2 and "
               "the missing ) belongs on line 3. E reports line 3, and the message still names the line of "
               "the opening bracket: \"Missing ')' to close the '(' opened on line 2.\""))
    s.append(P("5.2 The detection point (D) was late on missing semicolons", h2))
    s.append(P("D and E differ on three programs only, M01, M02 and M03. All three are missing semicolons "
               "followed by another statement. The listing for M02 shows why:"))
    s.append(codebox("1  int a = 5;\n2  int b = 10              <- fix line: E reports line 2\n3\n"
                     "4  // show the total\n5  print a + b;            <- parser notices here: D and gcc report "
                     "line 5"))
    s.append(P("The parser cannot know that the semicolon is missing until it reaches print, the first token "
               "of the next statement. The blank line and the comment in between are skipped by the lexer, "
               "so the detection point ends up three lines below the mistake. M04, a missing semicolon on "
               "the last statement, is noticed at the end of the file, whose line is still the last line, so "
               "D gets it right by chance. Every other mistake in the corpus is noticed at the wrong token "
               "itself, so D and E agree on them.", ParagraphStyle("b5", parent=body, spaceBefore=6)))
    s.append(P("5.3 gcc reported at the detection point", h2))
    s.append(P("For all 23 mistakes that gcc reported, its line was the same as D's, including the three late "
               "ones. gcc gave a fix-it hint in five cases (M04, M05, M06, M14 and M15). It gave no message "
               f"for M19, where the divisor is a variable that is 0 ({code('int zero = a - 10;')} and then "
               f"{code('a / zero')}), even with -Wall -Wextra -O2. ErrorBuddy finds it because it keeps the "
               "value of every variable. Six of gcc's 23 reports were only warnings (M15, M17, M18, M20, M21 "
               "and M22), so the C program still compiles and a beginner can easily miss the message."))
    s.append(P("5.4 A second test: the limit for 'Did you mean' hints", h2))
    s.append(P(f"For an undeclared name ErrorBuddy suggests a declared name with a small edit distance. The "
               f"rule in {code('looksLike()')} allows 1 edit for names of up to 3 letters and 2 edits for "
               "longer names, and names shorter than 3 letters are never suggested. We built three more "
               "versions that allow 1, 2 or 3 edits for every name and ran all four on 24 probes: 13 real "
               "typos of a declared name and 11 new names that should get no hint. The labels were decided "
               "before running."))
    hint_lines = read("out_hints.txt").splitlines()
    s.append(table([
        ["Version", "Rule", "Right hint", "Wrong hint", "Missed", "Correctly silent"],
        *[[ln[:9].strip(), escape(ln[9:55].strip()), *ln[55:].split()] for ln in hint_lines[1:5]],
    ], [0.1, 0.42, 0.12, 0.12, 0.1, 0.14],
        extra=[("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#E3F1E4"))]))
    s.append(P("Table 4. Hint results per version (submitted rule in green). 'Wrong hint' includes both a "
               "hint for a new name and a hint that names the wrong variable.", cap))
    s.append(P("The submitted rule did best: 12 of 13 typos found, and no hint for one-letter names such as z "
               "and c, which every uniform rule got wrong. Any limit large enough to catch scroe (two "
               "letters changed) also suggests existing names for new names that are one letter away, such "
               "as dry and day or date and rate. The only typo the submitted rule missed is aeg for age, a "
               "swap of two neighbouring letters, which Levenshtein distance counts as 2 edits. The test "
               "also showed a bug. With first and last declared, the typo fast gets the hint 'first' "
               f"(2 edits) instead of 'last' (1 edit). {code('similarVariable()')} goes through the symbol "
               "table in alphabetical order and returns the first name within the limit, not the closest "
               "one."))

    probe = hint_lines[6:]
    head, rest = probe[0], probe[1:]
    half = (len(rest) + 1) // 2
    small = ParagraphStyle("termsmall", parent=term, fontSize=6.6, leading=8.2)
    left = terminal("\n".join([head] + rest[:half]), "~/ErrorBuddy$ python3 case_study/run_study.py --hints",
                    small, W / 2)
    right = terminal("\n".join([head] + rest[half:]), " ", small, W / 2)
    both = Table([[left, right]], colWidths=[W / 2, W / 2])
    both.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                              ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, -1), TERM_BG)]))
    s.append(both)
    s.append(P("Figure 4. Per-probe part of the hint test output (one listing, shown in two columns): the hint each "
               "version printed.", cap))

    # 6
    s.append(P("6. Output of the experiment and what we found out", h1))
    s.append(P(f"After building the experiment we ran it on our own machine with "
               f"{code('python3 case_study/run_study.py')}. Figure 3 is the terminal output; the per-probe "
               "output of the hint test is Figure 4 in Section 5.4. This section reads that output line by line, because it "
               "is the evidence behind every claim in this report."))
    s.append(terminal(read("out_placement.txt"), "~/ErrorBuddy$ python3 case_study/run_study.py"))
    s.append(P("Figure 3. Output of run_study.py (Ubuntu 22.04, g++/gcc 11.4.0). The first block is the "
               "per-program table, the second the score of each variant.", cap))
    s.append(P("6.1 How to read the output", h2))
    s.append(P("The column <b>fix</b> is the fix line that we decided by hand before running anything. "
               "Columns <b>G</b>, <b>D</b> and <b>E</b> are the lines each variant reported. An asterisk "
               "means the line is not the fix line, and a dash means the variant gave no report. "
               "<b>gcc kind</b> says whether gcc's first message was an error or a warning. In the summary "
               "lines, <b>caught</b> is the number of mistakes reported at all, <b>line-exact</b> the number "
               "reported on the fix line, and <b>late</b> and <b>early</b> the number reported after or "
               "before it. In Figure 4 a dash means no hint was printed."))
    s.append(P("6.2 What we found out", h2))
    s.append(table([
        ["#", "Finding", "Evidence in the output"],
        ["1", "<b>The same checks give different results with a different line rule.</b> D and E share every "
              "check and every message, but D was right on 21 programs and E on 24.",
         "Summary lines: D line-exact=21/24, E line-exact=24/24."],
        ["2", "<b>Only missing semicolons are affected.</b> The rows where D differs from the fix line are "
              "M01, M02 and M03. On the other 21 programs D and E print the same line.",
         "Asterisks only in rows M01 to M03."],
        ["3", "<b>The error can be more than one line away.</b> Blank lines and comments push the "
              "detection point further down.", "M02: fix 2, G and D 5."],
        ["4", "<b>gcc uses the detection point.</b> Wherever gcc reported, its line equals D's line.",
         "Columns G and D are the same except M19."],
        ["5", "<b>Keeping variable values finds more.</b> A divisor that is a variable holding 0 was not "
              "reported by gcc.", "M19: G is a dash, gcc kind is none."],
        ["6", "<b>Some real problems are only warnings in C.</b> In six cases gcc let the program compile.",
         "gcc kind is warning on M15, M17, M18 and M20 to M22."],
        ["7", "<b>No variant reported too early.</b> An early line would be worse than a late one, because "
              "the student would change correct code.", "early=0 in all three summary lines."],
        ["8", "<b>The hint chooses the first close name, not the closest.</b>",
         "Figure 4, row fast: submitted version prints first."],
    ], [0.04, 0.64, 0.32]))
    s.append(P("Table 5. What the experiment output tells us.", cap))
    s.append(P("<b>End result in one paragraph.</b> Reporting the line of the token where the parser stopped, "
               "which is what gcc does, was correct for 21 of 24 beginner mistakes. It was wrong for the "
               "most common one, the missing semicolon, by one to three lines. Choosing the line for each "
               "kind of error, as the submitted ErrorBuddy does, fixed all three cases without changing any "
               "check or message. The hint limit we chose was the best of the four we tried, but the hint "
               "itself should be the closest name and not the first one found."))

    # 7
    s.append(P("7. What this means for our design", h1))
    s.append(P("<b>Short answer.</b> We keep the fix point for every error, and we will change the hint code "
               "to pick the closest name."))
    s.append(P("<b>1. Keep choosing the line per error.</b> This result has no downside. Three wrong lines "
               "were removed, no check or message changed, and no report got worse. The change in the code "
               f"is small: {code('previous().line')} instead of the lookahead's line in two places."))
    s.append(P("<b>2. Write the rule down so that it carries over.</b> The rule behind our choice is: if "
               "something is missing, report the line of the token it should follow; if something is wrong "
               "or extra, report the token itself. When we add if, while, for and braces, a missing } will "
               "be the same problem as a missing ; and this rule will apply to it."))
    s.append(P("<b>3. Fix the hint ranking.</b> similarVariable() should return the name with the smallest "
               "distance, and we could count a swap of two neighbouring letters as one edit so that aeg "
               "finds age. This is a few lines of code. We have not made the change yet, so all numbers in "
               "this report describe the submitted compiler."))
    s.append(P("<b>4. Keep proven problems as errors.</b> M17, M18 and M20 to M22 are only warnings in gcc, "
               "and M19 is not reported. In ErrorBuddy all six are errors. This is right for a language in "
               "which every value is known at compile time. Once input is added, 'the divisor is 0' and "
               "'the divisor may be 0' will need different severities."))
    s.append(P("<b>Threats to validity.</b> (a) The corpus is small (24 programs and 24 hint probes) and "
               "written by us. The fix lines and hint labels were fixed before running, but some are "
               "judgement calls: for an undeclared name we take the line where it is used, and we labelled "
               "totals as a typo of total but values as a new name. (b) gcc compiles C and not our "
               "language. We wrote each mistake in both, but C's grammar is larger and this affects some of "
               "gcc's choices. (c) We only score gcc's first message and only its line; the comparison of "
               "wording in Section 8 is not measured. (d) Our language has no control flow, so mistakes "
               "with braces or else, where the line question is harder, are not tested. (e) We did not test "
               "with real beginners, so we assume, but have not measured, that the right line saves them "
               "time."))

    # 8
    s.append(CondPageBreak(70 * mm))
    s.append(P("8. What ErrorBuddy outputs", h1))
    s.append(P("Every error has the form <i>Error on line L</i>, a message, a <i>Suggestion</i> and the phase "
               "that found it. An error stops compilation with exit code 1, and no intermediate code is "
               "printed. A correct program prints its three-address code, its symbol table and the list of "
               "completed phases, with exit code 0. The outputs below were produced by the compiler."))
    outs = [
        ("int a = 5;\nint b = 10\nprint a + b;", "Error on line 2:\nExpected ';' at the end of the statement.\n"
         "Suggestion: Add a semicolon after '10'.\n(Found during: Syntax Analysis)"),
        ("int x = 4;\nint y = x + * 3;", "Error on line 2:\nTwo operators in a row: '+' followed by '*'.\n"
         "Suggestion: Remove one of them, or put a number\nor variable between them."),
        ("int a = 10;\nint zero = a - 10;\nint b = a / zero;", "Error on line 3:\nDivision by zero. Variable "
         "'zero' is 0 at this point,\nso dividing by it is impossible.\n(Found during: Semantic Analysis)"),
        ("int score = 10;\nint bonus = 5;\nscroe = score + bonus;", "Error on line 3:\nVariable 'scroe' has "
         "not been declared.\nSuggestion: Did you mean 'score'? If 'scroe' is a\nnew variable, write 'int "
         "scroe = ...;'."),
        ("int 2nd = 5;", "Error on line 1:\n'2nd' is not a valid name. Variable names cannot\nstart with a "
         "digit.\n(Found during: Lexical Analysis)"),
        ("int a = 5;\nint b = 10;\nint c = a + b * 2;\nprint c;", "Compilation successful!\n  a = 5\n  b = 10\n"
         "  t1 = b * 2\n  t2 = a + t1\n  c = t2\n  print c"),
    ]
    rows = [["Program", "Output"]] + [[Preformatted(a, mono), Preformatted(b, mono)] for a, b in outs]
    s.append(table(rows, [0.4, 0.6]))
    s.append(P("Table 6. Real ErrorBuddy output. Each error names the line, the problem, a fix and the phase.",
               cap))
    s.append(P("The errors fall into three groups by phase. Lexical: unknown symbol, a name that starts with "
               "a digit, a number too large for an int. Syntax: missing ;, missing or extra ), two operators "
               "in a row, an operator with nothing after it, a missing operator between two values, empty "
               "brackets, a missing value after =, negative literals, misspelled keywords and lines that are "
               "not statements. Semantic: undeclared or misspelled variable, duplicate declaration, a "
               "variable used in its own declaration, division by zero (by a number, a variable or an "
               "expression) and overflow. A correct program never produces a message."))

    # 9
    s.append(P("9. Conclusions and lessons", h1))
    s.append(P("(1) The line an error reports is a design choice and should not simply be the place where the "
               "parser stopped. In a 24-program experiment the same compiler went from 21 to 24 correct "
               "lines by changing only the line rule. (2) The detection point goes wrong for mistakes where "
               "something is missing, because these are only noticed at the next token. (3) A compiler that "
               "knows every value can prove problems that gcc only warns about or does not see. (4) Hints "
               "need a ranking as well as a limit; our own test found that the submitted hint can name the "
               "wrong variable. (5) Small lexer choices (the comment rule first, reading the whole word "
               "before the keyword lookup) decide which explanation the student finally reads."))
    s.append(P(f"<b>Reproducing the experiment.</b> Run {code('make test')} (10 of 10 examples pass), then "
               f"{code('python3 case_study/run_study.py')}. It prints the table and summary lines shown in "
               f"Figure 3. The option {code('--hints')} prints Table 4 and Figure 4, and {code('--lexer')} "
               "runs the experiments of Section 3. The corpus with its fix lines is in "
               f"{code('case_study/corpus.py')}."))

    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=20 * mm, title=TITLE,
                            author=", ".join(f"{n} ({r})" for n, r in AUTHORS),
                            subject="ErrorBuddy case study")
    # keep every table or figure on the same page as its caption
    flow = []
    for f in s:
        long_table = isinstance(flow[-1] if flow else None, Table) and flow[-1]._nrows > 8
        if isinstance(f, Paragraph) and f.style is cap and flow and not long_table:
            flow[-1] = KeepTogether([flow[-1], f])
        else:
            flow.append(f)
    # and every heading on the same page as the block after it
    flow2 = []
    for f in reversed(flow):
        if isinstance(f, Paragraph) and f.style in (h1, h2) and flow2:
            nxt = flow2[-1]
            flow2[-1] = KeepTogether([f] + (nxt._content if isinstance(nxt, KeepTogether) else [nxt]))
        else:
            flow2.append(f)
    doc.build(flow2[::-1], onFirstPage=decorate, onLaterPages=decorate)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
