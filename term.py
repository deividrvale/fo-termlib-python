from __future__ import annotations
from dataclasses import dataclass
from utils import list_eq


@dataclass
class Var:
    name: str


@dataclass
class FnSym:
    name: str
    arity: int


@dataclass
class FnApp:
    fnApp: tuple[FnSym, list[Term]]


Term = Var | FnApp


def term_eq(s: Term, t: Term) -> bool:
    match (s, t):
        case (Var(x), Var(y)):
            return x == y
        case (Var(_), FnApp(_)):
            return False
        case (FnApp(_), Var(_)):
            return False
        case (FnApp(l), FnApp(r)):
            return (l[0] == r[0]) and list_eq(term_eq, l[1], r[1])
        case _:
            raise TypeError("Arguments to term_eq should be instances of Terms.")


def _tms_to_string(f, tms: list[Term]):
    if (len(tms)) == 0:
        return ""
    else:
        l = len(tms)
        args_strings = ""
        for i in range(l - 1):
            args_strings += f(tms[i]) + ","
        return args_strings + f(tms[l - 1])


def to_string(tm: Term) -> str:
    if not isinstance(tm, Term):
        raise TypeError("Argument of incorrect type, please supply an argument that is an instance of Term.")
    match tm:
        case Var(x):
            return x
        case FnApp((f, tms)):
            fn_name = f.name
            return fn_name + "(" + (_tms_to_string(to_string, tms)) + ")"



# x = Var("x")
# y = Var("y")
#
# f = FnSym("f", 2)
# g = FnSym("g", 2)
#
# s = FnApp((f, [x, x, x, y]))
# t = FnApp((f, [x]))
#
# print(to_string(s))