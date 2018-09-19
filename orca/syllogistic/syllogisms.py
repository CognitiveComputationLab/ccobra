""" Functions for preparing lists of syllogisms and responses.

"""

_GLOBAL_MOODS = ['A', 'I', 'E', 'O']
_GLOBAL_SYLLOGISMS = None
_GLOBAL_RESPONSES = None

def get_syllogisms():
    """ Generates the list of syllogisms. Actual list generation is only
    performed once. Afterwards, cached lists are returned.

    Returns
    -------
    list(str)
        List containing the 64 syllogisms (AA1, AA2, ..., OO4) with ordering
        following the precedence A < I < E < O.

    """

    global _GLOBAL_SYLLOGISMS

    if _GLOBAL_SYLLOGISMS:
        return _GLOBAL_SYLLOGISMS

    syllogs = []
    for mood1 in _GLOBAL_MOODS:
        for mood2 in _GLOBAL_MOODS:
            for fig in range(1, 5):
                syllogs.append(mood1 + mood2 + str(fig))

    _GLOBAL_SYLLOGISMS = syllogs
    return _GLOBAL_SYLLOGISMS

def get_responses():
    """ Generates the list of responses to syllogisms. Actual list generation
    is only performed once. Afterwards, cached lists are returned.

    Returns
    -------
    list(str)
        List containing the nine valid answers to syllogistic reasoning
        problems. Order follows the precedence A < I < E < O < NVC, and
        ac < ca. Ex: Aac, Aca, Iac, Ica, ...

    """

    global _GLOBAL_RESPONSES

    if _GLOBAL_RESPONSES:
        return _GLOBAL_RESPONSES

    resps = []
    for mood in _GLOBAL_MOODS:
        for direction in ['ac', 'ca']:
            resps.append(mood + direction)
    resps.append('NVC')

    _GLOBAL_RESPONSES = resps
    return _GLOBAL_RESPONSES

def premise_text(quantifier, first, second):
    text = ''
    if quantifier == 'A':
        text = 'All {} are {}'
    elif quantifier == 'I':
        text = 'Some {} are {}'
    elif quantifier == 'E':
        text = 'No {} are {}'
    elif quantifier == 'O':
        text = 'Some {} are not {}'
    else:
        raise ValueError('Invalid premise quantifier')

    return text.format(first, second)

def syllog_text(task, placeholders):
    figure = int(task[2])

    # Generate the task text
    premise1 = None
    premise2 = None
    if figure == 1:
        premise1 = premise_text(task[0], placeholders[0], placeholders[1])
        premise2 = premise_text(task[1], placeholders[1], placeholders[2])
    elif figure == 2:
        premise1 = premise_text(task[0], placeholders[1], placeholders[0])
        premise2 = premise_text(task[1], placeholders[2], placeholders[1])
    elif figure == 3:
        premise1 = premise_text(task[0], placeholders[0], placeholders[1])
        premise2 = premise_text(task[1], placeholders[2], placeholders[1])
    elif figure == 4:
        premise1 = premise_text(task[0], placeholders[1], placeholders[0])
        premise2 = premise_text(task[1], placeholders[1], placeholders[2])
    else:
        raise ValueError('Invalid figure.')

    return '{};{}'.format(premise1, premise2)

def response_text(response, placeholders):
    if response[2:] == 'ac':
        return premise_text(response[0], placeholders[0], placeholders[2])
    elif response[2:] == 'ca':
        return premise_text(response[0], placeholders[2], placeholders[0])

    return 'No Valid Conclusion'
