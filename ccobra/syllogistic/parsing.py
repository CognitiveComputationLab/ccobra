""" Collection of syllogistic helper functions.

"""

def get_syllogisms():
    """ Generates a list of syllogistic task identifiers.

    Returns
    -------
    list(str)
        List of syllogistic task identifiers, i.e., ['AA1', 'AA2', ...]. Order
        of precedence is A < I < E < O.

    """

    syllogisms = []
    for prem1 in ['A', 'I', 'E', 'O']:
        for prem2 in ['A', 'I', 'E', 'O']:
            for fig in ['1', '2', '3', '4']:
                syllogisms.append(prem1 + prem2 + fig)
    return syllogisms

def get_responses():
    """ Generates a list of syllogistic response identifiers.

    Returns
    -------
    list(str)
        List of syllogistic response identifiers, i.e., ['Aac', 'Aca', 'Iac',
        ...]. Order of precedence is A < I < E < O. No valid conclusion is
        added as 'NVC' to the end of the list.

    """

    responses = []
    for quant in ['A', 'I', 'E', 'O']:
        for direction in ['ac', 'ca']:
            responses.append(quant + direction)
    responses.append('NVC')
    return responses

def encode_task(task_tuple):
    """ Encodes a syllogistic task by transforming a task tuple string into
    its corresponding identifier.

    Parameters
    ----------
    task_tuple : str
        Task tuple string (e.g., 'All;pilots;gardeners/Some;gardeners;cooks').

    Returns
    -------
    str
        Syllogistic task identifier (e.g., 'AI1'). Figures are defined in
        accordance to Khemlani et al. (2012).

    """

    p1, p2 = [x.split(';') for x in task_tuple.split('/')]

    quant1 = p1[0].replace('All', 'A').replace(
        'Some not', 'O').replace('Some', 'I').replace('No', 'E')
    quant2 = p2[0].replace('All', 'A').replace(
        'Some not', 'O').replace('Some', 'I').replace('No', 'E')
    figure = 1
    if p1[1] == p2[1]:
        figure = 3
    elif p1[2] == p2[1]:
        figure = 1
    elif p1[2] == p2[2]:
        figure = 4
    elif p1[1] == p2[2]:
        figure = 2
    else:
        raise ValueError('Could not determine figure of:', task_tuple)

    return quant1 + quant2 + str(figure)

def encode_response(tuptup):
    """ Encodes a syllogistic response by transforming the tuple containing the
    response string and the task tuple into its string representation.

    Parameters
    ----------
    tuptup : pd.Series
        Pandas series containing the task string tuple (e.g.,
        'Some;models;managers/All;models;clerks') and response tuple
        representation (e.g., 'Some;managers;clerks').

    Returns
    -------
    str
        Encoded response (e.g., 'Iac').

    """

    response_string, task_tuple = tuptup
    response_tuple = response_string.split(';')

    if response_tuple[0] == 'NVC':
        return 'NVC'

    object_sets = [set(x.split(';')[1:]) for x in task_tuple.split('/')]
    midterm = object_sets[0].intersection(object_sets[1])
    obj_a = object_sets[0] - midterm

    quant = response_tuple[0].replace('All', 'A').replace(
        'Some not', 'O').replace('Some', 'I').replace('No', 'E')

    return quant + ('ac' if response_tuple[1] == list(obj_a)[0] else 'ca')

def decode_response(enc_response, task):
    """ Decodes an encoded syllogistic response by transforming it to the
    corresponding tuple representation and inserting the appropriate terms.

    Parameters
    ----------
    enc_response : str
        Encoded syllogistic response (e.g., 'Aac').

    task : list(str)
        Syllogistic task in the tuple list representation (e.g.,
        [['Some', 'models', 'managers'], ['All', 'models', 'clerks']]).

    """

    print(task)
    exit()

    if enc_response == 'NVC':
        return ['NVC']

    obj_a = set(task[0][1:]) - set(task[1][1:])
    obj_c = set(task[1][1:]) - set(task[0][1:])

    quant = enc_response[0].replace('A', 'All').replace(
        'I', 'Some').replace('O', 'Some not').replace('E', 'No')
    if enc_response[1:] == 'ac':
        return [quant, list(obj_a)[0], list(obj_c)[0]]

    return [quant, list(obj_c)[0], list(obj_a)[0]]
