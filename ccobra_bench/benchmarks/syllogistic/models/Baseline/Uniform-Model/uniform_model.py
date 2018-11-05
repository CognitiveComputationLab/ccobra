import numpy as np

import ccobra

class UniformModel(ccobra.CCobraModel):
    def __init__(self, name='UniformModel'):
        super(UniformModel, self).__init__(name, ["syllogistic"], ["single-choice"])

    def predict(self, item, **kwargs):
        return item.choices[np.random.randint(0, len(item.choices))]
