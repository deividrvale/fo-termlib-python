# from term import *
from term import Term
import term as tm


def gen_get_name(s: Term, t: Term) -> str:
    return "[" + tm.to_string(s) + ">" + tm.to_string(t) + "]"


def gen_geq_name(s: Term, t: Term) -> str:
    return "[" + tm.to_string(s) + "≥" + tm.to_string(t) + "]"
