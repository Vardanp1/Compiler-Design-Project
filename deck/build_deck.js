// build_deck.js - builds ErrorBuddy_Complete.pptx (architecture + explanation in one deck)
//   node deck/build_deck.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "ErrorBuddy_Complete.pptx");
const SHOT = path.join(__dirname, "playground.png");

// Dark "terminal" palette taken from the web playground.
const HEX = {
  bg: "101318", panel: "1A1E25", line: "2D333D", text: "ECE8E1", muted: "9AA2AD",
  coral: "F2775F", green: "4CC38A", amber: "E2B451", blue: "7FA8F5", violet: "C39BF0",
};
const THEME = {
  name: "ErrorBuddy Terminal",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: HEX.bg, lt1: HEX.text, dk2: HEX.panel, lt2: HEX.muted,
    accent1: HEX.coral, accent2: HEX.green, accent3: HEX.amber, accent4: HEX.blue,
    accent5: HEX.line, accent6: HEX.violet, hlink: HEX.blue, folHlink: HEX.violet,
  },
};
const MONO = "Courier New";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "ErrorBuddy: complete architecture and explanation";
pres.author = "Vardan Pandya";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const K = {
  bg: C.text1, text: C.background1, panel: C.text2, muted: C.background2,
  coral: C.accent1, green: C.accent2, amber: C.accent3, blue: C.accent4, line: C.accent5, violet: C.accent6,
};

// ---------- layouts ----------
pres.defineSlideMaster({
  title: "EB_TITLE",
  background: { color: HEX.bg },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 1.2, w: 4.8, h: 1.0,
        fontSize: 46, align: "left", bold: true, color: K.text, valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.5, y: 2.35, w: 4.5, h: 1.2,
        fontSize: 18, color: K.muted, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "EB_SECTION",
  background: { color: HEX.bg },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 2.2, w: 9, h: 0.9,
        fontSize: 40, align: "left", bold: true, color: K.text, valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.5, y: 3.15, w: 8, h: 0.8,
        fontSize: 16, color: K.muted, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "EB_CONTENT",
  background: { color: HEX.bg },
  margin: [0.5, 0.5, 0.6, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9, h: 0.65,
        fontSize: 26, align: "left", bold: true, color: K.text, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "ErrorBuddy  ·  Compiler Design Project", options: {
        x: 5.6, y: 5.18, w: 3.4, h: 0.3, fontSize: 10, color: K.muted, align: "right", margin: 0 } } },
  ],
  slideNumber: { x: 9.1, y: 5.18, w: 0.4, h: 0.3, fontSize: 10, color: K.muted, align: "right", margin: 0 },
});

// ---------- helpers ----------
let n = 0;
const id = (s) => `${s}-${++n}`;

function panel(slide, x, y, w, h, fill = K.panel, border = K.line) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08,
    fill: { color: fill }, line: { color: border, width: 0.75 }, objectName: id("panel") });
}
function text(slide, t, o) {
  slide.addText(t, Object.assign({ isTextBox: true, margin: 0, color: K.text, fontSize: 14,
    valign: "top", objectName: id("text") }, o));
}
// Code block: array of lines or of run arrays.
function code(slide, lines, x, y, w, h, o = {}) {
  panel(slide, x, y, w, h, K.bg, K.line);
  const runs = [];
  lines.forEach((ln, i) => {
    const last = i === lines.length - 1;
    const parts = Array.isArray(ln) ? ln : [{ text: ln }];
    parts.forEach((p, j) => runs.push({ text: p.text, options: Object.assign({ color: K.text },
      p.options || {}, j === parts.length - 1 && !last ? { breakLine: true } : {}) }));
  });
  text(slide, runs, { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: h - 0.24, fontFace: MONO,
    fontSize: o.fontSize || 12, lineSpacingMultiple: o.spacing || 1.1 });
}
function label(slide, t, x, y, w, color = K.muted) {
  text(slide, t.toUpperCase(), { x, y, w, h: 0.25, fontSize: 10, bold: true, color, charSpacing: 1.5 });
}
function chip(slide, t, x, y, w, color, h = 0.32, size = 12) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06,
    fill: { color: K.panel }, line: { color, width: 1 }, objectName: id("chip") });
  text(slide, t, { x, y, w, h, fontSize: size, color, align: "center", valign: "middle", bold: true });
}
function arrow(slide, x1, y1, x2, y2, color = K.muted, dash) {
  slide.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2),
    w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
    line: { color, width: 1.25, endArrowType: "triangle", dashType: dash || "solid" }, objectName: id("arrow") });
}
// Box with a bold heading and a muted subline (diagram node).
function node(slide, head, sub, x, y, w, h, color = K.text, border = K.line, size = 13) {
  panel(slide, x, y, w, h, K.panel, border);
  text(slide, [
    { text: head, options: { bold: true, color, fontSize: size, breakLine: !!sub } },
    ...(sub ? [{ text: sub, options: { color: K.muted, fontSize: size > 12 ? 11 : 10 } }] : []),
  ], { x: x + 0.1, y, w: w - 0.2, h, align: "center", valign: "middle" });
}
// Phase strip motif: the same strip the playground shows, current phase lit.
const PHASES = ["1 Lexical", "2 Syntax", "3 Semantic", "4 TAC", "5 Errors"];
function phaseStrip(slide, active) {
  PHASES.forEach((p, i) => {
    const on = i === active;
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5 + i * 1.02, y: 5.16, w: 0.95, h: 0.28, rectRadius: 0.05,
      fill: { color: on ? K.coral : K.panel }, line: { color: on ? K.coral : K.line, width: 0.75 }, objectName: id("phase") });
    text(slide, p, { x: 0.5 + i * 1.02, y: 5.16, w: 0.95, h: 0.28, fontSize: 10, bold: on,
      color: on ? K.bg : K.muted, align: "center", valign: "middle" });
  });
}
function content(section, title, notes) {
  const s = pres.addSlide({ masterName: "EB_CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(section, num, title, sub, notes) {
  pres.addSection({ title: section });
  const s = pres.addSlide({ masterName: "EB_SECTION", sectionTitle: section });
  text(s, num, { x: 0.5, y: 1.45, w: 2, h: 0.7, fontSize: 40, bold: true, color: K.coral, fontFace: MONO });
  s.addText(title, { placeholder: "title" });
  s.addText(sub, { placeholder: "body" });
  if (notes) s.addNotes(notes);
  return s;
}
const err = { color: HEX.coral };
const ok = { color: HEX.green };

// =====================================================================
// 1. Title
pres.addSection({ title: "Introduction" });
{
  const s = pres.addSlide({ masterName: "EB_TITLE", sectionTitle: "Introduction" });
  s.addText([{ text: "Error" }, { text: "Buddy", options: { color: K.coral } }], { placeholder: "title" });
  s.addText("A beginner compiler that explains its own errors: the right line, plain words, one concrete fix.",
    { placeholder: "body" });
  text(s, "Compiler Design Project · C++17", { x: 0.5, y: 3.75, w: 4.4, h: 0.3, fontSize: 13, color: K.muted });
  text(s, "Architecture, every phase, evaluation and scope in one deck", { x: 0.5, y: 4.05, w: 4.4, h: 0.3, fontSize: 13, color: K.muted, italic: true });
  code(s, [
    [{ text: "$ ", options: ok }, { text: "./errorbuddy missing_semicolon.txt" }],
    "",
    [{ text: "Error on line 2:", options: err }],
    "Expected ';' at the end of the",
    "statement.",
    [{ text: "Suggestion: ", options: { color: HEX.amber } }, { text: "Add a semicolon" }],
    "after '10'.",
    "",
    [{ text: "(Found during: Syntax Analysis)", options: { color: HEX.muted } }],
  ], 5.4, 1.2, 4.1, 3.2, { fontSize: 13 });
  s.addNotes("ErrorBuddy is a small compiler written in C++17 with only the standard library. It takes a beginner language through lexing, parsing, semantic checks and three-address code, and its main contribution is the error message: the line where the fix belongs, plain English, and one concrete suggestion. This deck combines the earlier presentation and the architecture deck into one: problem, language, architecture, each phase, the web playground, testing, the case study, and what is built versus planned.");
}

// 2. At a glance + agenda
{
  const s = content("Introduction", "ErrorBuddy at a glance",
    "Numbers are from the source tree as of 26 Oct 2026: lexer.cpp, parser.cpp, main.cpp and the two headers add up to about 730 lines. make test passes all 10 example programs, and the case study shows every one of 24 classic mistakes reported on the line where the fix belongs.");
  const stats = [["5", "compiler phases"], ["3", "C++ source files"], ["~730", "lines of C++"], ["10/10", "tests pass (make test)"], ["24/24", "mistakes on the fix line"]];
  stats.forEach(([v, l], i) => {
    const x = 0.5 + (i % 3) * 1.55, y = 1.25 + Math.floor(i / 3) * 1.85;
    panel(s, x, y, 1.4, 1.6);
    text(s, v, { x, y: y + 0.2, w: 1.4, h: 0.7, fontSize: 30, bold: true, color: i < 3 ? K.text : K.green, align: "center", fontFace: MONO });
    text(s, l, { x: x + 0.1, y: y + 0.95, w: 1.2, h: 0.55, fontSize: 12, color: K.muted, align: "center" });
  });
  label(s, "In this deck", 5.4, 1.25, 4);
  const agenda = [["01", "Problem and idea", "why compiler errors confuse beginners"], ["02", "The language", "what ErrorBuddy compiles"],
    ["03", "Architecture", "files, data flow, one compile end to end"], ["04", "The five phases", "lexer, parser, symbol table, TAC, errors"],
    ["05", "Tools and evaluation", "playground, tests, case study"], ["06", "Scope", "built today versus planned"]];
  agenda.forEach(([num, h, d], i) => {
    const y = 1.6 + i * 0.55;
    text(s, num, { x: 5.4, y, w: 0.5, h: 0.45, fontSize: 14, bold: true, color: K.coral, fontFace: MONO });
    text(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: d, options: { color: K.muted, fontSize: 11 } }],
      { x: 5.95, y, w: 3.55, h: 0.5, fontSize: 14 });
  });
}

