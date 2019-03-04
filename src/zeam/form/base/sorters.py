def sort_components(order):

    if not isinstance(order, list) and not isinstance(order, tuple):
        raise ValueError(
            "Please provide a valid list or tuple of component identifiers.")

    if len(order) < 2:
        raise ValueError(
            "Please provide a list of, at least, two component identifiers.")

    order = tuple(order)

    def compare(c1, c2):
        """Compares according to the index in the order tuple.
        """
        try:
            o1 = order.index(c1.identifier)
        except ValueError:
            return 1

        try:
            o2 = order.index(c2.identifier)
        except ValueError:
            return -1

        if o1 > o2:
            return 1

        if o1 < o2:
            return -1

        return 0

    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return compare(self.obj, other.obj) < 0

        def __gt__(self, other):
            return compare(self.obj, other.obj) > 0

        def __eq__(self, other):
            return compare(self.obj, other.obj) == 0

        def __le__(self, other):
            return compare(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return compare(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return compare(self.obj, other.obj) != 0

    return K
