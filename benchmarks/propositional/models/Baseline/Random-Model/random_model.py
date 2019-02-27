import numpy as np

import ccobra

class RandomModel(ccobra.CCobraModel):
    def __init__(self, name='RandomModel'):
        super(RandomModel, self).__init__(
            name, ['propositional'], ['single-choice'])

    def predict(self, item, **kwargs):
        return item.choices[np.random.randint(0, len(item.choices))]