// =====================================================================
divider("Problem and idea", "01", "Problem and idea", "Compiler errors are written for people who already know the grammar.");

// 3. Problem
{
  const s = content("Problem and idea", "Compiler errors talk like grammars",
    "A beginner forgets one semicolon. gcc reports the next line, uses parser vocabulary like 'expected ... before', and never says what to type. Students lose a lot of time on messages like this.");
  label(s, "Program (equivalent C)", 0.5, 1.15, 4);
  code(s, ["1  int a = 5;", [{ text: "2  int b = 10        " }, { text: "<- real mistake", options: err }], "3  printf(\"%d\", a + b);"], 0.5, 1.45, 4.3, 1.1, { fontSize: 13 });
  label(s, "gcc 11.4 says", 5.2, 1.15, 4);
  code(s, ["program.c:3:5: error:", "expected ',' or ';'", "before 'printf'"], 5.2, 1.45, 4.3, 1.1, { fontSize: 13 });
  const cards = [["Wrong line", "Points at line 3. The fix belongs on line 2."], ["Jargon", "\"expected ... before\" is grammar talk, not plain English."], ["No fix", "Says what the parser wanted, never what to type."]];
  cards.forEach(([h, d], i) => {
    const x = 0.5 + i * 3.07;
    panel(s, x, 2.95, 2.9, 1.85);
    chip(s, "✕", x + 0.25, 3.2, 0.42, K.coral, 0.42, 16);
    text(s, h, { x: x + 0.25, y: 3.75, w: 2.4, h: 0.35, fontSize: 18, bold: true });
    text(s, d, { x: x + 0.25, y: 4.12, w: 2.45, h: 0.6, fontSize: 13, color: K.muted });
  });
}

// 4. Idea
{
  const s = content("Problem and idea", "Every error is a structured object",
    "ErrorBuddy's idea: an error is not a string, it is a CompileError with four fields. Any phase can throw it. main.cpp prints it in one fixed format. The four fields are what make the message teachable: where, which phase, what went wrong, and how to fix it.");
  code(s, [
    [{ text: "Error on line 2:", options: err }],
    "Expected ';' at the end of the statement.",
    [{ text: "Suggestion: ", options: { color: HEX.amber } }, { text: "Add a semicolon after '10'." }],
    "",
    [{ text: "(Found during: Syntax Analysis)", options: { color: HEX.muted } }],
  ], 0.5, 1.3, 4.6, 1.75, { fontSize: 12 });
  text(s, "Same mistake, ErrorBuddy output", { x: 0.5, y: 3.15, w: 4.6, h: 0.3, fontSize: 12, color: K.muted, italic: true });
  code(s, ["struct CompileError {", "    int    line;", "    string phase;", "    string message;", "    string suggestion;", "};"], 0.5, 3.5, 4.6, 1.45, { fontSize: 11, spacing: 1.0 });
  const fields = [["LINE", "2", "where the fix belongs, not where parsing stopped", K.coral], ["PHASE", "Syntax Analysis", "lexical, syntax or semantic", K.blue],
    ["MESSAGE", "Expected ';' at the end…", "what rule was broken, in plain English", K.text], ["SUGGESTION", "Add a semicolon…", "one concrete thing to type", K.amber]];
  fields.forEach(([f, v, d, col], i) => {
    const y = 1.3 + i * 0.92;
    panel(s, 5.5, y, 4.0, 0.8);
    text(s, f, { x: 5.65, y: y + 0.1, w: 1.35, h: 0.3, fontSize: 11, bold: true, color: col, charSpacing: 0.5 });
    text(s, v, { x: 7.05, y: y + 0.08, w: 2.35, h: 0.3, fontSize: 11, fontFace: MONO, color: K.text });
    text(s, d, { x: 5.65, y: y + 0.42, w: 3.75, h: 0.3, fontSize: 12, color: K.muted });
  });
}

// 5. Objectives
{
  const s = content("Problem and idea", "Four objectives",
    "These were the project goals: a working compiler down to intermediate code, every core phase, errors that read like a tutor, and only hand-written C++ with no Lex or Yacc so every message is under our control.");
  const objs = [["Build a working compiler", "Source text in, three-address code (TAC) out."], ["Cover every core phase", "Lexical, syntax, semantic, intermediate code and error reporting."],
    ["Report errors like a tutor", "The right line, plain words, one concrete fix."], ["Hand-written C++17 only", "Standard library, no Lex or Yacc, so each message is ours."]];
  objs.forEach(([h, d], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.3 + Math.floor(i / 2) * 1.85;
    panel(s, x, y, 4.4, 1.6);
    text(s, String(i + 1), { x: x + 0.3, y: y + 0.3, w: 0.8, h: 1.0, fontSize: 44, bold: true, color: K.coral, fontFace: MONO });
    text(s, h, { x: x + 1.2, y: y + 0.3, w: 3.05, h: 0.4, fontSize: 15, bold: true });
    text(s, d, { x: x + 1.2, y: y + 0.75, w: 3.0, h: 0.65, fontSize: 14, color: K.muted });
  });
}

