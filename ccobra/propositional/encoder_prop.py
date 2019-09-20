import ccobra

OPERATORS = [
    'not',
    'and',
    'or',
    'iff',
    'if'
]

class PropositionalEncoder(ccobra.CCobraDomainEncoder):
    """ Syllogistic encoder. Provides functions for abbreviating syllogistic tasks and responses.

    """

    @staticmethod
    def encode_clause(clause):
        """ Encodes a single clause by parsing the Polish normal form.

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

        """

        return ', '.join([PropositionalEncoder.encode_clause(x) for x in task])

    @staticmethod
    def encode_response(response, task):
        """ Encodes a response to its propositional encoding.

        """

        return PropositionalEncoder.encode_clause(response[0])
