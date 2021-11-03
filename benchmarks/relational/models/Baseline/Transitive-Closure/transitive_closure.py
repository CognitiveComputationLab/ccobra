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
    premises = [x.lower() for x in premises]
    new_found = True
    it = 0

    closure = set()
    closure.update(premises)

    for rule in list(closure):
        rule = rule.split(';')
        closure.add(";".join([OPPOSITES[rule[0]], rule[2], rule[1]]))

    while new_found:
        if it >= max_depth:
            print("Break due to max-depth")
            break
        new_found = False
        c_size = len(closure)

        newly = set()
        for rule in closure:
            rule = rule.lower().split(";")

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
                elif rule[2] == rule2[1]:
                    for key, value in COMBINATIONS.items():
                        if value == rule_set:
                            newly.add(";".join([key, rule[1], rule2[2]]))
                            newly.add(";".join([OPPOSITES[key], rule2[2], rule[1]]))

                # Perform transitive closure
                if rule[2] == rule2[1]: 
                    if rule[0] == rule2[0]:
                        newly.add(";".join([rule[0], rule[1], rule2[2]]))
                        newly.add(";".join([OPPOSITES[rule[0]], rule2[2], rule[1]]))
                    elif rule2[0] in COMBINATIONS and rule[0] in COMBINATIONS[rule2[0]]:
                        # e.g., rule2 == north-east, rule == north
                        # => north-east and north
                        newly.add(";".join([rule[0], rule[1], rule2[2]]))
                        newly.add(";".join([rule2[0], rule[1], rule2[2]]))
                        newly.add(";".join([OPPOSITES[rule[0]], rule2[2], rule[1]]))
                        newly.add(";".join([OPPOSITES[rule2[0]], rule2[2], rule[1]]))
                    elif rule[0] in COMBINATIONS and rule2[0] in COMBINATIONS[rule[0]]:
                        # e.g., rule == north-east, rule2 == north
                        # => north-east and north
                        newly.add(";".join([rule[0], rule[1], rule2[2]]))
                        newly.add(";".join([rule2[0], rule[1], rule2[2]]))
                        newly.add(";".join([OPPOSITES[rule[0]], rule2[2], rule[1]]))
                        newly.add(";".join([OPPOSITES[rule2[0]], rule2[2], rule[1]]))
                    elif rule[0] in COMBINATIONS and rule2[0] in COMBINATIONS:
                        # e.g., north-east and north-west
                        rule1_set = COMBINATIONS[rule[0]]
                        rule2_set = COMBINATIONS[rule2[0]]
                        new_ops = rule1_set.intersection(rule2_set)
                        for new_op in new_ops:
                            newly.add(";".join([new_op, rule[1], rule2[2]]))
                            newly.add(";".join([OPPOSITES[new_op], rule2[2], rule[1]]))
                            
        closure.update(newly)
        
        if len(closure) > c_size:
            new_found = True
            c_size = len(closure)
        it += 1
    return closure

def is_valid_conclusion(premises, conclusion):
    premises_str = [";".join(x).lower() for x in premises]
    closure = get_transitive_closure(premises_str)
    conclusion_strs = [";".join(x).lower() for x in conclusion]
    
    for concl in conclusion_strs:
        if concl not in closure:
            return False
    return True
    
def is_possible_model(premises, conclusion):
    premises_str = [";".join(x).lower() for x in premises]
    closure = get_transitive_closure(premises_str)
    
    # invert the conclusions
    conclusion_strs = []
    for partial_conclusion in conclusion:
        reverted = OPPOSITES[partial_conclusion[0].lower()]
        conclusion_strs.append("{};{};{}".format(reverted, partial_conclusion[1], partial_conclusion[2]).lower())
    
    for concl in conclusion_strs:
        if concl in closure:
            return False
    return True

class TransitiveClosure(ccobra.CCobraModel):
    def __init__(self, name='TransitiveClosure'):
        super(TransitiveClosure, self).__init__(name, ['spatial-relational'], ['verify', "accept", 'single-choice'])

    def predict(self, item, **kwargs):
        if item.response_type == 'verify':
            return is_valid_conclusion(item.task, item.choices[0])
            
        if item.response_type == 'accept':
            return is_possible_model(item.task, item.choices[0])   

        result_options = []
        for choice in item.choices:
            if is_valid_conclusion(item.task, choice):
                result_options.append(choice)

        if len(result_options) == 0:
            result_options = item.choices

        return result_options[np.random.randint(0, len(result_options))]