// =====================================================================
divider("The language", "02", "The language", "A small, C-like beginner language, kept small on purpose so every phase is complete.");

// 6. Language
{
  const s = content("The language", "What ErrorBuddy compiles",
    "Every variable is an int and must be declared with a starting value. Arithmetic is + - * / with normal precedence and parentheses. print outputs any expression. Statements end with a semicolon and // starts a comment. There is no unary minus, no loops, no if/else and no functions, and compilation stops at the first error. The original proposal targeted a larger beginner-C subset; that is covered on the scope slide as planned work.");
  label(s, "examples/valid.txt", 0.5, 1.15, 4);
  code(s, [
    [{ text: "// A valid ErrorBuddy program", options: { color: HEX.muted } }],
    [{ text: "int", options: { color: HEX.violet } }, { text: " age = 20;" }],
    [{ text: "int", options: { color: HEX.violet } }, { text: " score = 10;" }],
    "score = score + age * 2;",
    [{ text: "int", options: { color: HEX.violet } }, { text: " bonus = (score - 5) / 5;" }],
    [{ text: "print", options: { color: HEX.violet } }, { text: " score;" }],
    [{ text: "print", options: { color: HEX.violet } }, { text: " bonus * (age + 1);" }],
  ], 0.5, 1.45, 4.4, 2.15, { fontSize: 12 });
  label(s, "Grammar (one C++ function per rule)", 5.2, 1.15, 4.3);
  code(s, ["program     → statement*", "statement   → declaration", "            | assignment | print",
    "declaration → int ID = expr ;", "assignment  → ID = expr ;", "print       → print expr ;",
    "expression  → term ((+|-) term)*", "term        → factor ((*|/) factor)*", "factor      → NUM | ID | ( expr )"], 5.2, 1.45, 4.3, 2.15, { fontSize: 11, spacing: 1.0 });
  const feats = [["Has", "int variables with a starting value, + - * /, ( ), print, // comments", K.green],
    ["Leaves out", "unary minus, if/else, loops, functions, input", K.coral], ["Stops", "at the first error, so no partial TAC is shown", K.amber]];
  feats.forEach(([h, d, col], i) => {
    const x = 0.5 + i * 3.07;
    panel(s, x, 3.85, 2.9, 1.1);
    text(s, h, { x: x + 0.2, y: 3.95, w: 2.5, h: 0.3, fontSize: 14, bold: true, color: col });
    text(s, d, { x: x + 0.2, y: 4.27, w: 2.55, h: 0.62, fontSize: 12, color: K.muted });
  });
}

// =====================================================================
divider("Architecture", "03", "Architecture", "Five phases in three C++ files, one error channel, three ways to run it.");

// 7. Full architecture
{
  const s = content("Architecture", "Five phases, three source files",
    "Only three C++ files. lexer.cpp is Phase 1. parser.cpp does Phases 2 to 4 in a single pass: while it recognises a statement it checks its meaning and emits its TAC. That is syntax-directed translation. Errors use one channel: a CompileError struct defined in lexer.h that any phase can throw. main.cpp catches it and prints it, and then no TAC is shown. Exit codes: 0 success, 1 compile error, 2 bad usage or unreadable file, 3 internal error.");
  // pipeline row
  node(s, "program.txt", "source text", 0.5, 1.35, 1.45, 0.85);
  node(s, "lexer.cpp", "Phase 1 · tokenize()", 2.3, 1.35, 1.6, 0.85, K.blue);
  panel(s, 4.25, 1.15, 3.05, 1.95, K.panel, K.coral);
  text(s, "parser.cpp · Phases 2–4, one pass", { x: 4.3, y: 1.22, w: 2.95, h: 0.3, fontSize: 11, bold: true, color: K.coral, align: "center" });
  [["Syntax", "recursive descent"], ["Semantic", "symbol table"], ["TAC", "t1 = a op b"]].forEach(([h, d], i) => {
    const x = 4.38 + i * 0.97;
    panel(s, x, 1.6, 0.88, 1.35, K.bg, K.line);
    text(s, [{ text: h, options: { bold: true, breakLine: true, fontSize: 11 } }, { text: d, options: { color: K.muted, fontSize: 10 } }],
      { x: x + 0.02, y: 1.6, w: 0.84, h: 1.35, align: "center", valign: "middle" });
  });
  node(s, "main.cpp", "driver · prints result", 7.65, 1.35, 1.85, 0.85, K.green);
  arrow(s, 1.95, 1.78, 2.3, 1.78);
  arrow(s, 3.9, 1.78, 4.25, 1.78);
  arrow(s, 7.3, 1.78, 7.65, 1.78);
  text(s, "string", { x: 1.83, y: 1.45, w: 0.6, h: 0.25, fontSize: 10, color: K.muted, align: "center" });
  text(s, "tokens", { x: 3.78, y: 1.45, w: 0.6, h: 0.25, fontSize: 10, color: K.muted, align: "center" });
  text(s, "TAC", { x: 7.25, y: 1.45, w: 0.45, h: 0.25, fontSize: 10, color: K.muted, align: "center" });
  // error channel
  panel(s, 2.3, 3.35, 7.2, 0.62, K.panel, K.coral);
  text(s, [{ text: "Phase 5 · CompileError { line, phase, message, suggestion }", options: { bold: true, color: K.coral, breakLine: true } },
    { text: "thrown at the first problem by any phase, caught in main.cpp", options: { color: K.muted, fontSize: 11 } }],
    { x: 2.45, y: 3.35, w: 6.9, h: 0.62, fontSize: 13, valign: "middle" });
  arrow(s, 3.1, 2.2, 3.1, 3.35, K.coral, "dash");
  arrow(s, 5.8, 3.1, 5.8, 3.35, K.coral, "dash");
  arrow(s, 8.6, 3.35, 8.6, 2.2, K.coral, "dash");
  // ways to run
  label(s, "Ways to run the same binary", 0.5, 4.2, 4);
  [["Terminal", "./errorbuddy file.txt [--tokens]"], ["make test", "diff against examples/expected"], ["Web playground", "web/server.py → JSON → browser"]].forEach(([h, d], i) => {
    const x = 0.5 + i * 3.07;
    text(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: d, options: { color: K.muted, fontSize: 10, fontFace: MONO } }],
      { x, y: 4.45, w: 2.95, h: 0.55, fontSize: 13 });
  });
  text(s, [{ text: "EXIT CODES", options: { bold: true, fontSize: 10, breakLine: true } }, { text: "0 ok · 1 error", options: { fontFace: MONO, breakLine: true } }, { text: "2 usage · 3 internal", options: { fontFace: MONO } }],
    { x: 0.5, y: 3.3, w: 1.75, h: 0.75, fontSize: 10, color: K.muted });
}

