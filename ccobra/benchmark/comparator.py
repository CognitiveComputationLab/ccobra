""" Contains different comparator classes for model output data structures.

"""

import copy

class Comparator():
    def compare(self, obj_a, obj_b):
        raise NotImplementedError()

def tuple_to_string(tuptup):
    def join_deepest(tup, sep=';'):
        if not isinstance(tup, list):
            return tup
        if not isinstance(tup[0], list):
            return sep.join(tup)
        else:
            for idx in range(len(tup)):
                tup[idx] = join_deepest(tup[idx], sep)
            return tup

    tup = copy.deepcopy(tuptup)
    tup = join_deepest(tup, ';')
    tup = join_deepest(tup, '/')

    # Sort the tuples
    tup = sorted(tup) if isinstance(tup, list) else tup

    tup = join_deepest(tup, '|')
    return tup

class EqualityComparator():
    def compare(self, obj_a, obj_b):
        return tuple_to_string(obj_a) == tuple_to_string(obj_b)

class NVCComparator():
    def compare(self, obj_a, obj_b):
        return ("NVC" == tuple_to_string(obj_a)) == ("NVC" == tuple_to_string(obj_b))
