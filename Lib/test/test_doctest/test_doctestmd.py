import unittest
import doctest

def dummyfunction_codeblocks():
    """
    A dummy function that uses codeblocks in the examples.

    It is used like this:
    ```
    >>> 1 == 1
    True
    ```
    """
    pass

class TestMarkdownDocstring(unittest.TestCase):
    def test_DoctestRunner(self):
        test = doctest.DocTestFinder().find(dummyfunction_codeblocks)[0]
        results = doctest.DocTestRunner().run(test)
        self.assertEqual(results, (0,1))