// 8. Files and responsibilities
{
  const s = content("Architecture", "What each file does",
    "Line counts from wc -l on 26 Oct 2026. The compiler itself is about 730 lines across the three .cpp files and two headers. CompileError lives in lexer.h so every phase can include and throw it. The parser holds most of Phase 5 as well: the diagnosis helpers and the typo hints.");
  const hdr = (t) => ({ text: t, options: { bold: true, color: HEX.muted, fontSize: 11, fill: { color: HEX.panel } } });
  const cell = (t, o = {}) => ({ text: t, options: Object.assign({ color: HEX.text, fontSize: 12 }, o) });
  const f = (t) => cell(t, { fontFace: MONO, color: HEX.coral });
  const rows = [
    [hdr("FILE"), hdr("LINES"), hdr("ROLE")],
    [f("main.cpp"), cell("88"), cell("Driver: reads the file, runs the phases, prints TAC, symbols and phase summary or the error; sets the exit code")],
    [f("lexer.h / lexer.cpp"), cell("48 / 114"), cell("Phase 1: Token, TokenType, tokenize(). Also defines CompileError")],
    [f("parser.h / parser.cpp"), cell("80 / 396"), cell("Phases 2–4 in one pass + most of Phase 5 (diagnosis helpers, typo hints)")],
    [f("Makefile"), cell("45"), cell("make, run, test, web, clean · g++ -std=c++17 -Wall -Wextra -pedantic -O2")],
    [f("examples/"), cell("10 + 10"), cell("Test programs and their expected output in examples/expected/*.out")],
    [f("web/"), cell("89 / 288"), cell("server.py + index.html: browser playground that runs the real binary")],
    [f("case_study/"), cell("972"), cell("24-mistake corpus, ErrorBuddy vs gcc study, hint and lexer experiments")],
  ];
  s.addTable(rows, { x: 0.5, y: 1.2, w: 9, colW: [2.2, 0.95, 5.85], rowH: 0.44, valign: "middle",
    border: { type: "solid", pt: 0.5, color: HEX.line }, fill: { color: HEX.bg }, margin: [0.04, 0.1, 0.04, 0.1], objectName: id("table") });
}

// 9. Execution flow of one compile
{
  const s = content("Architecture", "One compile, end to end",
    "Running ./errorbuddy examples/precedence.txt --tokens. main() reads the arguments and the whole file. tokenize() returns 22 tokens plus END_OF_FILE, each tagged with its line, and --tokens prints them as a table. The parser then loops over statements; for each one it parses, checks names and values against the symbol table, and appends TAC. If every statement passes, main prints TAC, symbol table and the phase summary and exits 0. At the first problem a CompileError is thrown, main prints the four fields, no TAC is shown, and the exit code is 1.");
  const steps = [["1", "Start", "main() reads path + --tokens, loads the whole file into one string"],
    ["2", "Lex", "tokenize() → vector<Token>, each with type, text and line"],
    ["3", "Parse + emit", "for every statement: grammar, symbol table, append TAC"],
    ["4", "Finish", "main() prints the result and sets the exit code"]];
  steps.forEach(([num, h, d], i) => {
    const x = 0.5 + i * 2.3;
    panel(s, x, 1.2, 2.1, 1.65);
    text(s, num, { x: x + 0.15, y: 1.3, w: 0.5, h: 0.45, fontSize: 22, bold: true, color: K.coral, fontFace: MONO });
    text(s, h, { x: x + 0.15, y: 1.75, w: 1.85, h: 0.3, fontSize: 14, bold: true });
    text(s, d, { x: x + 0.15, y: 2.07, w: 1.85, h: 0.75, fontSize: 11, color: K.muted });
    if (i < 3) arrow(s, x + 2.1, 2.02, x + 2.3, 2.02);
  });
  label(s, "every phase passed · exit 0", 0.5, 3.05, 4.3, K.green);
  code(s, ["Compilation successful!", "    t1 = b * 2", "    t2 = a + t1", "    c = t2", "[OK] 1. Lexical Analysis - 22 tokens …"], 0.5, 3.35, 4.3, 1.6, { fontSize: 11 });
  label(s, "first problem found · exit 1", 5.2, 3.05, 4.3, K.coral);
  code(s, [[{ text: "Error on line 3:", options: err }], "Division by zero. Variable 'zero'", "is 0 at this point …",
    [{ text: "Suggestion: ", options: { color: HEX.amber } }, { text: "Make sure the value" }], "on the right of '/' is not zero."], 5.2, 3.35, 4.3, 1.6, { fontSize: 11 });
}

// 10. Parser internals
{
  const s = content("Architecture", "Inside the parser",
    "This is the control flow of parser.cpp. parseProgram rejects an empty file, then calls statement until END_OF_FILE. statement dispatches on the first token. Every rule descends through expression, term and factor; binary computes the value, checks division by zero and int range, and emits one TAC instruction. expectSemicolon ends each statement and, if the semicolon is missing, diagnoses why. Each coral note is a place a CompileError can be thrown.");
  const row1 = 1.3, row2 = 3.15, bh = 0.72;
  node(s, "parseProgram()", "until END_OF_FILE", 0.5, row1, 1.55, bh, K.text, K.line, 10);
  node(s, "statement()", "dispatch on 1st token", 2.4, row1, 1.6, bh, K.text, K.line, 10);
  [["int", "declaration()"], ["name =", "assignment()"], ["print", "printStatement()"]].forEach(([k, f], i) => {
    const y = 1.12 + i * 0.4;
    panel(s, 4.35, y, 1.9, 0.34);
    text(s, [{ text: k + "  ", options: { color: K.coral, bold: true } }, { text: f, options: { fontFace: MONO } }],
      { x: 4.43, y, w: 1.8, h: 0.34, fontSize: 11, valign: "middle" });
  });
  node(s, "expression()", "loops on + −", 6.6, 1.12, 1.35, 0.5, K.text, K.line, 10);
  node(s, "term()", "loops on * /", 6.6, 1.72, 1.35, 0.5, K.text, K.line, 10);
  node(s, "factor()", "NUM, ID, (expr)", 8.15, 1.12, 1.35, 1.1, K.text, K.line, 10);
  arrow(s, 2.05, row1 + bh / 2, 2.4, row1 + bh / 2);
  arrow(s, 4.0, row1 + bh / 2, 4.35, row1 + bh / 2);
  arrow(s, 6.25, row1 + bh / 2, 6.6, row1 + bh / 2);
  arrow(s, 7.95, 1.67, 8.15, 1.67);
  const errs1 = [[0.5, 1.55, "empty program"], [2.4, 1.6, "misspelled keyword, lone name, extra ;"], [4.35, 1.9, "already declared, keyword as name, not declared + Did you mean"], [6.6, 2.9, "two operators in a row, -5, empty ( ), missing )"]];
  errs1.forEach(([x, w, t]) => text(s, "throws: " + t, { x, y: 2.48, w, h: 0.55, fontSize: 10, color: K.coral }));
  // row 2
  node(s, "binary()", "value, div by 0, int range, emit", 6.6, row2, 2.9, bh, K.text, K.line, 10);
  node(s, "expectSemicolon()", "ends every statement", 4.35, row2, 1.9, bh, K.text, K.line, 10);
  node(s, "save", "symbol table, emit, loop", 2.4, row2, 1.6, bh, K.text, K.line, 10);
  node(s, "Success", "TAC → main.cpp", 0.5, row2, 1.55, bh, K.green, K.green, 10);
  arrow(s, 8.82, 2.22, 8.82, row2);
  arrow(s, 6.6, row2 + bh / 2, 6.25, row2 + bh / 2);
  arrow(s, 4.35, row2 + bh / 2, 4.0, row2 + bh / 2);
  arrow(s, 2.4, row2 + bh / 2, 2.05, row2 + bh / 2);
  text(s, "throws: division by zero, int overflow", { x: 6.6, y: 3.95, w: 2.9, h: 0.3, fontSize: 10, color: K.coral });
  text(s, "throws: extra ), extra =, missing operator, missing ;", { x: 4.35, y: 3.95, w: 2.1, h: 0.5, fontSize: 10, color: K.coral });
  text(s, "After save, statement() runs again until END_OF_FILE. Every throw is a CompileError caught by main.cpp.", { x: 0.5, y: 4.6, w: 9, h: 0.3, fontSize: 11, color: K.muted, italic: true });
}

