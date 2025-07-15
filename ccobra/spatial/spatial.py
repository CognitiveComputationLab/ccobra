""" Spatial utils providing some predefined lists and functions.

"""

CARDINAL_DIRECTIONS = [
    'north', 'east', 'south', 'west'
]
"""str: List of the cardinal directions."""

#: List of the ordinal directions
ORDINAL_DIRECTIONS = [
    'north-east', 'north-west', 'south-east', 'south-west'
]

#: Dictionary mapping the relations to their opposites
OPPOSITES = {
    'right': 'left',
    'left': 'right',
    'up': 'down',
    'down': 'up',
    'north': 'south',
    'south': 'north',
    'west': 'east',
    'east': 'west',
    'north-east': 'south-west',
    'north-west': 'south-east',
    'south-east': 'north-west',
    'south-west': 'north-east'
}

#: Dictionary mapping combined relations to their components
CARDINAL_COMBINATIONS = {
    'north-east': set(['north', 'east']),
    'north-west': set(['north', 'west']),
    'south-east': set(['south', 'east']),
    'south-west': set(['south', 'west'])
}

def invert(statement):
    """ Inverts a given spatial statement (in list form).
    Thereby, the statement preserves its meaning, but uses the opposite
    relation. For example:
    ["left", "A", "B"] becomes ["right", "B", "A"].
    This can be useful to bring a set of statements in a unified form.

    Parameters
    ----------
    statement : list(str)
        The spatial statement in list form.

    Returns
    -------
    list(str)
        The inverted statement.

    """
    relation = statement[0].lower()
    obj_1 = statement[1]
    obj_2 = statement[2]
    if relation not in OPPOSITES:
        raise ValueError("No opposite found for '{}'".format(relation))
    else:
        return [OPPOSITES[relation], obj_2, obj_1]

def combine_cardinal_relations(card1, card2):
    """ Combines two cardinal relations. If the cardinal directions 
    do oppose each other, 'None' is returned. If they are the same,
    the same relation will be returned. Otherwise, they will be combined
    into an ordinal direction.
    For example:
    combine_cardinal_relations("north", "south") --> None
    combine_cardinal_relations("north", "north") --> "north"
    combine_cardinal_relations("north", "west") --> "north-west"

    Parameters
    ----------
    card1 : str
        The first cardinal direction

    card2 : str
        The second cardinal direction

    Returns
    -------
    str
        The combined relation (or None)

    """
    card1 = card1.lower()
    card2 = card2.lower()
    if card1 not in CARDINAL_DIRECTIONS:
        raise ValueError(f'{card1} is not a cardinal direction.')
    if card2 not in CARDINAL_DIRECTIONS:
        raise ValueError(f'{card2} is not a cardinal direction.')

    if OPPOSITES[card1] == card2:
        return None
    if card1 == card2:
        return card1

    for combination, components in CARDINAL_COMBINATIONS.items():
        if (card1 in components) and (card2 in components):
            return combination
    return None

def combine_ordinal_relations(ord1, ord2):
    """ Combines two ordinal relations. If the ordinal directions 
    do oppose each other, 'None' is returned. If they are the same,
    the same relation will be returned. Otherwise, they will be combined
    into an cardinal direction.
    For example:
    combine_ordinal_relations("north-west", "south-east") --> None
    combine_ordinal_relations("north-west", "north-west") --> "north-west"
    combine_ordinal_relations("north-west", "south-west") --> "west"

    Parameters
    ----------
    ord1 : str
        The first ordinal direction

    ord2 : str
        The second ordinal direction

    Returns
    -------
    str
        The combined relation (or None)

    """
    ord1 = ord1.lower()
    ord2 = ord2.lower()
    
    if ord1 not in ORDINAL_DIRECTIONS:
        raise ValueError(f'{ord1} is not an ordinal direction.')
    if ord2 not in ORDINAL_DIRECTIONS:
        raise ValueError(f'{ord2} is not an ordinal direction.')

    if OPPOSITES[ord1] == ord2:
        return None
    if ord1 == ord2:
        return ord1

    components1 = CARDINAL_COMBINATIONS[ord1]
    components2 = CARDINAL_COMBINATIONS[ord2]
    combination = components1.intersection(components2)
    if len(combination) == 1:
        return list(combination)[0]
    return None

def is_partially_equal(relation1, relation2):
    """ Tests if two relations are sharing a same component.
    For example, "south-east" and "south-west" share the partitial
    direction "south", and would therefore be partially equal.

    Parameters
    ----------
    relation1 : str
        The first relation

    relation2 : str
        The second relation

    Returns
    -------
    bool
        True, if both relations have a shared component

    """
    relation1 = relation1.lower()
    relation2 = relation2.lower()
    if relation1 == relation2:
        return True
    
    rel1_set = set()
    if relation1 in CARDINAL_COMBINATIONS:
        rel1_set = CARDINAL_COMBINATIONS[relation1]
    else:
        rel1_set.add(relation1)
    
    rel2_set = set()
    if relation2 in CARDINAL_COMBINATIONS:
        rel2_set = CARDINAL_COMBINATIONS[relation2]
    else:
        rel2_set.add(relation2)
    
    return len(rel1_set.intersection(rel2_set)) > 0