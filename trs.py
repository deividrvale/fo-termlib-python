from dataclasses import dataclass
from term import Term
import term as tm


def to_string(lhs, rhs) -> str:
    return tm.to_string(lhs) + " -> " + tm.to_string(rhs)


@dataclass
class Rule:
    lhs: Term
    rhs: Term

    def __init__(self, lhs: Term, rhs: Term):
        if tm.is_var(lhs):
            raise TypeError("The lhs of the rule " + to_string(lhs, rhs) + " is of type variable.")


x = tm.Var("x")
y = tm.Var("y")

rule = Rule(x, y)
