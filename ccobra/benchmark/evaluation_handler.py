""" CCOBRA evaluation handler.

"""

import copy

import pandas as pd
import numpy as np

from .. import tuple_to_string

class EvaluationHandler():
    """ Evaluation handler class used to handle an evaluation setting.

    """
    def __init__(self, data_column, comparator, predict_fn_name, adapt_fn_name, task_encoders, resp_encoders):
        """ Initializes the Evaluation handler for a given data column and evaluation settings.

        Parameters
        ----------
        data_column : str
            Name of the data column to predict.

        comparator : ccobra.CCobraComparator
            Comparator to be used when comparing the prediction to the true value.

        predict_fn_name : str
            Name of the predict function within the models-

        adapt_fn_name : str
            Name of the adapt function within the models-

        task_encoders : dict(str, ccobra.CCobraTaskEncoder)
            Dictionary specifying the task encoders to be used for the domains in the dataset.

        resp_encoders : dict(str, ccobra.CCobraResponseEncoder)
            Dictionary specifying the response encoders to be used for the domains in the dataset.

        """
        self.data_column = data_column
        self.comparator = comparator
        self.predict_fn_name = predict_fn_name
        self.adapt_fn_name = adapt_fn_name
        self.task_encoders = task_encoders
        self.resp_encoders = resp_encoders

        # Prepare result dataframe
        self.result = []

    def predict(self, model, modelname, item, target, aux):
        """ Queries a given model for the prediction to a given task and manages the results.

        Parameters
        ----------
        model : ccobra.CCobraModel
            Model to query.

        modelname : str
            Name of the model in the results.

        item : ccobra.Item
            The item that the model should base the prediction on.

        target : tuple
            True response for the given item.

        aux : dict(str, object)
            Dictionary containing auxiliary information that should be passed to the model.

        """
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
            'truth': tuple_to_string(target),
            'prediction': tuple_to_string(prediction),
            'score': score
        }

        if self.task_encoders:
            domain = res_dict['domain']
            res_dict['task_enc'] = self.task_encoders[domain].encode_task(item.task) if domain in self.task_encoders else np.nan

        if self.resp_encoders:
            domain = res_dict['domain']
            if item.response_type == "verify":
                if len(item.choices) != 1:
                    raise ValueError("Only a single choice is allowed for response type 'verify'")
                
                truth_enc = np.nan
                prediction_enc = np.nan
                if domain in self.resp_encoders:
                    verification_target = item.choices[0]
                    verification_enc = self.resp_encoders[domain].encode_response(verification_target, item.task)
                
                    prediction_enc = "{};{}".format(verification_enc, prediction)
                    truth_enc = "{};{}".format(verification_enc, target)

                res_dict['truth_enc_{}'.format(self.data_column)] = truth_enc
                res_dict['prediction_enc_{}'.format(self.data_column)] = prediction_enc
            else:
                truth_enc = self.resp_encoders[domain].encode_response(target, item.task) if domain in self.resp_encoders else np.nan
                prediction_enc = self.resp_encoders[domain].encode_response(prediction, item.task) if domain in self.resp_encoders else np.nan
                res_dict['truth_enc_{}'.format(self.data_column)] = truth_enc
                res_dict['prediction_enc_{}'.format(self.data_column)] = prediction_enc

        self.result.append(res_dict)

    def adapt(self, model, item, full):
        """ Allows the given model to adapt to the true response to a given task.

        Parameters
        ----------
        model : ccobra.CCobraModel
            Model to query.

        item : ccobra.Item
            The item that the model should base the prediction on.

        full : dict(str, object)
            Dictionary containing the true response and the auxiliary information.

        """
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
        """ Returns the results for the respective evaluation setting.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the results for the evaluation setting.

        """
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

