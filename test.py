from term import Term, FnApp, FnSym
from trs import Rule, Trs
import term as tm
import lpo_solver as lpo

x = tm.Var("x")
y = tm.Var("y")
g = FnApp((FnSym("g", 2), [x, x]))
f = FnApp((FnSym("f", 1), [x]))

rule = Rule(f, x)

print(tm.get_vars(g))

print(lpo.gen_fn_pred_name(f))
