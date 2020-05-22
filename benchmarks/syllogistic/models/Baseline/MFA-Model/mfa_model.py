import collections

import numpy as np

import ccobra

class MFAModel(ccobra.CCobraModel):
    def __init__(self, name='MFAModel', k=1):
        super(MFAModel, self).__init__(name, ["syllogistic"], ["single-choice"])

        # Parameters
        self.k = k

        # Initialize the model's storage
        self.database = np.zeros((64, 9))

    def pre_train(self, dataset):
        for subj_train_data in dataset:
            for seq_train_data in subj_train_data:
                self.adapt(seq_train_data['item'], seq_train_data['response'])

    def pre_train_person(self, dataset):
        self.pre_train([dataset])

    def predict(self, item, **kwargs):
        enc_task = ccobra.syllogistic.encode_task(item.task)
        task_idx = ccobra.syllogistic.SYLLOGISMS.index(enc_task)

        weights = self.database[task_idx]
        pred_idxs = np.arange(9)[weights == weights.max()]
        pred_idx = np.random.choice(pred_idxs)

        return ccobra.syllogistic.decode_response(
            ccobra.syllogistic.RESPONSES[pred_idx], item.task)

    def adapt(self, item, response, **kwargs):
        enc_task = ccobra.syllogistic.encode_task(item.task)
        enc_resp = ccobra.syllogistic.encode_response(response, item.task)

        task_idx = ccobra.syllogistic.SYLLOGISMS.index(enc_task)
        resp_idx = ccobra.syllogistic.RESPONSES.index(enc_resp)

        self.database[task_idx][resp_idx] += 1
