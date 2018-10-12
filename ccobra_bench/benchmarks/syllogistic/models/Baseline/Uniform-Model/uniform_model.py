import numpy as np

from ccobra import CCobraModel

class UniformModel(CCobraModel):
    def __init__(self, name='UniformModel'):
        super(UniformModel, self).__init__(name, ["syllogistic"], ["single-choice"])

    def predict(self, item, **kwargs):
        return np.random.choice(item.choices)
