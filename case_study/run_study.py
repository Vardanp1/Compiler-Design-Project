#!/usr/bin/env python3
# run_study.py - reproduces every number in the ErrorBuddy case study.
#
#   python3 run_study.py            line-placement study (Sections 4-6)
#   python3 run_study.py --hints    "Did you mean" threshold study (Section 7)
#   python3 run_study.py --lexer    lexer-order experiments (Section 3)
#
# It builds three things from the real C++ sources in the parent folder:
#   E  ErrorBuddy as shipped (reports the line where the fix belongs)
#   D  the same compiler, patched so that every error reports the line of the
#      token the parser was looking at when it gave up (the detection point)
#   G  gcc on the equivalent C program (first diagnostic, -Wall -Wextra)
import os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
BUILD = os.path.join(HERE, "build")
sys.path.insert(0, HERE)
from corpus import CASES

C_HEAD = "#include <stdio.h>\nint main(void) {\n"   # 2 lines before the student code
C_TAIL = "\nreturn 0;\n}\n"
C_OFFSET = 2


def patched_build(name, edits):
    """Copy the real sources, apply (file, old, new) edits, compile."""
    d = os.path.join(BUILD, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for f in ("lexer.h", "lexer.cpp", "parser.h", "parser.cpp", "main.cpp"):
        shutil.copy(os.path.join(SRC, f), d)
    for f, old, new in edits:
        p = os.path.join(d, f)
        text = open(p).read()
        assert text.count(old) == 1, (name, f, old)
        open(p, "w").write(text.replace(old, new))
    exe = os.path.join(d, "errorbuddy")
    subprocess.run(["g++", "-std=c++17", "-O2", "-o", exe, "main.cpp", "lexer.cpp", "parser.cpp"],
                   cwd=d, check=True)
    return exe


def build_shipped():
    subprocess.run(["make", "-s", "-C", SRC], check=True, stdout=subprocess.DEVNULL)
    return os.path.join(SRC, "errorbuddy")


# Variant D: every lookahead records its line; fail() reports that line instead.
DETECTION_EDITS = [
    ("parser.h", "const Token& peek() const { return tokens[pos]; }",
     "const Token& peek() const { lookLine = tokens[pos].line; return tokens[pos]; }"),
    ("parser.h", "class Parser {", "extern int lookLine;\nclass Parser {"),
    ("parser.cpp", "    throw CompileError{line, phase, message, suggestion};",
     "    throw CompileError{lookLine ? lookLine : line, phase, message, suggestion};"),
    ("parser.cpp", "static const char* SYNTAX", "int lookLine = 0;\nstatic const char* SYNTAX"),
]


def run_eb(exe, source):
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(source)
    out = subprocess.run([exe, f.name], capture_output=True, text=True).stdout
    os.unlink(f.name)
    m = re.search(r"Error on line (\d+):\n(.*)\nSuggestion: (.*)\n\n\(Found during: (.*)\)", out)
    if not m:
        return dict(line=None, msg="", sugg="", phase="", raw=out)
    return dict(line=int(m[1]), msg=m[2], sugg=m[3], phase=m[4], raw=out)


def run_gcc(code):
    with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as f:
        f.write(C_HEAD + code + C_TAIL)
    r = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-O2", "-c", "-o", os.devnull,
                        "-fno-diagnostics-color", "-fdiagnostics-parseable-fixits", f.name],
                       capture_output=True, text=True)
    os.unlink(f.name)
    first = None
    for ln in r.stderr.splitlines():
        m = re.match(r".*?\.c:(\d+):\d+: (error|warning): (.*)", ln)
        if m and first is None:
            first = dict(line=int(m[1]) - C_OFFSET, kind=m[2], msg=m[3])
    if first is None:
        return dict(line=None, kind="none", msg="", fixit=False, raw=r.stderr)
    first["fixit"] = "fix-it:" in r.stderr or "did you mean" in r.stderr
    first["raw"] = r.stderr
    return first


