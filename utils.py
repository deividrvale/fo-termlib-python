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


def is_member(eq, x, xs: list) -> bool:
    for y in xs:
        if eq(x, y) is True:
            return True
    return False


def remove_duplicates(eq, xs):
    unique_list = []
    for y in xs:
        if is_member(eq, y, unique_list):
            continue
        else:
            unique_list += [y]
    return unique_list


def is_sublist(eq, xs, ys) -> bool:
    for x in xs:
        if not (is_member(eq, x, ys)):
            return False
    return True
