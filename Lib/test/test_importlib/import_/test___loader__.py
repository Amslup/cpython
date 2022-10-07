from importlib import machinery
import sys
import types
import unittest
import warnings

from test.test_importlib import util


class SpecLoaderMock:

    def find_spec(self, fullname, path=None, target=None):
        return machinery.ModuleSpec(fullname, self)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        pass


class SpecLoaderAttributeTests:

    def test___loader__(self):
        loader = SpecLoaderMock()
        with util.uncache('blah'), util.import_state(meta_path=[loader]):
            module = self.__import__('blah')
        self.assertEqual(loader, module.__loader__)


(Frozen_SpecTests,
 Source_SpecTests
 ) = util.test_both(SpecLoaderAttributeTests, __import__=util.__import__)


class LoaderMock:

    def find_module(self, fullname, path=None):
        return self

    def load_module(self, fullname):
        sys.modules[fullname] = self.module
        return self.module


class LoaderAttributeTests:

    def test___loader___missing(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ImportWarning)
            module = types.ModuleType('blah')
            try:
                del module.__spec__
            except AttributeError:
                pass
            loader = LoaderMock()
            loader.module = module
            with util.uncache('blah'), util.import_state(meta_path=[loader]):
                module = self.__import__('blah')
            self.assertEqual(loader, module.__spec__.loader)

    def test___loader___is_None(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ImportWarning)
            module = types.ModuleType('blah')
            loader = LoaderMock()
            loader.module = module
            module.__spec__ = machinery.ModuleSpec('blah', loader)
            with util.uncache('blah'), util.import_state(meta_path=[loader]):
                returned_module = self.__import__('blah')
            self.assertEqual(returned_module, module.__spec__.loader)


(Frozen_Tests,
 Source_Tests
 ) = util.test_both(LoaderAttributeTests, __import__=util.__import__)


if __name__ == '__main__':
    unittest.main()
