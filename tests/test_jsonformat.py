import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "bin.d", "50-spl-jsonformat"))  # noqa


import jsonformat

# COOKIECUTTER-TODO: Fill in unit tests logic, as required.  Remove default tests


class TestJsonFormatCommand(unittest.TestCase):
    def test_example001(self):
        """ Descrption of the test ... """
        actual = "1"
        self.assertEqual(actual, "1")

    def test_example002(self):
        """ Descrption of a exception raising test """
        with self.assertRaises(ValueError):
            int("apple") > float()

    @unittest.expectedFailure
    def test_not_working(self):
        """ Demonstration of a failing tests  """
        # This pattern is useful for known bug scenarios, once fixed, remove @expectFailure
        raise Exception("We know dis!  (Dr Wenowdis)")

    @unittest.skipUnless("SPLUNK_HOME" in os.environ, "Need 'SPLUNK_HOME' to run test")
    def test_that_needs_splunk(self):
        # Some test that will only run if SPLUNK_HOME is set
        os.listdir(os.environ["SPLUNK_HOME"])


if __name__ == '__main__':
    unittest.main()
