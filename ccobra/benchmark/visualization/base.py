""" Base classes and functions for CCOBRA visualization.

"""

import numpy as np

def ccobracolor(idx, n_models, lightness=0.5):
    x = (idx + 1) / (n_models + 1)
    r = (np.sin(x * 2 * np.pi * 1.247 + np.pi) * 127 + 128) * lightness
    g = (np.sin(x * 2 * np.pi * 0.373) * 127 + 128) * lightness
    b = (np.cos(x * 2 * np.pi * 0.91113) * 127 + 128) * lightness
    return '#' + ''.join([('0' + hex(int(y)).replace('0x', ''))[-2:] for y in [r, g, b]])

class CCobraVisualizer():
    def __init__(self):
        pass

    def to_html(self, result_df):
        raise NotImplementedError()
