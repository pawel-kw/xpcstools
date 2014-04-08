import unittest
import sys
sys.path.append('../')
import inputparser

class testInputParser(unittest.TestCase):

    def setUp(self):
        self.oldInputFile = './input_old.txt'
        self.newInputFile = './input_new.txt'
        self.newInputXPCSFile = './input_new_xpcs.txt'

    def test_old_input_read(self):
        # try to read the classic input file example to see
        # if it doesn't produce any errors:
        input_data = inputparser.inputparser(self.oldInputFile)

    def test_old_input_recognition(self):
        # is the input data format recognized?
        input_data = inputparser.inputparser(self.oldInputFile)
        self.assertTrue(input_data.Parameters['oldInputFormat'])

    def test_new_input_read(self):
        # try to read the pyxsvs input file example to see
        # if it doesn't produce any errors:
        input_data = inputparser.inputparser(self.newInputFile)

    def test_new_input_recognition(self):
        input_data = inputparser.inputparser(self.newInputFile)
        self.assertFalse(input_data.Parameters['oldInputFormat'])

    def test_new_input_xpcsmode(self):
        input_data = inputparser.inputparser(self.newInputXPCSFile)
        self.assertTrue(input_data.Parameters['mode'] == 'XPCS')

suite = unittest.TestLoader().loadTestsFromTestCase(testInputParser)
unittest.TextTestRunner(verbosity=2).run(suite)
