import z3

import trs
from term import Term, FnApp, FnSym
from trs import Rule, Trs
import term as tm
import lpo_solver as lpo

# As a test, let us encode the following system manually:
# f(x) -> x and g(f(x), y) -> f(y)

# The python encoding of this system is as follows:
# We first encodde the variables
x = tm.Var("x")
y = tm.Var("y")

# This system has two function symbols f : 1 and g : 2

f = FnSym("f", 1)
g = FnSym("g", 2)

sig = [f, g]

# Now we encode the first rule, f(x) -> x

fx = FnApp((f, [x]))

rule1 = trs.Rule(fx, x)

# Now we encode the second rule, g(f(x), y) -> f(y)
fy = FnApp((f, [y]))

rule2 = trs.Rule(FnApp((g, [fx, y])), fy)
