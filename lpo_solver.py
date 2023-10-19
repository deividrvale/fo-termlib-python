# from term import *
from term import Term, FnSym

import term as tm
import z3
import trs


# Name Generation -------------------------------------------------------------
def gen_gt_name(s: Term, t: Term) -> str:
    """
    Given two terms s and t, generates the string [s > t].
    """
    return "[" + tm.to_string(s) + ">" + tm.to_string(t) + "]"


def gen_gte_name(s: Term, t: Term) -> str:
    return "[" + tm.to_string(s) + ">=" + tm.to_string(t) + "]"


def gen_fn_pred_name(fn: FnSym) -> str:
    if not isinstance(fn, FnSym):
        raise TypeError("Precedence names should be given only to function symbols.\n"
                        f"The the argument is of type {type(fn)} "
                        f"while it should be an instance of <class 'term.FnSym'>.")
    return f"[Pred({str(fn)})]"


# Generation of z3 boolean variables ------------------------------------------

# The first step is to create boolean variables for each one of the subterms of l -> r.
# The value bool_vars below keeps track of those names.

z3_gt = {}
z3_gte = {}
z3_prec = {}


def gen_z3_gt_vars(ss: list[Term], ts: list[Term]):
    for s in ss:
        for t in ts:
            if tm.term_eq(s, t):
                z3_gt[(s, t)] = z3.BoolVal(False)
            else:
                z3_gt[(s, t)] = z3.Bool(gen_gt_name(s, t))
    print(z3_gt)


def gen_z3_gte_vars(ss: list[Term], ts: list[Term]):
    for s in ss:
        for t in ts:
            if tm.term_eq(s, t):
                z3_gte[(s, t)] = z3.BoolVal(True)
            else:
                z3_gte[(s, t)] = z3.Bool(gen_gte_name(s, t))
    print(z3_gte)


def gen_z3_prec_vars(fs: list[FnSym]):
    for f in fs:
        z3_prec[f] = z3.Int(gen_fn_pred_name(f))
    print(z3_prec)
