import ccobra

class NVCModel(ccobra.CCobraModel):
    def __init__(self, name='NVCModel'):
        super(NVCModel, self).__init__(name, ["syllogistic"], ["single-choice"])

    def predict(self, item, **kwargs):
        return [['NVC']]
