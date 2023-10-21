from dataclasses import dataclass
from term import Term, FnApp, FnSym, Var
import term as tm
import utils


def to_string(lhs, rhs) -> str:
    return tm.to_string(lhs) + " -> " + tm.to_string(rhs)


@dataclass
class Rule:
    lhs: Term
    rhs: Term

    def __init__(self, lhs: Term, rhs: Term):
        if tm.is_var(lhs):
            raise TypeError(
                "The lhs of the rule " +
                to_string(lhs, rhs) +
                " is of type variable."
            )
        vars_lhs = tm.get_vars(lhs)
        if not utils.is_sublist(tm.term_eq, tm.get_vars(rhs), vars_lhs) and len(vars_lhs) > 0:
            raise TypeError(
                "The rule " +
                to_string(lhs, rhs) +
                " is not valid." +
                " Recall that every variable in the (rhs) should also occur in the (lhs)."
            )
        self.lhs = lhs
        self.rhs = rhs


@dataclass
class Trs:
    vars: list[Var]
    signature: list[FnSym]
    rules: list[Rule]
