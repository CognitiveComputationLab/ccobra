""" CCOBRA model interface. Defines the general structure a model needs to
implement for being used in the CCOBRA framework.

"""

import ccobra

class CheatModel(ccobra.CCobraModel):
    """ Base class for CCOBRA models.

    """

    def __init__(self, name='CheatModel'):
        super(CheatModel, self).__init__(
            name, ['syllogistic'], ['single-choice'])

    def pre_train(self, dataset):
        pass

    def person_train(self, data):
        self.data = data

    def predict(self, item, **kwargs):
        for dat in self.data:
            dat_item = dat['item']
            if dat_item == item:
                return dat['response']

        assert False, 'IMPOSSIBRU'

        return [['NVC']]

    def adapt(self, item, target, **kwargs):
        pass
