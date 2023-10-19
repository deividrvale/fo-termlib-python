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
                        f"The the argument is of type {type(fn)} while it should be an instance of <class 'term.FnSym'>.")
    return f"[Pred({str(fn)})]"

# Generation of z3 boolean variables ------------------------------------------

# The first step is to create boolean variables for each one of the subterms of l -> r.
# The value bool_vars below keeps track of those names.

def gen_boolean_vars(ss : list[Term], ts: list[Term]) -> object:


# class Solver:
#     sig: list[FnSym]
#     trs: trs.Trs