def cell(line, fix):
    return "-" if line is None else str(line)


def placement_study():
    E = build_shipped()
    D = patched_build("detection", DETECTION_EDITS)
    rows, score = [], {k: dict(exact=0, caught=0, early=0, late=0) for k in "GDE"}
    print(f"{'case':<5}{'mistake':<42}{'fix':>4}{'G':>5}{'D':>5}{'E':>5}   gcc kind")
    for c in CASES:
        g, d, e = run_gcc(c["c"]), run_eb(D, c["eb"]), run_eb(E, c["eb"])
        for k, r in (("G", g), ("D", d), ("E", e)):
            if r["line"] is None:
                continue
            s = score[k]
            s["caught"] += 1
            if r["line"] == c["fix"]: s["exact"] += 1
            elif r["line"] > c["fix"]: s["late"] += 1
            else: s["early"] += 1
        rows.append((c, g, d, e))
        mark = lambda r: cell(r["line"], c["fix"]) + ("" if r["line"] in (None, c["fix"]) else "*")
        print(f"{c['id']:<5}{c['name']:<42}{c['fix']:>4}{mark(g):>5}{mark(d):>5}{mark(e):>5}   {g['kind']}")
    n = len(CASES)
    print()
    names = dict(G="gcc 11.4 (first diagnostic)", D="ErrorBuddy, detection-point line",
                 E="ErrorBuddy, fix-point line (shipped)")
    for k in "GDE":
        s = score[k]
        print(f"{k}  {names[k]:<38} caught={s['caught']:>2}/{n}  line-exact={s['exact']:>2}/{n}"
              f"  late={s['late']}  early={s['early']}")
    return rows


def hint_study():
    # Each probe: declared names, the mistyped word, and the hint that SHOULD appear.
    # A word with expected None is a genuinely new name; any hint for it is wrong.
    PROBES = [
        (["score", "bonus"], "scroe", "score"),
        (["total", "marks"], "totl", "total"),
        (["count"], "cuont", "count"),
        (["average"], "avrage", "average"),
        (["average"], "averge", "average"),
        (["result"], "reslt", "result"),
        (["total"], "totals", "total"),
        (["number"], "numbr", "number"),
        (["counter"], "conter", "counter"),
        (["salary"], "salry", "salary"),
        (["sum"], "sun", "sum"),
        (["max"], "mx", "max"),
        (["age"], "aeg", "age"),
        (["x", "y"], "z", None),
        (["a", "b"], "c", None),
        (["sum"], "sum2", None),
        (["total"], "tax", None),
        (["score"], "store", None),
        (["width"], "height", None),
        (["day"], "dry", None),
        (["rate"], "date", None),
        (["value"], "values", None),
        (["max"], "min", None),
        (["first", "last"], "fast", None),
    ]
    # NOTE: "values" vs "value" and "totals" vs "total" are deliberately ambiguous;
    # we label "totals" as a typo of an existing name and "values" as a new name
    # (two different decisions a real student might make). See Section 7.
    POLICIES = {
        "k1":       ("1 edit, all names",        "size_t allowed = target.size() <= 3 ? 1 : 2;", "size_t allowed = 1;", False),
        "shipped":  ("1 edit if <=3 letters else 2, skip names <3", None, None, True),
        "k2":       ("2 edits, all names",       "size_t allowed = target.size() <= 3 ? 1 : 2;", "size_t allowed = 2;", False),
        "k3":       ("3 edits, all names",       "size_t allowed = target.size() <= 3 ? 1 : 2;", "size_t allowed = 3;", False),
    }
    SKIP_SHORT = "if (entry.first.size() >= 3 && looksLike(name, entry.first))"
    NO_SKIP = "if (looksLike(name, entry.first))"
    print(f"{'policy':<9}{'rule':<46}{'right':>6}{'wrong':>6}{'missed':>7}{'silent-ok':>10}")
    results = {}
    for key, (rule, old, new, keep_skip) in POLICIES.items():
        if key == "shipped":
            exe = build_shipped()
        else:
            edits = [("parser.cpp", old, new)]
            if not keep_skip:
                edits.append(("parser.cpp", SKIP_SHORT, NO_SKIP))
            exe = patched_build("hint_" + key, edits)
        right = wrong = missed = silent = 0
        detail = []
        for names, typo, want in PROBES:
            prog = "".join(f"int {n} = 1;\n" for n in names) + f"{typo} = 2;\n"
            r = run_eb(exe, prog)
            m = re.search(r"Did you mean '([^']+)'", r["sugg"])
            got = m[1] if m else None
            if want is None:
                ok = got is None; silent += ok; wrong += not ok
            elif got == want: right += 1; ok = True
            elif got is None: missed += 1; ok = False
            else: wrong += 1; ok = False
            detail.append((typo, want, got))
        results[key] = detail
        print(f"{key:<9}{rule:<46}{right:>6}{wrong:>6}{missed:>7}{silent:>10}")
    print()
    print(f"{'typo':<7}{'expect':<8}" + "".join(f"{k:>8}" for k in POLICIES))
    for i, (names, typo, want) in enumerate(PROBES):
        print(f"{typo:<7}{str(want or '-'):<8}" + "".join(f"{str(results[k][i][2] or '-'):>8}" for k in POLICIES))


