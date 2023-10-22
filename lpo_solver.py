from term import Term, FnSym, Var, FnApp
from trs import Trs

import term as tm
import z3
import trs


# Name Generation -------------------------------------------------------------
def gen_gt_name(s: Term, t: Term) -> str:
    """
    Given two terms s and t, generates the string [s > t].
    """
    if not isinstance(s, Term) and isinstance(t, Term):
        raise TypeError(f"The arguments is of type {type(s)} and {type(t)} "
                        f"while they should be of type <class tm.Term>")
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


def gen_z3_gt(s: Term, t: Term) -> None:
    z3_gt[(s, t)] = z3.Bool(gen_gt_name(s, t))


def gen_z3_gte(s: Term, t: Term) -> None:
    if tm.term_eq(s, t):
        z3_gte[(s, t)] = z3.BoolVal(True)
    else:
        z3_gte[(s, t)] = z3.Bool(gen_gte_name(s, t))


def gen_z3_prec_vars(fs: list[FnSym]) -> None:
    for f in fs:
        z3_prec[f] = z3.Int(gen_fn_pred_name(f))


# Adding constraints over those variables -------------------------------------
solver = z3.Solver()


def _gen_z3_ctrs(u: Term, v: Term):
    if not isinstance(u, Term) and isinstance(v, Term):
        raise TypeError(f"The arguments provided are of type {type(u)} "
                        f"and {type(v)} "
                        f"while they should be of type <class tm.Term>")
    match (u, v):
        case (Var(_), _):
            gen_z3_gt(u, v)
            solver.add(z3.Not(z3_gt[(u, v)]))
        case (FnApp((_, args_u)), Var(_)):
            # When u = f(u_1, ..., u_n) and v is a variable,
            # we add the constraint:
            # [u > v] -> ([u_1 >= v] \/ ... \/ [u_n >= v]).
            # Generate the [u > v] z3 variable.
            gen_z3_gt(u, v)
            # Generate the [u_i >= v] z3 variables.
            for x in args_u:
                gen_z3_gte(x, v)
            # Form the disjunctions with the u_i's.
            or_exprs = z3.Or(list(map(lambda x: z3_gte[(x, v)], args_u)))
            # We then finally add the implication formula to the solver.
            solver.add(z3.Implies(
                z3_gt[u, v],
                or_exprs
            ))
        case (FnApp((f, args_u)), FnApp((g, args_v))) if f == g and len(args_u) == len(args_v) > 0:
            # Let i be the smallest index 0 <= i < n such that u_i != v_i.
            # We will compute this index below.
            # For this case, the formula we need to add is the following:
            # [u > v] -> (
            #              (\/_i [u_i >= v]) \/
            #              ([u_i > v_i] /\
            #              (/\_{j = i + 1}^n [u > v_j]
            # In order to determine this smallest index i
            # such that u_i in args_u and v_i in args_v are different,
            # we count the indexes such that u_i == v_i is true.
            # Then the next index is the one such that u_i == v_i is false.
            min_index = 0
            for u_i, v_i in zip(args_u, args_v):
                if tm.term_eq(u_i, v_i):
                    min_index += 1
                    continue
                else:
                    break
            # Now, if no such i exists, it means that all arguments are equal.
            # Notice that this only happens whenever min_index is exactly
            # equal to the length of the lists.
            if min_index == len(args_u):
                gen_z3_gt(u, v)
                solver.add(z3_gt[(u, v)])
            else:
                # In this case, we have to generate the expression:
                # [u > v] -> (
                #               ([u_1 >= v_1] \/ ... \/ [u_n >= v_n]) \/
                #               ([u_i > v_i] /\ [u > v_{i + 1}] /\ ... /\ [u > v_n])
                # To do this we generate the gt and gte variables first.
                gen_z3_gt(u, v)
                u_i = args_u[min_index]
                v_i = args_v[min_index]
                gen_z3_gt(u_i, v_i)
                for x in args_v[(min_index + 1):]:
                    gen_z3_gt(u, x)
                for x in args_u:
                    gen_z3_gte(x, v)
                or_exprs = z3.Or(list(map(lambda x: z3_gte[(x, v)], args_u)))
                and_exprs = z3.And((
                        [z3_gt[(u_i, v_i)]] +
                        list(map(lambda x: z3_gt[u, x], args_v[(min_index + 1):]))
                ))
                solver.add(z3.Implies(
                    z3_gt[(u, v)],
                    z3.Or(
                        or_exprs,
                        and_exprs
                    )
                ))
        case (FnApp((f, args_u)), FnApp((g, args_v))) if (not f == g):
            gen_z3_gt(u, v)
            gen_z3_prec_vars([f, g])
            for u_i in args_u:
                gen_z3_gte(u_i, v)
            for v_i in args_v:
                gen_z3_gt(u, v_i)
            or_exprs = z3.Or(list(map(lambda x: z3_gte[(x, v)], args_u)))
            and_exprs = z3.And((
                    [z3_prec[f] > z3_prec[g]] +
                    list(map(lambda x: z3_gt[(u, x)], args_v))
            ))
            solver.add(z3.Implies(
                z3_gt[(u, v)],
                z3.Or(
                    or_exprs,
                    and_exprs
                )
            ))
        case (_, _) if tm.term_eq(u, v):
            gen_z3_gt(u, v)
            solver.add(z3.Not(z3_gt[(u, v)]))
        case _:
            raise TypeError("No matching...")


def gen_z3_ctrs(s: Term, t: Term):
    # We require that [s > t] holds:
    gen_z3_gt(s, t)
    solver.add(z3_gt[(s, t)])
    # Then we collect all subterms of s and all subterms of t.
    subtm_s = tm.get_subterms(s)
    subtm_t = tm.get_subterms(t)
    # Finally, we generate constraints over each subterm u of s and v of t.
    # Those constraints are added to the solver we created earlier.
    for u in subtm_s:
        for v in subtm_t:
            _gen_z3_ctrs(u, v)


def prove_termination(trs: Trs):
    for r in trs.rules:
        gen_z3_ctrs(r.lhs, r.rhs)
    match solver.check():
        case z3.sat:
            print("Term Rewriting System is terminating.")
            print(solver.model())
        case z3.unsat:
            print("MAYBE")
            exit()
        case z3.unknown:
            print("MAYBE")
            exit()
        case _:
            raise TypeError("Argument is not an instance of <class Solver>.")
