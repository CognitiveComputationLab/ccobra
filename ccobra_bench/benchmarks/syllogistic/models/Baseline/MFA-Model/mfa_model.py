import collections

import numpy as np

from ccobra import CCobraModel

def get_syllogisms():
    syllogisms = []
    for prem1 in ['A', 'I', 'E', 'O']:
        for prem2 in ['A', 'I', 'E', 'O']:
            for fig in ['1', '2', '3', '4']:
                syllogisms.append(prem1 + prem2 + fig)
    return syllogisms

def get_responses():
    responses = []
    for quant in ['A', 'I', 'E', 'O']:
        for direction in ['ac', 'ca']:
            responses.append(quant + direction)
    responses.append('NVC')
    return responses

def encode_task(task_tuple):
    p1, p2 = [x.split(';') for x in task_tuple.split('/')]

    quant1 = p1[0].replace('All', 'A').replace(
        'Some not', 'O').replace('Some', 'I').replace('No', 'E')
    quant2 = p2[0].replace('All', 'A').replace(
        'Some not', 'O').replace('Some', 'I').replace('No', 'E')
    figure = 1
    if p1[1] == p2[1]:
        figure = 3
    elif p1[2] == p2[1]:
        figure = 1
    elif p1[2] == p2[2]:
        figure = 4
    elif p1[1] == p2[2]:
        figure = 2
    else:
        raise ValueError('Could not determine figure of:', task_tuple)

    return quant1 + quant2 + str(figure)

def encode_response(tuptup):
    response_string, task_tuple = tuptup
    response_tuple = response_string.split(';')

    if response_tuple[0] == 'NVC':
        return 'NVC'

    object_sets = [set(x.split(';')[1:]) for x in task_tuple.split('/')]
    midterm = object_sets[0].intersection(object_sets[1])
    obj_a = object_sets[0] - midterm

    quant = response_tuple[0].replace('All', 'A').replace(
        'Some not', 'O').replace('Some', 'I').replace('No', 'E')

    return quant + ('ac' if response_tuple[1] == list(obj_a)[0] else 'ca')

def decode_response(enc_response, task):
    if enc_response == 'NVC':
        return ['NVC']

    obj_a = set(task[0][1:]) - set(task[1][1:])
    obj_c = set(task[1][1:]) - set(task[0][1:])

    quant = enc_response[0].replace('A', 'All').replace('I', 'Some').replace('O', 'Some not').replace('E', 'No')
    if enc_response[1:] == 'ac':
        return [quant, list(obj_a)[0], list(obj_c)[0]]

    return [quant, list(obj_c)[0], list(obj_a)[0]]


class MFAModel(CCobraModel):
    def __init__(self, name='MFAModel'):
        super(MFAModel, self).__init__(name, ["syllogistic"], ["single-choice"])

        # Initialize the model's storage
        syllogisms = get_syllogisms()
        responses = get_responses()
        self.predictions = {}
        for syllogism in syllogisms:
            self.predictions[syllogism] = responses

    def pre_train(self, dataset):
        count_df = dataset.get().groupby(
            ['task', 'response'], as_index=False)['id'].agg('count')

        count_df['enc_task'] = count_df['task'].apply(encode_task)
        count_df['enc_resp'] = count_df[['response', 'task']].apply(encode_response, axis=1)

        for task, df in count_df.groupby('enc_task'):
            mfa = df.loc[df['id'] == df['id'].max()]['enc_resp'].tolist()
            self.predictions[task] = mfa

    def predict(self, item, **kwargs):
        enc_task = encode_task('/'.join([';'.join(x) for x in item.task]))
        enc_resp = self.predictions[enc_task]

        responses = [decode_response(x, item.task) for x in enc_resp]
        return responses[np.random.randint(0, len(responses))]
