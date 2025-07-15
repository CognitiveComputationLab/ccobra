""" CCOBRA helper function.

"""

import copy

def convert_to_basic_types(elem):
    """ Converts an element to primitive types. If the element
    is a list, the inner elements will be converted instead.
    The preference order is bool > int > float > string.

    Parameters
    ----------
    elem : Object
        Element to convert.

    Returns
    -------
    Object
        Primitive object representing the given element.

    """
    if isinstance(elem, int):
        return elem
    if isinstance(elem, float):
        return elem
    if isinstance(elem, bool):
        return elem
    if isinstance(elem, list):
        return [convert_to_basic_types(x) for x in elem]

    elem = str(elem)
    if elem == "True":
        return True
    if elem == "False":
        return False
    
    try:
        result = int(elem)
        return result
    except ValueError:
        try:
            result = float(elem)
            return result
        except ValueError:
            return elem
            
def tuple_to_string(tuptup):
    """ Converts a tuple to its string representation. Uses different separators (';', '/', '|') for
    different depths of the representation.

    Parameters
    ----------
    tuptup : list
        Tuple to convert to its string representation.

    Returns
    -------
    str
        String representation of the input tuple.

    """

    def join_deepest(tup, sep=';'):
        """ Recursive function to create the string representation for the deepest level of the
        tuptup list.

        Parameters
        ----------
        tup : object
            Element to join if list or list of lists.

        sep : str, optional
            Separation character to join the list elements by.

        Returns
        -------
        object
            List containing joined string in max depth. Str if input depth = 1.

        """

        if not isinstance(tup, list):
            return str(tup)
        if not isinstance(tup[0], list):
            return sep.join([str(x) for x in tup])

        for idx, val in enumerate(tup):
            tup[idx] = join_deepest(val, sep)
        return tup

    tup = copy.deepcopy(tuptup)
    tup = join_deepest(tup, ';')
    tup = join_deepest(tup, '/')
    tup = join_deepest(tup, '|')
    return tup


def unnest(tup):
    """ Unnests a nested tuple. If an element is insight nested lists, the function
    returns the element, otherwise the list is returned.

    Parameters
    ----------
    tup : list
        Nested tuples.

    Returns
    -------
    object
        Element or list without unneccessary nesting.

    """
    while True:
        if not isinstance(tup, list):
            return tup
        if len(tup) != 1:
            return tup
        
        tup = tup[0]