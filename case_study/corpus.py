# corpus.py - the hand-labelled mistake corpus for the line-placement study.
#
# Each case is one beginner mistake written twice: in ErrorBuddy's language
# ("eb") and as the equivalent C statements ("c"), which run_study.py wraps in
# main() so gcc can compile them. "fix" is the line the student has to edit,
# decided by hand BEFORE any reporter was run. "hint" is the name a
# "Did you mean" hint should offer (None if no hint is expected).

CASES = [
    dict(id="M01", name="missing ; (next line is print)", fix=2, eb="""int a = 5;
int b = 10
print a + b;""", c="""int a = 5;
int b = 10
printf("%d\\n", a + b);"""),

    dict(id="M02", name="missing ; (blank line + comment after)", fix=2, eb="""int a = 5;
int b = 10

// show the total
print a + b;""", c="""int a = 5;
int b = 10

// show the total
printf("%d\\n", a + b);"""),

    dict(id="M03", name="missing ; (next line is assignment)", fix=2, eb="""int a = 5;
int b = 10
b = b + a;
print b;""", c="""int a = 5;
int b = 10
b = b + a;
printf("%d\\n", b);"""),

    dict(id="M04", name="missing ; on last statement", fix=3, eb="""int a = 5;
int b = a * 2;
print b""", c="""int a = 5;
int b = a * 2;
printf("%d\\n", b)"""),

    dict(id="M05", name="missing )", fix=2, eb="""int x = 2;
int y = (x + 3 * 4;
print y;""", c="""int x = 2;
int y = (x + 3 * 4;
printf("%d\\n", y);"""),

    dict(id="M06", name="missing ) (expression split over lines)", fix=3, eb="""int x = 2;
int y = (x +
    3 * 4;
print y;""", c="""int x = 2;
int y = (x +
    3 * 4;
printf("%d\\n", y);"""),

    dict(id="M07", name="extra )", fix=2, eb="""int a = 5;
int b = (a + 2)) * 3;
print b;""", c="""int a = 5;
int b = (a + 2)) * 3;
printf("%d\\n", b);"""),

    dict(id="M08", name="two operators in a row", fix=2, eb="""int x = 4;
int y = x + * 3;
print y;""", c="""int x = 4;
int y = x + * 3;
printf("%d\\n", y);"""),

    dict(id="M09", name="operator with no right operand", fix=2, eb="""int x = 4;
int y = x + ;
print y;""", c="""int x = 4;
int y = x + ;
printf("%d\\n", y);"""),

    dict(id="M10", name="missing operator between values", fix=3, eb="""int a = 2;
int b = 3;
int c = a b;
print c;""", c="""int a = 2;
int b = 3;
int c = a b;
printf("%d\\n", c);"""),

    dict(id="M11", name="missing value after =", fix=2, eb="""int a = 1;
int b = ;
print a;""", c="""int a = 1;
int b = ;
printf("%d\\n", a);"""),

    dict(id="M12", name="empty parentheses", fix=2, eb="""int a = 1;
int b = a * ();
print b;""", c="""int a = 1;
int b = a * ();
printf("%d\\n", b);"""),

    dict(id="M13", name="undeclared variable", fix=2, eb="""int total = 50;
total = total + marks;
print total;""", c="""int total = 50;
total = total + marks;
printf("%d\\n", total);"""),

    dict(id="M14", name="misspelled variable", fix=3, hint="score", eb="""int score = 10;
int bonus = 5;
scroe = score + bonus;
print score;""", c="""int score = 10;
int bonus = 5;
scroe = score + bonus;
printf("%d\\n", score);"""),

    dict(id="M15", name="misspelled print keyword", fix=2, hint="print", eb="""int x = 3;
prnt x;""", c="""int x = 3;
prinft("%d\\n", x);"""),

    dict(id="M16", name="duplicate declaration", fix=4, eb="""int age = 18;
int year = 2026;
print age;
int age = 19;""", c="""int age = 18;
int year = 2026;
printf("%d\\n", age);
int age = 19;"""),

    dict(id="M17", name="variable used in its own declaration", fix=1, eb="""int a = a + 1;
print a;""", c="""int a = a + 1;
printf("%d\\n", a);"""),

    dict(id="M18", name="division by literal 0", fix=2, eb="""int a = 10;
int b = a / 0;
print b;""", c="""int a = 10;
int b = a / 0;
printf("%d\\n", b);"""),

    dict(id="M19", name="division by a variable that is 0", fix=3, eb="""int a = 10;
int zero = a - 10;
int b = a / zero;
print b;""", c="""int a = 10;
int zero = a - 10;
int b = a / zero;
printf("%d\\n", b);"""),

    dict(id="M20", name="division by an expression that is 0", fix=1, eb="""int a = 8 / (4 - 4);
print a;""", c="""int a = 8 / (4 - 4);
printf("%d\\n", a);"""),

    dict(id="M21", name="arithmetic overflow", fix=1, eb="""int big = 2000000000 * 2;
print big;""", c="""int big = 2000000000 * 2;
printf("%d\\n", big);"""),

    dict(id="M22", name="literal too large for int", fix=1, eb="""int n = 99999999999;
print n;""", c="""int n = 99999999999;
printf("%d\\n", n);"""),

    dict(id="M23", name="unknown symbol", fix=2, eb="""int a = 5;
int b = a @ 2;
print b;""", c="""int a = 5;
int b = a @ 2;
printf("%d\\n", b);"""),

    dict(id="M24", name="name starts with a digit", fix=1, eb="""int 2nd = 5;
print 2nd;""", c="""int 2nd = 5;
printf("%d\\n", 2nd);"""),
]