// =====================================================================
divider("The five phases", "04", "The five phases", "Lexer, parser, symbol table, three-address code, and the error engine.");

// 11. Phase 1
{
  const s = content("The five phases", "Phase 1 · The lexer makes tokens",
    "A hand-written scanner: one loop over the characters. A newline increments the line counter, whitespace and // comments are skipped, runs of digits become NUMBER, letters or underscore start a name and int and print become keywords, and single characters become symbols. It always appends END_OF_FILE. The line stored on every token is what later makes accurate error lines possible.");
  phaseStrip(s, 0);
  label(s, "Input", 0.5, 1.15, 2);
  code(s, ["int c = a + b * 2;"], 0.5, 1.45, 3.2, 0.5, { fontSize: 14 });
  label(s, "Output: vector<Token>  (text · type · line)", 4.0, 1.15, 5.5);
  const toks = [["int", "KEYWORD"], ["c", "IDENT"], ["=", "ASSIGN"], ["a", "IDENT"], ["+", "OPERATOR"], ["b", "IDENT"], ["*", "OPERATOR"], ["2", "NUMBER"], [";", "SEMI"]];
  toks.forEach(([t, ty], i) => {
    const x = 0.5 + i * 1.0;
    panel(s, x, 2.15, 0.9, 0.85);
    text(s, t, { x, y: 2.2, w: 0.9, h: 0.4, fontSize: 18, bold: true, align: "center", fontFace: MONO, color: K.coral });
    text(s, ty, { x, y: 2.6, w: 0.9, h: 0.3, fontSize: 9, align: "center", color: K.muted });
  });
  const cols = [["Skips and tracks", ["spaces and // comments", "counts newlines, so every token carries its line"], K.green],
    ["Rejects (lexical errors)", ["unknown symbols such as @", "numbers above INT_MAX", "names that start with a digit: 2nd"], K.coral],
    ["Hands on", ["token list ending in END_OF_FILE", "--tokens prints it as a line / type / text table"], K.blue]];
  cols.forEach(([h, items, col], i) => {
    const x = 0.5 + i * 3.07;
    panel(s, x, 3.25, 2.9, 1.7);
    text(s, h, { x: x + 0.2, y: 3.35, w: 2.5, h: 0.3, fontSize: 14, bold: true, color: col });
    text(s, items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1 } })),
      { x: x + 0.2, y: 3.7, w: 2.55, h: 1.2, fontSize: 12, color: K.text, paraSpaceAfter: 3 });
  });
}

// 12. Phase 2 grammar + call tree
{
  const s = content("The five phases", "Phase 2 · Recursive descent",
    "Recursive descent: each grammar rule is one C++ function. expression calls term, term calls factor. Because * and / live one level deeper than + and -, they bind tighter without any precedence table. The while loops in expression and term make operators left-associative, so 10 - 4 - 3 is (10 - 4) - 3. factor recurses on '(' with a nesting limit of 200. Writing the parser by hand gives full control over every error message, which is the point of the project.");
  phaseStrip(s, 1);
  label(s, "C++ shape of the rules", 0.5, 1.15, 4);
  code(s, [
    "Operand expression() {",
    "  Operand l = term();",
    "  while (check(PLUS) || check(MINUS))",
    "    l = binary(l, advance(), term());",
    "  return l;",
    "}",
    "Operand term() {    // same, * and /",
    "  ... factor() ...",
    "}",
  ], 0.5, 1.45, 4.3, 2.6, { fontSize: 11, spacing: 1.0 });
  label(s, "Call tree for  a + b * 2", 5.2, 1.15, 4.3);
  const n1 = (t, x, y, w, col = K.text) => { panel(s, x, y, w, 0.42); text(s, t, { x, y, w, h: 0.42, fontSize: 11, fontFace: MONO, align: "center", valign: "middle", color: col }); };
  n1("expression()", 6.4, 1.5, 1.9);
  n1("term()", 5.2, 2.25, 1.2); n1("+", 6.75, 2.25, 0.5, K.coral); n1("term()", 7.95, 2.25, 1.2);
  n1("factor: a", 5.2, 3.0, 1.2); n1("factor: b", 6.75, 3.0, 1.1); n1("*", 7.97, 3.0, 0.35, K.coral); n1("factor: 2", 8.42, 3.0, 1.08);
  arrow(s, 7.0, 1.92, 5.8, 2.25); arrow(s, 7.0, 1.92, 7.0, 2.25); arrow(s, 7.6, 1.92, 8.55, 2.25);
  arrow(s, 5.8, 2.67, 5.8, 3.0); arrow(s, 8.35, 2.67, 7.3, 3.0); arrow(s, 8.55, 2.67, 8.15, 3.0); arrow(s, 8.8, 2.67, 8.96, 3.0);
  text(s, "b * 2 finishes inside the right-hand term() before + is applied, so the TAC computes it first.", { x: 5.2, y: 3.6, w: 4.3, h: 0.5, fontSize: 12, color: K.muted });
  panel(s, 0.5, 4.3, 9, 0.65);
  text(s, [{ text: "Precedence comes from the grammar, not a table.  ", options: { bold: true } },
    { text: "Loops make operators left-associative: 10 - 4 - 3 = (10 - 4) - 3.", options: { color: K.muted } }],
    { x: 0.7, y: 4.3, w: 8.6, h: 0.65, fontSize: 13, valign: "middle" });
}

// 13. Syntax-directed translation trace
{
  const s = content("The five phases", "Parse, check and emit in one pass",
    "Worked trace for int c = a + b * 2. declaration calls expression; term returns a; plus is seen; the next term takes b, sees star, takes 2 and calls binary, which emits t1 = b * 2. Back in expression, binary emits t2 = a + t1. expectSemicolon finds the semicolon, c goes into the symbol table, and c = t2 is emitted. Code for each statement is emitted as soon as it is parsed, so TAC stays in source order.");
  phaseStrip(s, 1);
  const tr = [["declaration()", "sees int c =, calls expression()"], ["term() → a", "first operand, + is next"], ["term() → b * 2", "binary() emits  t1 = b * 2"],
    ["expression()", "binary() emits  t2 = a + t1"], ["expectSemicolon()", "; found, c enters the symbol table, emit  c = t2"]];
  tr.forEach(([h, d], i) => {
    const y = 1.2 + i * 0.75;
    chip(s, String(i + 1), 0.5, y + 0.1, 0.42, K.coral, 0.42, 14);
    text(s, [{ text: h, options: { bold: true, fontFace: MONO, breakLine: true } }, { text: d, options: { color: K.muted, fontSize: 12 } }],
      { x: 1.1, y, w: 4.5, h: 0.65, fontSize: 13 });
  });
  label(s, "TAC · precedence.txt", 6.0, 1.15, 3.5);
  code(s, ["a = 5", "b = 10", [{ text: "t1 = b * 2", options: { color: HEX.coral } }], [{ text: "t2 = a + t1", options: { color: HEX.coral } }], [{ text: "c = t2", options: { color: HEX.coral } }], "print c"], 6.0, 1.45, 3.5, 2.3, { fontSize: 14 });
  text(s, "This is syntax-directed translation: syntax, semantics and code generation share one walk over the tokens.", { x: 6.0, y: 3.9, w: 3.5, h: 0.9, fontSize: 12, color: K.muted, italic: true });
}

