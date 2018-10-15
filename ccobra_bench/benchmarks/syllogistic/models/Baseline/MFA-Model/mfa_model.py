import collections

import numpy as np

import ccobra

class MFAModel(ccobra.CCobraModel):
    def __init__(self, name='MFAModel'):
        super(MFAModel, self).__init__(name, ["syllogistic"], ["single-choice"])

        # Initialize the model's storage
        syllogisms = ccobra.syllogistic.get_syllogisms()
        responses = ccobra.syllogistic.get_responses()
        self.predictions = {}
        for syllogism in syllogisms:
            self.predictions[syllogism] = responses

    def pre_train(self, dataset):
        count_df = dataset.get().groupby(
            ['task', 'response'], as_index=False)['id'].agg('count')

        count_df['enc_task'] = count_df['task'].apply(ccobra.syllogistic.encode_task)
        count_df['enc_resp'] = count_df[['response', 'task']].apply(ccobra.syllogistic.encode_response, axis=1)

        for task, df in count_df.groupby('enc_task'):
            mfa = df.loc[df['id'] == df['id'].max()]['enc_resp'].tolist()
            self.predictions[task] = mfa

    def predict(self, item, **kwargs):
        enc_task = ccobra.syllogistic.encode_task('/'.join([';'.join(x) for x in item.task]))
        enc_resp = self.predictions[enc_task]

        responses = [ccobra.syllogistic.decode_response(x, item.task) for x in enc_resp]
        return responses[np.random.randint(0, len(responses))]
