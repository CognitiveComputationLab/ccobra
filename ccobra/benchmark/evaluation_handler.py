import copy

import pandas as pd
import numpy as np

from . import comparator

class EvaluationHandler():
    def __init__(self, data_column, comparator, predict_fn_name, adapt_fn_name, task_encoders, resp_encoders):
        self.data_column = data_column
        self.comparator = comparator
        self.predict_fn_name = predict_fn_name
        self.adapt_fn_name = adapt_fn_name
        self.task_encoders = task_encoders
        self.resp_encoders = resp_encoders

        # Prepare result dataframe
        self.result = []

    def predict(self, model, modelname, item, target, aux):
        item = copy.deepcopy(item)
        aux = copy.deepcopy(aux)

        # Obtain the model prediction
        pred_fn = getattr(model, self.predict_fn_name, None)
        if pred_fn is None:
            raise NotImplementedError("{} has to be implemented in {}".format(self.predict_fn_name, modelname))

        prediction = pred_fn(item, **aux)
        score = self.comparator.compare(prediction, target)

        # Collect the evaluation result data
        res_dict = {
            'model': modelname,
            'id': item.identifier,
            'domain': item.domain,
            'response_type': item.response_type,
            'sequence': item.sequence_number,
            'task': item.task_str,
            'choices': item.choices_str,
            'truth': comparator.tuple_to_string(target),
            'prediction': comparator.tuple_to_string(prediction),
            'score': score
        }

        if self.task_encoders:
            domain = res_dict['domain']
            res_dict['task_enc'] = self.task_encoders[domain].encode_task(item.task) if domain in self.task_encoders else np.nan

        if self.resp_encoders:
            domain = res_dict['domain']
            res_dict['truth_enc_{}'.format(self.data_column)] = self.resp_encoders[domain].encode_response(target, item.task) if domain in self.resp_encoders else np.nan
            res_dict['prediction_enc_{}'.format(self.data_column)] = self.resp_encoders[domain].encode_response(prediction, item.task) if domain in self.resp_encoders else np.nan

        self.result.append(res_dict)

    def adapt(self, model, item, full):
        if self.adapt_fn_name is None:
            return

        item = copy.deepcopy(item)
        full = copy.deepcopy(full)

        target = full[self.data_column]
        aux = {x: y for x, y in full.items() if x != self.data_column}
        adapt_fn = getattr(model, self.adapt_fn_name, None)
        if adapt_fn is None:
            return

        adapt_fn(item, target, **aux)

    def get_result_df(self):
        return pd.DataFrame(self.result)

    def __repr__(self):
        s = 'EvaluationHandler(data_column={}, comparator={}, predict_fn_name={}, adapt_fn_name={}, task_encoders={}, resp_encoders={})'.format(
            self.data_column,
            self.comparator,
            self.predict_fn_name,
            self.adapt_fn_name,
            self.task_encoders,
            self.resp_encoders
        )
        return s