// 14. Phase 3 symbol table
{
  const s = content("The five phases", "Phase 3 · Symbol table checks",
    "The symbol table is a std::map from name to Symbol {declaredLine, value}. Semantic checks run inside the parser at the moment each name or operator is seen. A name is added only after its initial value is parsed, so int a = a + 1 is caught. Because the language has no input and no loops, every value is known at compile time; that is how a / zero is caught even when zero is a variable.");
  phaseStrip(s, 2);
  label(s, "Symbol table after valid.txt", 0.5, 1.15, 4);
  const h = (t) => ({ text: t, options: { bold: true, color: HEX.muted, fontSize: 11, fill: { color: HEX.panel } } });
  const c = (t, col = HEX.text) => ({ text: t, options: { color: col, fontSize: 13, fontFace: MONO } });
  s.addTable([[h("NAME"), h("DECLARED"), h("VALUE")], [c("age", HEX.coral), c("line 2"), c("20")], [c("score", HEX.coral), c("line 3"), c("50")], [c("bonus", HEX.coral), c("line 5"), c("9")]],
    { x: 0.5, y: 1.45, w: 3.9, colW: [1.4, 1.4, 1.1], rowH: 0.42, valign: "middle", border: { type: "solid", pt: 0.5, color: HEX.line }, fill: { color: HEX.bg }, margin: [0.04, 0.1, 0.04, 0.1], objectName: id("table") });
  panel(s, 0.5, 3.35, 3.9, 1.6);
  text(s, [{ text: "Why values are tracked", options: { bold: true, breakLine: true } },
    { text: "No input and no loops means every value is known while compiling, so division by a variable that is 0 is caught before the program runs.", options: { color: K.muted, fontSize: 12 } }],
    { x: 0.7, y: 3.45, w: 3.5, h: 1.4, fontSize: 14 });
  const checks = [["Undeclared or misspelled", "scroe = 2;  →  Did you mean 'score'?"], ["Declared twice", "'age' already declared on line 1"],
    ["No starting value", "int a;  →  needs '= value'"], ["Used in its own declaration", "int a = a + 1;"], ["Division by zero · overflow", "a / zero,  8 / (4 - 4),  int range"]];
  checks.forEach(([hh, d], i) => {
    const y = 1.15 + i * 0.77;
    panel(s, 4.75, y, 4.75, 0.66);
    text(s, [{ text: hh, options: { bold: true, breakLine: true } }, { text: d, options: { color: K.muted, fontFace: MONO, fontSize: 11 } }],
      { x: 4.95, y, w: 4.45, h: 0.66, fontSize: 13, valign: "middle" });
  });
}

// 15. Phase 4 TAC
{
  const s = content("The five phases", "Phase 4 · Three-address code",
    "This is the real output for examples/valid.txt: 12 instructions. Each instruction has at most one operator. Temporaries t1, t2 and so on are numbered by newTemp, which skips any name the user already wrote so a temp never clashes with a variable. Parentheses only change grouping and produce no instructions. TAC is printed only if the whole program passes.");
  phaseStrip(s, 3);
  label(s, "Source", 0.5, 1.15, 3);
  code(s, ["int age = 20;", "int score = 10;", "score = score + age * 2;", "int bonus = (score - 5) / 5;", "print score;", "print bonus * (age + 1);"], 0.5, 1.45, 3.6, 2.2, { fontSize: 12 });
  label(s, "TAC (12 instructions)", 4.4, 1.15, 3);
  code(s, ["age = 20", "score = 10", "t1 = age * 2", "t2 = score + t1", "score = t2", "t3 = score - 5"], 4.4, 1.45, 2.45, 2.2, { fontSize: 12 });
  code(s, ["t4 = t3 / 5", "bonus = t4", "print score", "t5 = age + 1", "t6 = bonus * t5", "print t6"], 7.05, 1.45, 2.45, 2.2, { fontSize: 12 });
  const rules = [["One operator", "per instruction: t1 = a op b"], ["Safe temps", "t1, t2… skip names already used"], ["All or nothing", "printed only if every phase passes"]];
  rules.forEach(([hh, d], i) => {
    const x = 0.5 + i * 3.07;
    panel(s, x, 3.9, 2.9, 1.05);
    text(s, [{ text: hh, options: { bold: true, color: K.green, breakLine: true } }, { text: d, options: { color: K.muted, fontSize: 12 } }],
      { x: x + 0.2, y: 3.9, w: 2.55, h: 1.05, fontSize: 14, valign: "middle" });
  });
}

// 16. Phase 5 error examples
{
  const s = content("The five phases", "Phase 5 · Errors that teach",
    "Every row is real ErrorBuddy output from the examples folder or the case-study corpus. The message names the rule that was broken in plain English, and the suggestion says what to type.");
  phaseStrip(s, 4);
  const h = (t) => ({ text: t, options: { bold: true, color: HEX.muted, fontSize: 11, fill: { color: HEX.panel } } });
  const m = (t) => ({ text: t, options: { color: HEX.coral, fontSize: 12, fontFace: MONO } });
  const c = (t) => ({ text: t, options: { color: HEX.text, fontSize: 12 } });
  const g = (t) => ({ text: t, options: { color: HEX.muted, fontSize: 11 } });
  s.addTable([
    [h("MISTAKE"), h("PHASE"), h("ERRORBUDDY SAYS")],
    [m("int b = (a + 2)) * 3;"), g("Syntax"), c("Found an extra ')' that has no matching '('.")],
    [m("int y = (x + 3 * 4;"), g("Syntax"), c("Missing ')' to close the '(' opened on line 2. Add ')' after '4'.")],
    [m("int y = x + * 3;"), g("Syntax"), c("Two operators in a row: '+' followed by '*'.")],
    [m("int a = -5;"), g("Syntax"), c("Negative numbers such as '-5' are not supported directly. Write 0 - 5.")],
    [m("prnt x;"), g("Syntax"), c("Unknown word 'prnt'. Did you mean the keyword 'print'?")],
    [m("total + marks"), g("Semantic"), c("Variable 'marks' has not been declared. Declare it: 'int marks = 0;'")],
    [m("int age = 19;"), g("Semantic"), c("Variable 'age' has already been declared (on line 1).")],
    [m("int x = 2nd;"), g("Lexical"), c("'2nd' is not a valid name. Variable names cannot start with a digit.")],
  ], { x: 0.5, y: 1.15, w: 9, colW: [2.3, 0.95, 5.75], rowH: 0.42, valign: "middle", border: { type: "solid", pt: 0.5, color: HEX.line }, fill: { color: HEX.bg }, margin: [0.03, 0.1, 0.03, 0.1], objectName: id("table") });
}