def lexer_study():
    E = build_shipped()
    # L1: comment check moved after the single-character symbols
    L1 = patched_build("lex_comment_late", [("lexer.cpp",
        "        // 2. Comments: '//' until the end of the line are ignored.\n"
        "        if (c == '/' && i + 1 < src.size() && src[i + 1] == '/') {\n"
        "            while (i < src.size() && src[i] != '\\n') i++;\n"
        "            continue;\n"
        "        }\n", "")])
    # L2: no check for a digit run followed by letters
    L2 = patched_build("lex_no_digit_name", [("lexer.cpp",
        "            if (i < src.size() && isLetter(src[i])) {", "            if (false) {")])
    # L3: keywords matched as a prefix before reading the whole word
    L3 = patched_build("lex_keyword_prefix", [("lexer.cpp",
        "        if (isLetter(c)) {\n",
        "        if (src.compare(i, 5, \"print\") == 0) { tokens.push_back({TokenType::KW_PRINT, \"print\", line}); i += 5; continue; }\n"
        "        if (src.compare(i, 3, \"int\") == 0)   { tokens.push_back({TokenType::KW_INT, \"int\", line}); i += 3; continue; }\n"
        "        if (isLetter(c)) {\n")])
    tests = [
        ("L1 comment rule after '/'", L1, "int a = 10 / 2; // half of ten\nprint a;\n"),
        ("L2 no digit-then-letter rule", L2, "int 2nd = 5;\nprint 2nd;\n"),
        ("L3 keyword matched as prefix", L3, "int interest = 5;\nint printer = 2;\nprint interest + printer;\n"),
    ]
    for title, exe, prog in tests:
        print("=" * 64)
        print(title)
        print("source:", prog.replace("\n", " | "))
        for label, x in (("shipped", E), ("variant", exe)):
            r = subprocess.run([x, "--tokens", "/dev/stdin"], input=prog, capture_output=True, text=True).stdout
            toks = re.findall(r"^\s+\d+\s+\S+\s+(\S+)$", r, re.M)
            status = "OK" if "Compilation successful" in r else re.search(r"Error on line \d+:\n.*", r)[0].replace("\n", " ")
            print(f"  {label:<8} tokens: {' '.join(toks) or '(lexer stopped)'}")
            print(f"  {'':<8} result: {status}")


if __name__ == "__main__":
    if "--hints" in sys.argv: hint_study()
    elif "--lexer" in sys.argv: lexer_study()
    else: placement_study()
