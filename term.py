from __future__ import annotations
from dataclasses import dataclass
from types import UnionType
from utils import list_eq, remove_duplicates
import functools


@dataclass
class Var:
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(str(self))


@dataclass
class FnSym:
    name: str
    arity: int

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(str(self))


@dataclass
class FnApp:
    fnApp: tuple[FnSym, list[Term]]

    def __init__(self, app: tuple[FnSym, list[Term]]):
        match app:
            case (FnSym(f, ar), args):
                if ar == len(args):
                    self.fnApp = (FnSym(f, ar), args)
                else:
                    raise TypeError(
                        "Invalid functional application!" +
                        f" The arity of {f} is {str(ar)}" +
                        f" but it is being applied to {str(len(args))}."
                    )
            case x:
                raise TypeError(
                    "Invalid term construction."
                    " Expected type is tuple[FnSym, list[Term]]" +
                    f" supplied argument type is {type(x)}."
                )

    def __str__(self):
        return to_string(self)

    def __repr__(self):
        return to_string(self)

    def __hash__(self):
        return hash(str(self))


Term: UnionType = Var | FnApp


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


def is_var(tm: Term) -> bool:
    match tm:
        case (Var(_)):
            return True
        case _:
            return False


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
        raise TypeError(f"The argument is of type {type(tm)} while it should be of type Term.")
    match tm:
        case Var(x):
            return x
        case FnApp(((FnSym(f, _)), [])):
            return f
        case FnApp((f, tms)):
            fn_name = f.name
            return f"{f.name}({_tms_to_string(to_string, tms)})"


def get_vars(tm: Term) -> list[Term]:
    def _get_vars(t: Term):
        match t:
            case Var(x):
                return [Var(x)]
            case FnApp((_, tms)):
                return functools.reduce(
                    list.__add__,
                    map(_get_vars, tms),
                    []
                )
    return remove_duplicates(term_eq, _get_vars(tm))


def get_subterms(tm: Term) -> list[Term]:
    def _get_subterms(t: Term):
        match t:
            case Var(x):
                return [Var(x)]
            case FnApp((f, tms)):
                return functools.reduce(
                    list.__add__,
                    ([[FnApp((f, tms))]] + list(map(_get_subterms, tms))),
                    []
                )
    return remove_duplicates(term_eq, _get_subterms(tm))
