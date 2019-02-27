""" Transitive closure model originally implemented as the "dansitive closure"
model.

"""

import numpy as np
import ccobra

OPPOSITES = {
    'right': 'left',
    'left': 'right',
    'up': 'down',
    'down': 'up',
    'north': 'south',
    'south': 'north',
    'west': 'east',
    'east': 'west',
    'north-east': 'south-west',
    'north-west': 'south-east',
    'south-east': 'north-west',
    'south-west': 'north-east'
}

COMBINATIONS = {
    'north-east': set(['north', 'east']),
    'north-west': set(['north', 'west']),
    'south-east': set(['south', 'east']),
    'south-west': set(['south', 'west'])
}

def get_transitive_closure(premises, max_depth=10):
    new_found = True
    it = 0

    closure = set()
    closure.update(premises)

    for rule in list(closure):
        rule = rule.split(';')
        closure.add(";".join([OPPOSITES[rule[0]], rule[2], rule[1]]))

    while new_found:
        if it >= max_depth:
            break
        new_found = False
        c_size = len(closure)

        newly = set()
        for rule in closure:
            rule = rule.split(";")

            # Split combined directions
            if rule[0] in COMBINATIONS:
                for subop in COMBINATIONS[rule[0]]:
                    newly.add(";".join([subop, rule[1], rule[2]]))
                    newly.add(";".join([OPPOSITES[subop], rule[2], rule[1]]))

            for rule2 in closure:
                if rule == rule2:
                    continue

                rule2 = rule2.lower().split(";")

                # Merge combined directions only in transitive case
                rule_set = set([rule[0], rule2[0]])
                if rule[1] == rule2[1] and rule[2] == rule2[2]:
                    for key, value in COMBINATIONS.items():
                        if value == rule_set:
                            newly.add(";".join([key, rule[1], rule2[2]]))
                            newly.add(";".join([OPPOSITES[key], rule2[2], rule[1]]))

                # Perform transitive closure
                if rule[2] == rule2[1] and rule[0] == rule2[0]:
                    newly.add(";".join([rule[0], rule[1], rule2[2]]))
                    newly.add(";".join([OPPOSITES[rule[0]], rule2[2], rule[1]]))

        closure.update(newly)
        if len(closure) > c_size:
            new_found = True
            c_size = len(closure)
        it += 1
    return closure

def is_valid_conclusion(premises, conclusion):
    premises_str = [";".join(x).lower() for x in premises]
    conclusion_str = ";".join(conclusion[0]).lower()
    closure = get_transitive_closure(premises_str)
    return conclusion_str in closure

class TransitiveClosure(ccobra.CCobraModel):
    def __init__(self, name='TransitiveClosure'):
        super(TransitiveClosure, self).__init__(name, ['spatial-relational'], ['verify', 'single-choice'])

    def predict(self, item, **kwargs):
        if item.response_type == 'verify':
            return is_valid_conclusion(item.task, item.choices[0])

        result_options = []
        for choice in item.choices:
            if is_valid_conclusion(item.task, choice):
                result_options.append(choice)

        if len(result_options) == 0:
            result_options = item.choices

        return result_options[np.random.randint(0, len(result_options))]
