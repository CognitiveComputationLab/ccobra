import unittest
import ccobra

class EncodingTestCase(unittest.TestCase):
    """ Tests the encoding functions for the syllogistic reasoning
    domain.

    """

    def test_encode_response_quantifiers(self):
        """ Tests the encodings of all syllogistic quantifiers on a single
        demonstrative task.

        """

        task = [
            ['All', 'models', 'managers'],
            ['All', 'managers', 'clerks']
        ]

        self.assertEqual('Aac', ccobra.syllogistic.encode_response(
            ['All', 'models', 'clerks'], task))
        self.assertEqual('Aca', ccobra.syllogistic.encode_response(
            ['All', 'clerks', 'models'], task))
        self.assertEqual('Iac', ccobra.syllogistic.encode_response(
            ['Some', 'models', 'clerks'], task))
        self.assertEqual('Ica', ccobra.syllogistic.encode_response(
            ['Some', 'clerks', 'models'], task))
        self.assertEqual('Eac', ccobra.syllogistic.encode_response(
            ['No', 'models', 'clerks'], task))
        self.assertEqual('Eca', ccobra.syllogistic.encode_response(
            ['No', 'clerks', 'models'], task))
        self.assertEqual('Oac', ccobra.syllogistic.encode_response(
            ['Some not', 'models', 'clerks'], task))
        self.assertEqual('Oca', ccobra.syllogistic.encode_response(
            ['Some not', 'clerks', 'models'], task))
        self.assertEqual('NVC', ccobra.syllogistic.encode_response(
            ['NVC'], task))

    def test_encode_response_brackets(self):
        task = [
            ['All', 'models', 'managers'],
            ['All', 'managers', 'clerks']
        ]

        # Regular quantified response
        self.assertEqual('Aac', ccobra.syllogistic.encode_response(
            [['All', 'models', 'clerks']], task))

        # NVC response
        self.assertEqual('NVC', ccobra.syllogistic.encode_response(
            'NVC', task))
        self.assertEqual('NVC', ccobra.syllogistic.encode_response(
            [['NVC']], task))

    def test_encode_task_figure(self):
        self.assertEqual('AA1', ccobra.syllogistic.encode_task(
            [['All', 'A', 'B'], ['All', 'B', 'C']]))
        self.assertEqual('AA2', ccobra.syllogistic.encode_task(
            [['All', 'B', 'A'], ['All', 'C', 'B']]))
        self.assertEqual('AA3', ccobra.syllogistic.encode_task(
            [['All', 'A', 'B'], ['All', 'C', 'B']]))
        self.assertEqual('AA4', ccobra.syllogistic.encode_task(
            [['All', 'B', 'A'], ['All', 'B', 'C']]))

    def test_encode_task_quantifiers(self):
        self.assertEqual('AO1', ccobra.syllogistic.encode_task(
            [['All', 'A', 'B'], ['Some not', 'B', 'C']]))
        self.assertEqual('EI1', ccobra.syllogistic.encode_task(
            [['No', 'A', 'B'], ['Some', 'B', 'C']]))

if __name__ == '__main__':
    unittest.main()
