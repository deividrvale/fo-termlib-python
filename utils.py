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


def is_member(eq, x, list) -> bool:
    for y in list:
        if (eq(x,y) == True):
            return True
    return False


def remove_duplicates(eq, list):
    unique_list = []
    for y in list:
        if (is_member(eq, y, unique_list)):
            continue
        else:
            unique_list = unique_list + [y]
    return unique_list


def is_sublist(eq, list1, list2) -> bool:
    for x in list1:
        if not(is_member(eq, x, list2)):
            return False
    return True
