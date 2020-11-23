""" Propositional domain encoders.

"""

from ccobra import CCobraTaskEncoder

OPERATORS = [
    'not',
    'and',
    'or',
    'iff',
    'if'
]

class PropositionalTaskEncoder(CCobraTaskEncoder):
    """ Syllogistic encoder. Provides functions for abbreviating syllogistic tasks.

    """

    @staticmethod
    def encode_clause(clause):
        """ Encodes a single clause by parsing the Polish normal form.

        Parameters
        ----------
        clause : list(str)
            Propositional clause in list representation (e.g., ['If', 'not', 'A', 'B']).

        Returns
        -------
        str
            String representation of the input clause (e.g., "~A -> B").

        """

        # Parse the clause in reverse
        stack = []
        for term in reversed(clause):
            norm_term = term.lower()
            if norm_term in OPERATORS:
                if norm_term == 'not':
                    stack.append('~{}'.format(stack.pop()))
                elif norm_term == 'and':
                    stack.append('({} & {})'.format(stack.pop(), stack.pop()))
                elif norm_term == 'or':
                    stack.append('({} | {})'.format(stack.pop(), stack.pop()))
                elif norm_term == 'iff':
                    stack.append('({} <=> {})'.format(stack.pop(), stack.pop()))
                elif norm_term == 'if':
                    stack.append('({} -> {})'.format(stack.pop(), stack.pop()))
            else:
                stack.append(term)

        assert len(stack) == 1, 'Error: {} -> {}'.format(clause, stack)
        return stack[0]

    @staticmethod
    def encode_task(task):
        """ Encodes a task to its propositional encoding.

        Parameters
        ----------
        task : list(list(str))
            Propositional task as a list of clauses (e.g., [["If", "A", "B"], ["A"]]).

        Returns
        -------
        str
            String representation of the propositional task.

        """

        return ' ; '.join([PropositionalTaskEncoder.encode_clause(x) for x in task])
