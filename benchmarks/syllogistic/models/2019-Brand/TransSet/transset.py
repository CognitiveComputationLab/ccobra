""" TransSet model implementation.

"""

import ccobra


def atmosphere_predictions(premises):
    """ Produces atmosphere predictions to a given tuple of premises.

    Parameters
    ----------
    premises : list(str)
        List of premises (e.g., 'AA').

    Returns
    -------
    list(str)
        List of atmosphere predictions (e.g., ['Aac', 'Aca'])

    """

    responses = []
    if premises == 'AA':
        responses = ['Aac', 'Aca']
    elif premises == 'AI':
        responses = ['Iac', 'Ica']
    elif premises == 'AE':
        responses = ['Eac', 'Eca']
    elif premises == 'AO':
        responses = ['Oac', 'Oca']
    elif premises == 'EE':
        responses = ['Eac', 'Eca']
    elif premises == 'EI':
        responses = ['Oac', 'Oca']
    elif premises == 'EO':
        responses = ['Oac', 'Oca']
    elif premises == 'II':
        responses = ['Iac', 'Ica']
    elif premises == 'IO':
        responses = ['Oac', 'Oca']
    elif premises == 'OO':
        responses = ['Oac', 'Oca']
    return responses

def generate_prediction(figure, first, second):
    """ Generates predictions according the the TransSet theory.

    """

    neg_quantifiers = ['E', 'O']

    # DETERMINE THE DIRECTION

    # Figure 3 and 4: There is no clear path to process a set of As to the
    # endpoint of Cs. Therefore, different heuristics are used to find a
    # direction. The quantifiers are ranked according to the ability to choose
    # a set with high confidence (therefore all > none > (some/somenot))
    ordering = { 'A' : 3, 'E' : 2, 'I' : 1, 'O' : 1}

    # For figure 3 (where all paths point to B), the side with the 'more
    # informative' set is assumed to be the endpoint (e.g., "some A" and "all C", it is
    # reasonable to assume that the answer has to be a mapping from A to C, so
    # ac is the direction). For ties: NVC, as it is unclear which set is a subset of the other.
    if figure == '3':
        if ordering[second] > ordering[first]:
            figure = '1'
        elif ordering[second] < ordering[first]:
            figure = '2'
        else:
            return "NVC"

    # Figure 4 (all paths start from B) it is the other way round: the 'more
    # informative' set determines the starting point. As the premise starts with B, the
    # more informative set is a natural choice to be filtered by B, before the second premise
    # is applied.
    if figure == '4':
        if ordering[first] > ordering[second]:
            figure = '1'
        elif ordering[first] < ordering[second]:
            figure = '2'
        else:
            return "NVC"
    dir = 'ac'

    # The direction in fig 1 ist ac, in fig 2 it is ca. Therefore the premise
    # order can also be changed.
    if figure == '1':
        dir = 'ac'
    elif figure == '2':
        dir = 'ca'
        tmp = first
        first = second
        second = tmp

    # DETERMINE THE QUANTIFIER

    # It is assumed that the confidence in a path depends on the non-negative
    # quantifiers. The first premise is more important, as it is used in the
    # second premise to find the answer. therefore, a negative quantifier
    # in the first premise should increase the likelyhood of NVC more than a
    # negative quantifier in the second premise. Especially syllogisms with two
    # negative quantifiers will most likely be considered NVC
    if (first in neg_quantifiers) and not(second == 'A'):
        return "NVC"

    # After this pre-filtering, the atmosphere is used for the rest, as the set-based
    # approach is compatible with it's results.
    premises = ''.join(sorted([first, second]))
    atmosphere_prediction = atmosphere_predictions(premises)

    # The figure determines the direction
    direction_idx = 0 if (dir == 'ac') else 1
    return atmosphere_prediction[direction_idx]

class TransitivitySet(ccobra.CCobraModel):
    """ TransitivitySet CCOBRA implementation.

    """

    def __init__(self, name='TransSet'):
        """ Initializes the TransitivitySet model.

        Parameters
        ----------
        name : str
            Unique name of the model. Will be used throughout the ORCA
            framework as a means for identifying the model.

        """

        super(TransitivitySet, self).__init__(name, ['syllogistic'], ['single-choice'])


    def predict(self, item, **kwargs):
        """ Predicts weighted responses to a given syllogism.

        """

        # Obtain the syllogistic task encoding
        syl = ccobra.syllogistic.Syllogism(item)
        syllogism = syl.encoded_task
        figure = syllogism[2]
        first = syllogism[0]
        second = syllogism[1]

        # Generate and return the current prediction
        pred = generate_prediction(figure, first, second)
        return syl.decode_response(pred)
