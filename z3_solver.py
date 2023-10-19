from z3 import *


x = Bool("x")
y = Bool("y")

solver = Solver()

solver.add(And(x, y), Not(y))
print(solver.check())

# def get_solver_status():
#     match solver.check():
#         case sat:
#             return None
#         case unsat:
#             return None
#         case unknown:
#             return None


print(model[x])
