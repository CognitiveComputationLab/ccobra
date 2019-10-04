import numpy as np

import ccobra

def onehot_syllogism(syl):
    result = np.zeros((64,), dtype='float')
    result[ccobra.syllogistic.SYLLOGISMS.index(syl)] = 1
    return result

def onehot_syllogism_content(syl):
    """
    >>> onehot_syllogism('AA1')
    array([1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.])
    >>> onehot_syllogism('OI3')
    array([0., 0., 0., 1., 0., 1., 0., 0., 0., 0., 1., 0.])
    >>> onehot_syllogism('IE4')
    array([0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.])

    """

    task = np.zeros((12,), dtype='float')
    quants = quants = ['A', 'I', 'E', 'O']
    task[quants.index(syl[0])] = 1
    task[4 + quants.index(syl[1])] = 1
    task[8 + int(syl[2]) - 1] = 1
    return task

def onehot_response(response):
    """
    >>> onehot_response('Aac')
    array([1., 0., 0., 0., 0., 0., 0., 0., 0.])
    >>> onehot_response('NVC')
    array([0., 0., 0., 0., 0., 0., 0., 0., 1.])
    >>> onehot_response('Oca')
    array([0., 0., 0., 0., 0., 0., 0., 1., 0.])

    """

    resp = np.zeros((9,), dtype='float')
    resp[ccobra.syllogistic.RESPONSES.index(response)] = 1
    return resp
