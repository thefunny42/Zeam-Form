# -*- coding: utf-8 -*-

def sort_components(order):
    if not isinstance(order, list) and not isinstance(order, tuple):
        raise ValueError(
            "Please provide a valid list or tuple of component identifiers.")
    if len(order) < 2:
        raise ValueError(
            "Please provide a list of, at least, two component identifiers.")

    def compare(c1, c2, order=order):

        try: o1 = order.index(c1)
        except ValueError: return 1

        try: o2 = order.index(c2)
        except ValueError: return -1

        if o1 - o2 > 1: return 1
        if o1 - o2 < 1: return -1

        return 0

    return compare
