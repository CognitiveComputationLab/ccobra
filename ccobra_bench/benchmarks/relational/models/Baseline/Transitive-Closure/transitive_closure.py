""" Transitive closure model originally implemented as the "dansitive closure"
model.

"""

import ccobra

def get_transitive_closure(premises, max_depth=10):
    new_found = True
    it = 0

    closure = set()
    closure.update(premises)

    while(new_found):
        if it >= max_depth:
            break
        new_found = False
        c_size = len(closure)

        newly = set()
        for rule in closure:
            rule = rule.split(";")
            for rule2 in closure:
                rule2 = rule2.split(";")

                if rule[2] == rule2[1]:
                    newly.add(";".join([rule[0], rule[1], rule2[2]]))
        closure.update(newly)
        if len(closure) > c_size:
            new_found = True
            c_size = len(closure)
        it += 1

    return closure

def is_valid_conclusion(premises, conclusion):
    # replace right by left
    proc_premises = []
    for premise in premises:
        if premise[0] == "Right":
            proc_premises.append(["Left", premise[2], premise[1]])
        else:
            proc_premises.append(premise)
    proc_conclusion = ["Left", conclusion[2], conclusion[1]] \
                        if conclusion[0] == "Right" else conclusion

    premises_str = [";".join(x) for x in proc_premises]
    conclusion_str = ";".join(proc_conclusion)
    closure = get_transitive_closure(premises_str)

    return conclusion_str in closure

class TransitiveClosure(ccobra.CCobraModel):
    def __init__(self, name='TransitiveClosure'):
        super(TransitiveClosure, self).__init__(name, ['spatial-relational'], ['verify'])

    def predict(self, item, **kwargs):
        return is_valid_conclusion(item.task, item.choices[0])
