from term import Term, FnSym, Var, FnApp
from trs import Trs

import term as tm
import z3
import trs
import itertools


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
    # Since >= is just the union of syntactical equality and >, we do NOT use this:
    #   z3_gte[(s, t)] = z3.Bool(gen_gte_name(s, t))
    # as then we would have to create a defining formula for z3_gte[(s,t)] too.
    # Instead, we just use this:
    if tm.term_eq(s, t):
        z3_gte[(s, t)] = z3.BoolVal(True)
    else:
        z3_gte[(s, t)] = z3.Bool(gen_gt_name(s, t))


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
            # Variables are not greater than anything.
            solver.add(z3.Not(z3_gt[(u, v)]))
        case (FnApp((_, args_u)), Var(_)):
            # When u = f(u_1, ..., u_n) and v is a variable,
            # we add the constraint: [u > v] -> ([u_1 >= v] \/ ... \/ [u_n >= v]).
            # Form the disjunctions with the u_i's.
            or_exprs = z3.Or(list(map(lambda x: z3_gte[(x, v)], args_u)))
            # And add the implication formula to the solver.
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
            #              (/\_{j = i + 1}^n [u > v_j])) )
            # In order to determine this smallest index i
            # such that u_i in args_u and v_i in args_v are different,
            # we count the indexes such that u_i == v_i is true.
            # Then the next index is the one such that u_i == v_i is false.
            min_index = 0
            for u_i, v_i in zip(args_u, args_v):
                if tm.term_eq(u_i, v_i):
                    min_index += 1
                else:
                    break
            # Now, if no such i exists, it means that all arguments are equal,
            # so u and v are equal, so certainly not u > v.
            # Notice that this only happens whenever min_index is exactly
            # equal to the length of the lists.
            if min_index == len(args_u):
                solver.add(z3.Not(z3_gt[(u, v)]))
            else:
                # In this case, we have to generate the expression:
                # [u > v] -> (
                #               ([u_1 >= v] \/ ... \/ [u_n >= v]) \/
                #               ([u_i > v_i] /\ [u > v_{i + 1}] /\ ... /\ [u > v_n]) )
                u_i = args_u[min_index]
                v_i = args_v[min_index]
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
            solver.add(z3.Not(z3_gt[(u, v)]))
        case _:
            raise TypeError("No matching...")


def gen_z3_ctrs(s: Term, t: Term):
    # We first collect all subterms u of s and all subterms v of t, and generate
    # variables [u > v]
    subtm_s = tm.get_subterms(s)
    subtm_t = tm.get_subterms(t)
    for (u, v) in list(itertools.product(subtm_s,subtm_t)):
        gen_z3_gt(u, v)
        gen_z3_gte(u, v)
    # We require that [s > t] holds:
    solver.add(z3_gt[(s, t)])
    # Finally, we generate constraints over each subterm u of s and v of t,
    # creating a defining formula for each variable [u > v].
    # Those constraints are added to the solver we created earlier.
    for u in subtm_s:
        for v in subtm_t:
            _gen_z3_ctrs(u, v)


def print_precedence(model, sig):
    pred = [ (f, 0) for f in sig if f not in z3_prec ] +\
           [ (f, model.evaluate(z3_prec[f], model_completion=True).as_long()) for f in z3_prec ]
    pred.sort(reverse=True, key=lambda x:x[1])
    print("Precedence: ", end='')
    for i in range(len(pred)):
        if i > 0:
          if pred[i-1][1] > pred[i][1]: print(' > ', end='')
          else: print(' = ', end='')
        print(str(pred[i][0]), end='')
    print()


def print_inequalities(model, rules):
    pairsperrule = [ list(itertools.product(tm.get_subterms(s),tm.get_subterms(t))) for (s,t) in rules ]
    pairs = list(set([ pair for sublist in pairsperrule for pair in sublist ]))
    pairs.sort(key=lambda a:(len(str(a[0])), len(str(a[1]))), reverse=True)
    pairs = [ (u,v) for (u,v) in pairs if model.evaluate(z3_gt[(u,v)], model_completion=True) ]
    for pairindex in range(len(pairs)):
        (u,v) = pairs[pairindex]
        if (u,v) in rules: print("(RULE) ", end='')
        else: print("       ", end='')
        print(str(pairindex) + ". " + str(u) + " > " + str(v) + " by ", end='')
        match (u,v):
            case ( Var(_), _):
                print("ERROR")
                continue
            case ( FnApp((f, args_u)), Var(_) ):
                leftroot = f
                leftargs = args_u
                rightroot = None
                rightargs = []
            case ( FnApp((f, args_u)), FnApp((g, args_v)) ):
                leftroot = f
                leftargs = args_u
                rightroot = g
                rightargs = args_v
        if v in leftargs:
            print("ARG because " + str(v) + " >= " + str(v) + ".")
            continue
        u_i = next((arg for arg in leftargs if (arg,v) in pairs[pairindex+1:]), None)
        if u_i != None:
            j = pairs.index((u_i,v))
            print("ARG because " + str(j) + ".")
            continue
        if rightroot == None:
            print("ERROR")
            continue
        if leftroot == rightroot and len(leftargs) == len(rightargs) and leftargs != rightargs:
            print("LEX because ", end='')
            index = next(i for i in range(len(leftargs)) if leftargs[i] != rightargs[i])
            needed = [ (leftargs[index], rightargs[index]) ] +\
                     [ (u, rightargs[i]) for i in range(index+1, len(rightargs)) ]
            reasons = [ str(pairs.index(p)) if p in pairs else "ERROR" + str(p[0]) + ">" + str(p[1]) for p in needed]
            print(", ".join(reasons))
            continue
        if rightroot != None and model.evaluate(z3_prec[leftroot]).as_long() > model.evaluate(z3_prec[rightroot]).as_long():
            print("COPY because " + str(f) + " > " + str(g) + " and ", end='')
            needed =  [ (u, v_i) for v_i in rightargs ]
            reasons = [ str(pairs.index(p)) if p in pairs else "ERROR" + str(p[0]) + ">" + str(p[1]) for p in needed]
            print(", ".join(reasons))
            continue
        print("ERROR")


def print_proof(model, trs : Trs):
    print_precedence(model, trs.signature)
    print_inequalities(model, [ (r.lhs, r.rhs) for r in trs.rules ])


def prove_termination(trs: Trs):
    # Generate variables and requirements
    gen_z3_prec_vars(trs.signature)
    for r in trs.rules:
        gen_z3_ctrs(r.lhs, r.rhs)

    # See what the SMT solver says!
    match solver.check():
        case z3.sat:
            print("YES (term Rewriting System is terminating by LPO)")
            print_proof(solver.model(), trs)
        case z3.unsat:
            print("MAYBE (no solution possible with LPO)")
            exit()
        case z3.unknown:
            print("MAYBE (SAT solver could not determine if an LPO solution exists)")
            exit()
        case _:
            raise TypeError("Argument is not an instance of <class Solver>.")