// 17. Diagnosis by looking around
{
  const s = content("The five phases", "Diagnosis reads nearby tokens",
    "expectSemicolon runs when a statement should be over. If the next token is not a semicolon, it looks at what it is instead to name the likely cause. The last rule is why a missing semicolon on line 2 is reported on line 2, not on line 3 where the parser noticed it. factorError and unknownStatementError use the same idea: look at the previous and next token instead of printing a generic syntax error.");
  phaseStrip(s, 4);
  text(s, [{ text: "expectSemicolon()", options: { fontFace: MONO, bold: true, color: K.coral } }, { text: "  the statement is over, but the next token is not ';'. What is it?", options: { color: K.muted } }],
    { x: 0.5, y: 1.15, w: 9, h: 0.35, fontSize: 13 });
  const rules = [[")", "Found an extra ')' that has no matching '('."], ["=", "Unexpected '='. A statement can contain only one '='."],
    ["x  5  (  same line", "Missing operator between the two values."], ["anything else", "Expected ';', reported on the line of the previous token."]];
  rules.forEach(([t, d], i) => {
    const y = 1.6 + i * 0.55;
    panel(s, 0.5, y, 2.6, 0.45);
    text(s, t, { x: 0.6, y, w: 2.4, h: 0.45, fontSize: 13, fontFace: MONO, bold: true, valign: "middle", color: K.amber });
    arrow(s, 3.15, y + 0.22, 3.55, y + 0.22);
    text(s, d, { x: 3.65, y, w: 5.85, h: 0.45, fontSize: 13, valign: "middle" });
  });
  const sib = [["factorError()", "a value was expected: two operators in a row, -5, empty ( ), keyword inside an expression, program ended mid-expression"],
    ["unknownStatementError()", "a statement starts wrongly: misspelled or capitalised keyword, a name on its own, an extra ';', '=' with no name"]];
  sib.forEach(([f, d], i) => {
    const x = 0.5 + i * 4.6;
    panel(s, x, 3.9, 4.4, 1.05);
    text(s, [{ text: f, options: { fontFace: MONO, bold: true, color: K.coral, breakLine: true } }, { text: d, options: { color: K.muted, fontSize: 12 } }],
      { x: x + 0.2, y: 3.9, w: 4.0, h: 1.05, fontSize: 13, valign: "middle" });
  });
}

// 18. Typo hints chart
{
  const s = content("The five phases", "Typo hints use edit distance",
    "Hints use Levenshtein distance computed in a single rolling row (editDistance in parser.cpp). The case study tried four policies on 23 typo cases from case_study/corpus.py. Looser limits find more right answers but also more wrong ones. The shipped rule allows 1 edit for names up to 3 letters, 2 for longer names, skips names shorter than 3 letters as candidates, and never suggests the word itself. It gives the fewest wrong suggestions, 6, while still getting 12 right.");
  phaseStrip(s, 4);
  s.addChart(pres.charts.BAR, [
    { name: "Right suggestion", labels: ["1 edit", "Shipped", "2 edits", "3 edits"], values: [10, 12, 13, 13] },
    { name: "Wrong suggestion", labels: ["1 edit", "Shipped", "2 edits", "3 edits"], values: [8, 6, 9, 10] },
  ], { x: 0.5, y: 1.15, w: 5.2, h: 3.8, barDir: "col", barGrouping: "clustered", chartColors: [HEX.green, HEX.coral],
    showTitle: true, title: "Hint policies on 23 typo cases", titleColor: HEX.text, titleFontSize: 13, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.text, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt",
    catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: HEX.line, size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendColor: HEX.muted, legendFontSize: 11, legendFontFace: "+mn-lt", valAxisMaxVal: 15, valAxisMinVal: 0, valAxisMajorUnit: 5, objectName: id("chart") });
  label(s, "Examples", 6.0, 1.15, 3);
  code(s, ["scroe → score   2 edits", "prnt  → print   1 edit", "mx    → max     1 edit"], 6.0, 1.45, 3.5, 1.15, { fontSize: 12 });
  panel(s, 6.0, 2.85, 3.5, 2.1, K.panel, K.green);
  text(s, [{ text: "Shipped rule", options: { bold: true, color: K.green, breakLine: true } },
    { text: "1 edit for names of up to 3 letters, 2 for longer names. Never suggest the word itself. Fewest wrong hints (6) with 12 right.", options: { color: K.text, fontSize: 13 } }],
    { x: 6.2, y: 2.95, w: 3.1, h: 1.9, fontSize: 15 });
}

// =====================================================================
divider("Tools and evaluation", "05", "Tools and evaluation", "A browser playground, an automated test suite, and a case study against gcc.");

// 19. Web playground
{
  const s = content("Tools and evaluation", "Seeing it work: the web playground",
    "make web starts web/server.py on port 8795, using only the Python standard library. POST /api/compile writes the source to a temp file and runs the real ./errorbuddy with --tokens and a 5-second timeout, then parses its text output into JSON: tokens, error, TAC, symbols and phases. The page recompiles about 350 ms after you stop typing, highlights the error line, and the phase strip shows where compilation stopped. Example buttons load the programs from examples/. Nothing is reimplemented in JavaScript.");
  s.addImage({ path: SHOT, x: 0.5, y: 1.15, w: 5.6, h: 3.34, altText: "ErrorBuddy web playground showing a missing-semicolon error on line 2 with the suggestion and the phase strip", objectName: id("img") });
  text(s, "make web  →  http://localhost:8795", { x: 0.5, y: 4.6, w: 5.6, h: 0.3, fontSize: 12, fontFace: MONO, color: K.green });
  const steps = [["Editor", "recompiles ~350 ms after typing stops"], ["POST /api/compile", "temp file → ./errorbuddy --tokens, 5 s timeout"],
    ["server.py", "regex turns stdout into JSON: tokens, error, TAC, symbols"], ["Page", "highlights the error line, lights the phase strip"]];
  steps.forEach(([hh, d], i) => {
    const y = 1.15 + i * 0.95;
    panel(s, 6.4, y, 3.1, 0.82);
    text(s, [{ text: hh, options: { bold: true, fontFace: MONO, color: K.coral, breakLine: true, fontSize: 12 } }, { text: d, options: { color: K.muted, fontSize: 12 } }],
      { x: 6.55, y, w: 2.85, h: 0.82, valign: "middle" });
    if (i < 3) arrow(s, 7.95, y + 0.82, 7.95, y + 0.95);
  });
}

// 20. Testing
{
  const s = content("Tools and evaluation", "Testing: make test",
    "make test runs every program in examples/ and diffs its output against examples/expected/*.out. One sample program per error type plus two valid programs. All 10 passed when this deck was built on 26 Oct 2026.");
  const tests = [["valid", "full program, 12 TAC instructions"], ["precedence", "b * 2 computed before +"], ["missing_semicolon", "reported on line 2, not 3"],
    ["undeclared_variable", "'marks' has not been declared"], ["duplicate_declaration", "'age' already declared on line 1"], ["invalid_expression", "two operators in a row"],
    ["incorrect_parentheses", "missing ')' for '(' on line 2"], ["extra_parenthesis", "extra ')' with no '('"], ["division_by_zero", "variable 'zero' is 0"], ["empty", "nothing to compile"]];
  tests.forEach(([t, d], i) => {
    const x = 0.5 + (i % 2) * 3.35, y = 1.15 + Math.floor(i / 2) * 0.76;
    panel(s, x, y, 3.2, 0.66);
    text(s, "PASS", { x: x + 0.12, y, w: 0.5, h: 0.66, fontSize: 11, bold: true, color: K.green, valign: "middle", fontFace: MONO });
    text(s, [{ text: t, options: { fontFace: MONO, fontSize: 11, breakLine: true } }, { text: d, options: { color: K.muted, fontSize: 11 } }],
      { x: x + 0.68, y, w: 2.45, h: 0.66, valign: "middle" });
  });
  panel(s, 7.3, 1.15, 2.2, 3.7);
  text(s, "10/10", { x: 7.3, y: 1.5, w: 2.2, h: 0.8, fontSize: 36, bold: true, color: K.green, align: "center", fontFace: MONO });
  text(s, "example programs match their expected output", { x: 7.45, y: 2.35, w: 1.9, h: 0.75, fontSize: 12, color: K.muted, align: "center" });
  text(s, "g++ -std=c++17\n-Wall -Wextra\n-pedantic -O2", { x: 7.45, y: 3.4, w: 1.9, h: 0.9, fontSize: 11, color: K.text, align: "center", fontFace: MONO });
}

