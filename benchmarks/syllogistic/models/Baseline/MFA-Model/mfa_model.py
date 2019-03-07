import collections

import numpy as np

import ccobra

class MFAModel(ccobra.CCobraModel):
    def __init__(self, name='MFAModel', k=1):
        super(MFAModel, self).__init__(name, ["syllogistic"], ["single-choice"])

        # Parameters
        self.k = k

        # Initialize the model's storage
        syllogisms = ccobra.syllogistic.SYLLOGISMS
        responses = ccobra.syllogistic.RESPONSES
        self.predictions = {}
        for syllogism in syllogisms:
            self.predictions[syllogism] = dict(
                zip(responses, [0]*len(responses)))

    def pre_train(self, dataset):
        for subj_train_data in dataset:
            for seq_train_data in subj_train_data:
                self.adapt(seq_train_data['item'], seq_train_data['response'])

    def predict(self, item, **kwargs):
        enc_task = ccobra.syllogistic.encode_task(item.task)
        resp_counts = self.predictions[enc_task]

        target_value = sorted(
            np.unique(list(resp_counts.values())), reverse=True)[self.k - 1]
        resps = []
        for resp, cnt in resp_counts.items():
            if cnt == target_value:
                resps.append(resp)

        return ccobra.syllogistic.decode_response(
            resps[np.random.randint(0, len(resps))], item.task)

    def adapt(self, item, response, **kwargs):
        enc_task = ccobra.syllogistic.encode_task(item.task)
        enc_resp = ccobra.syllogistic.encode_response(response, item.task)
        self.predictions[enc_task][enc_resp] += 1
