def list_eq(eq, xs: list, ys: list) -> bool:
    if len(xs) == len(ys):
        for i in range(len(xs)):
            if eq(xs[i], ys[i]):
                continue
            else:
                return False
        return True
    else:
        return False
