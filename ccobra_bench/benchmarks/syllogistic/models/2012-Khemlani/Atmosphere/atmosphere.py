import pandas as pd
import numpy as np

import ccobra

class Atmosphere(ccobra.CCobraModel):
    def __init__(self, name='Atmosphere'):
        super(Atmosphere, self).__init__(
            name, ['syllogistic'], ['single-choice'])

        pred_df = pd.read_csv('Atmosphere.csv')
        self.predictions = dict(
            zip(
                pred_df['Syllogism'].tolist(),
                [x.split(';') for x in pred_df['Prediction']]))

    def predict(self, item, **kwargs):
        enc_task = ccobra.syllogistic.encode_task(
            '/'.join([';'.join(x) for x in item.task]))
        enc_resp = self.predictions[enc_task]
        dec_resp = [ccobra.syllogistic.decode_response(x, item.task) for x in enc_resp]
        return dec_resp[np.random.randint(0, len(dec_resp))]
