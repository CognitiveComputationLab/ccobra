import unittest
import ccobra

class DecodingTestCase(unittest.TestCase):
    """ Tests the decoding functions for the syllogistic reasoning
    domain.

    """

    def test_decode_response_quantifiers(self):
        task = [['All', 'models', 'managers'], ['All', 'managers', 'clerks']]

        self.assertEqual([['All', 'models', 'clerks']],
            ccobra.syllogistic.decode_response('Aac', task))
        self.assertEqual([['All', 'clerks', 'models']],
            ccobra.syllogistic.decode_response('Acc', task))
        self.assertEqual([['Some', 'models', 'clerks']],
            ccobra.syllogistic.decode_response('Iac', task))
        self.assertEqual([['Some', 'clerks', 'models']],
            ccobra.syllogistic.decode_response('Icc', task))
        self.assertEqual([['No', 'models', 'clerks']],
            ccobra.syllogistic.decode_response('Eac', task))
        self.assertEqual([['No', 'clerks', 'models']],
            ccobra.syllogistic.decode_response('Ecc', task))
        self.assertEqual([['Some not', 'models', 'clerks']],
            ccobra.syllogistic.decode_response('Oac', task))
        self.assertEqual([['Some not', 'clerks', 'models']],
            ccobra.syllogistic.decode_response('Occ', task))

        self.assertEqual([['NVC']],
            ccobra.syllogistic.decode_response('NVC', task))

    def test_decode_response_brackets(self):
        task = [['All', 'models', 'managers'], ['All', 'managers', 'clerks']]

        self.assertEqual([['NVC']],
            ccobra.syllogistic.decode_response('NVC', task))
        self.assertEqual([['NVC']],
            ccobra.syllogistic.decode_response(['NVC'], task))
        self.assertEqual([['NVC']],
            ccobra.syllogistic.decode_response([['NVC']], task))

if __name__ == '__main__':
    unittest.main()
