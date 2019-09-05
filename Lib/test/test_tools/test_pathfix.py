import os
import subprocess
import sys
import unittest
from test import support
from test.test_tools import import_tool, scriptsdir


class TestPathfixFunctional(unittest.TestCase):
    script = os.path.join(scriptsdir, 'pathfix.py')

    def setUp(self):
        self.temp_file = support.TESTFN
        self.addCleanup(support.unlink, support.TESTFN)

    def pathfix(self, shebang, pathfix_flags):
        with open(self.temp_file, 'w', encoding='utf8') as f:
            f.write(f'{shebang}\n' + 'print("Hello world")\n')
        subprocess.call([sys.executable, self.script, *pathfix_flags, '-n', self.temp_file])
        with open(self.temp_file, 'r', encoding='utf8') as f:
            output = f.read()
            lines = output.split('\n')
            self.assertEqual(lines[1:], ['print("Hello world")', ''])
            shebang = lines[0]
            return shebang

    def test_pathfix(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3',]),
            '#! /usr/bin/python3',
        )
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -R',
                ['-i', '/usr/bin/python3', ]),
            '#! /usr/bin/python3',
        )

    def test_pathfix_keeping_flags(self):
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python -R',
                ['-i', '/usr/bin/python3', '-k',]),
            '#! /usr/bin/python3 -R',
        )
        self.assertEqual(
            self.pathfix(
                '#! /usr/bin/env python',
                ['-i', '/usr/bin/python3', '-k',]),
            '#! /usr/bin/python3',
        )



if __name__ == '__main__':
    unittest.main()