// 21. Case study
{
  const s = content("Tools and evaluation", "Case study: reporting the fix line",
    "case_study/run_study.py runs 24 classic beginner mistakes through gcc 11.4 (the equivalent C, -Wall -Wextra, first diagnostic) and through two ErrorBuddy variants. Detection point reports the line where the parser noticed the problem; fix point, which is shipped, reports the previous token's line for a missing semicolon. gcc missed one case entirely: division by a variable that is 0. Its three late reports, and the detection-point variant's three, were all a missing semicolon.");
  s.addChart(pres.charts.BAR, [{ name: "Exact fix line", labels: ["gcc 11.4", "ErrorBuddy, detection point", "ErrorBuddy, fix point (shipped)"], values: [20, 21, 24] }],
    { x: 0.5, y: 1.15, w: 5.6, h: 3.8, barDir: "bar", chartColors: [HEX.muted, HEX.muted, HEX.green], invertedColors: [HEX.muted], showTitle: true, title: "Mistakes reported on the exact fix line (of 24)",
      titleColor: HEX.text, titleFontSize: 13, titleFontFace: "+mn-lt", showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.text, dataLabelFontSize: 12, dataLabelFontFace: "+mn-lt",
      catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
      valGridLine: { color: HEX.line, size: 0.5 }, catGridLine: { style: "none" }, showLegend: false, valAxisMaxVal: 25, valAxisMinVal: 0, valAxisMajorUnit: 5, objectName: id("chart") });
  const st = [["24/24", "mistakes caught by ErrorBuddy (gcc: 23)", K.green], ["0", "reports later than the fix line (gcc: 3)", K.green], ["3", "late gcc cases, all a missing ';'", K.coral]];
  st.forEach(([v, l, col], i) => {
    const y = 1.15 + i * 1.3;
    panel(s, 6.4, y, 3.1, 1.15);
    text(s, v, { x: 6.55, y: y + 0.12, w: 1.35, h: 0.9, fontSize: 24, bold: true, color: col, valign: "middle", fontFace: MONO });
    text(s, l, { x: 7.95, y: y + 0.12, w: 1.45, h: 0.9, fontSize: 12, color: K.muted, valign: "middle" });
  });
}

// 22. Lexer design choices
{
  const s = content("Tools and evaluation", "Lexer rules, tested by removal",
    "case_study/out_lexer.txt compares the shipped lexer with a variant that drops one rule. Without the comment rule, // becomes two slashes and the next line fails. Without the digit-then-letter rule, 2nd splits into 2 and nd and the message no longer names the real mistake. Without whole-word keyword matching, interest is read as int + erest.");
  const cases = [["// comments after '/'", "int a = 10 / 2; // half", "OK", "A statement cannot start with '/'."],
    ["No leading digit", "int 2nd = 5;", "'2nd' is not a valid name. Names cannot start with a digit.", "Expected a variable name after 'int', but found '2'."],
    ["Whole-word keywords", "int interest = 5;", "OK", "'int' is a reserved keyword and cannot be used as a variable name."]];
  cases.forEach(([h, src, ship, varr], i) => {
    const x = 0.5 + i * 3.07;
    panel(s, x, 1.2, 2.9, 3.75);
    text(s, h, { x: x + 0.2, y: 1.32, w: 2.55, h: 0.35, fontSize: 13, bold: true });
    code(s, [src], x + 0.15, 1.75, 2.6, 0.5, { fontSize: 11 });
    label(s, "Shipped", x + 0.2, 2.4, 2.5, K.green);
    text(s, ship, { x: x + 0.2, y: 2.65, w: 2.5, h: 0.85, fontSize: 12 });
    label(s, "Rule removed", x + 0.2, 3.55, 2.5, K.coral);
    text(s, varr, { x: x + 0.2, y: 3.8, w: 2.5, h: 1.0, fontSize: 12, color: K.muted });
  });
}

// =====================================================================
divider("Scope", "06", "Scope and conclusion", "What is built and tested today, and what the original proposal planned next.");

// 23. Built vs next
{
  const s = content("Scope", "Built today, and what comes next",
    "The original proposal targeted a beginner-C subset with if/else, while and for loops, comparison and logical operators and printf. What is implemented is a smaller language, int, arithmetic and print, so that every phase could be built completely and the error messages could be the focus. The right column is planned work, not built.");
  panel(s, 0.5, 1.15, 4.4, 3.8, K.panel, K.green);
  label(s, "Built and tested", 0.75, 1.3, 3, K.green);
  const built = ["int variables with a required starting value", "+ - * / with precedence and parentheses", "print any expression; // comments",
    "TAC, symbol table and phase summary", "Four-field errors with line-accurate hints", "Web playground and make test (10/10)"];
  text(s, built.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < built.length - 1 } })), { x: 0.75, y: 1.65, w: 4.0, h: 3.2, fontSize: 14, paraSpaceAfter: 6 });
  panel(s, 5.1, 1.15, 4.4, 3.8);
  label(s, "Next, from the proposal (not built)", 5.35, 1.3, 4, K.amber);
  const next = ["if / else, while and for loops", "Comparison and logical operators, printf", "Error recovery: several errors per run",
    "Functions and arrays; char and float", "Constant folding and other optimisations", "Assembly backend from TAC"];
  text(s, next.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < next.length - 1 } })), { x: 5.35, y: 1.65, w: 4.0, h: 3.2, fontSize: 14, color: K.muted, paraSpaceAfter: 6 });
}

// 24. Conclusion
{
  const s = pres.addSlide({ masterName: "EB_TITLE", sectionTitle: "Scope" });
  s.addText([{ text: "Error" }, { text: "Buddy", options: { color: K.coral } }], { placeholder: "title" });
  s.addText("A complete small compiler, lexer to three-address code, whose main contribution is errors that teach: the right line, plain words, and a concrete fix.", { placeholder: "body" });
  text(s, "Thank you", { x: 0.5, y: 3.95, w: 4.4, h: 0.4, fontSize: 18, italic: true, color: K.muted });
  label(s, "Try it", 5.4, 1.35, 3);
  code(s, [[{ text: "$ ", options: ok }, { text: "make test" }], [{ text: "$ ", options: ok }, { text: "make run FILE=examples/valid.txt" }],
    [{ text: "$ ", options: ok }, { text: "make web" }], "  → http://localhost:8795", [{ text: "$ ", options: ok }, { text: "python3 case_study/run_study.py" }]], 5.4, 1.65, 4.1, 2.1, { fontSize: 12 });
  s.addNotes("To recap: five phases in three C++ files, errors carried as one structured object, every one of 24 case-study mistakes reported on the line where the fix belongs, and 10 of 10 example programs passing. The commands on the right reproduce everything shown in this deck.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote " + OUT);
})();
