import os
import pickle
import sys
from textwrap import dedent, indent
import threading
import types
import unittest

from test import support
from test.support import import_helper
# Raise SkipTest if subinterpreters not supported.
_interpreters = import_helper.import_module('_xxsubinterpreters')
from test.support import interpreters
from test.support.interpreters import InterpreterNotFoundError
from .utils import (
    _captured_script, _run_output, _running, TestBase,
    CapturingScript,
)


class ModuleTests(TestBase):

    def test_queue_aliases(self):
        first = [
            interpreters.create_queue,
            interpreters.Queue,
            interpreters.QueueEmpty,
            interpreters.QueueFull,
        ]
        second = [
            interpreters.create_queue,
            interpreters.Queue,
            interpreters.QueueEmpty,
            interpreters.QueueFull,
        ]
        self.assertEqual(second, first)


class CreateTests(TestBase):

    def test_in_main(self):
        interp = interpreters.create()
        self.assertIsInstance(interp, interpreters.Interpreter)
        self.assertIn(interp, interpreters.list_all())

    def test_in_thread(self):
        lock = threading.Lock()
        interp = None
        def f():
            nonlocal interp
            interp = interpreters.create()
            lock.acquire()
            lock.release()
        t = threading.Thread(target=f)
        with lock:
            t.start()
        t.join()
        self.assertIn(interp, interpreters.list_all())

    def test_in_subinterpreter(self):
        main, = interpreters.list_all()
        interp = interpreters.create()
        out = _run_output(interp, dedent("""
            from test.support import interpreters
            interp = interpreters.create()
            print(interp.id)
            """))
        interp2 = interpreters.Interpreter(int(out))
        self.assertEqual(interpreters.list_all(), [main, interp, interp2])

    def test_after_destroy_all(self):
        before = set(interpreters.list_all())
        # Create 3 subinterpreters.
        interp_lst = []
        for _ in range(3):
            interps = interpreters.create()
            interp_lst.append(interps)
        # Now destroy them.
        for interp in interp_lst:
            interp.close()
        # Finally, create another.
        interp = interpreters.create()
        self.assertEqual(set(interpreters.list_all()), before | {interp})

    def test_after_destroy_some(self):
        before = set(interpreters.list_all())
        # Create 3 subinterpreters.
        interp1 = interpreters.create()
        interp2 = interpreters.create()
        interp3 = interpreters.create()
        # Now destroy 2 of them.
        interp1.close()
        interp2.close()
        # Finally, create another.
        interp = interpreters.create()
        self.assertEqual(set(interpreters.list_all()), before | {interp3, interp})


class GetMainTests(TestBase):

    def test_id(self):
        main = interpreters.get_main()
        self.assertEqual(main.id, 0)

    def test_current(self):
        main = interpreters.get_main()
        current = interpreters.get_current()
        self.assertIs(main, current)

    def test_idempotent(self):
        main1 = interpreters.get_main()
        main2 = interpreters.get_main()
        self.assertIs(main1, main2)


class GetCurrentTests(TestBase):

    def test_main(self):
        main = interpreters.get_main()
        current = interpreters.get_current()
        self.assertEqual(current, main)

    def test_subinterpreter(self):
        main = interpreters.get_main()
        interp = interpreters.create()
        out = _run_output(interp, dedent("""
            from test.support import interpreters
            cur = interpreters.get_current()
            print(cur.id)
            """))
        current = interpreters.Interpreter(int(out))
        self.assertEqual(current, interp)
        self.assertNotEqual(current, main)

    def test_idempotent(self):
        with self.subTest('main'):
            cur1 = interpreters.get_current()
            cur2 = interpreters.get_current()
            self.assertIs(cur1, cur2)

        with self.subTest('subinterpreter'):
            interp = interpreters.create()
            out = _run_output(interp, dedent("""
                from test.support import interpreters
                cur = interpreters.get_current()
                print(id(cur))
                cur = interpreters.get_current()
                print(id(cur))
                """))
            objid1, objid2 = (int(v) for v in out.splitlines())
            self.assertEqual(objid1, objid2)

        with self.subTest('per-interpreter'):
            interp = interpreters.create()
            out = _run_output(interp, dedent("""
                from test.support import interpreters
                cur = interpreters.get_current()
                print(id(cur))
                """))
            id1 = int(out)
            id2 = id(interp)
            self.assertNotEqual(id1, id2)

    def test_unmanaged(self):
        with self.unmanaged_interpreter() as unmanaged:
            print(unmanaged)
            err = unmanaged.exec(dedent(f"""
                import {interpreters.__name__} as interpreters
                err = None
                try:
                    interpreters.get_current()
                except ValueError as exc:
                    err = exc
                assert exc is not None
                """))
            self.assertEqual(err, '')


class ListAllTests(TestBase):

    def test_initial(self):
        interps = interpreters.list_all()
        self.assertEqual(1, len(interps))

    def test_after_creating(self):
        main = interpreters.get_current()
        first = interpreters.create()
        second = interpreters.create()

        ids = []
        for interp in interpreters.list_all():
            ids.append(interp.id)

        self.assertEqual(ids, [main.id, first.id, second.id])

    def test_after_destroying(self):
        main = interpreters.get_current()
        first = interpreters.create()
        second = interpreters.create()
        first.close()

        ids = []
        for interp in interpreters.list_all():
            ids.append(interp.id)

        self.assertEqual(ids, [main.id, second.id])

    def test_idempotent(self):
        main = interpreters.get_current()
        first = interpreters.create()
        second = interpreters.create()
        expected = [main, first, second]

        actual = interpreters.list_all()

        self.assertEqual(actual, expected)
        for interp1, interp2 in zip(actual, expected):
            self.assertIs(interp1, interp2)

    def test_unmanaged(self):
        ...


class InterpreterObjectTests(TestBase):

    def test_init_int(self):
        interpid = interpreters.get_current().id
        interp = interpreters.Interpreter(interpid)
        self.assertEqual(interp.id, interpid)

    def test_init_interpreter_id(self):
        interpid = interpreters.get_current()._id
        interp = interpreters.Interpreter(interpid)
        self.assertEqual(interp._id, interpid)

    def test_init_unsupported(self):
        actualid = interpreters.get_current().id
        for interpid in [
            str(actualid),
            float(actualid),
            object(),
            None,
            '',
        ]:
            with self.subTest(repr(interpid)):
                with self.assertRaises(TypeError):
                    interpreters.Interpreter(interpid)

    def test_idempotent(self):
        main = interpreters.get_main()
        interp = interpreters.Interpreter(main.id)
        self.assertIs(interp, main)

    def test_init_does_not_exist(self):
        with self.assertRaises(InterpreterNotFoundError):
            interpreters.Interpreter(1_000_000)

    def test_init_bad_id(self):
        with self.assertRaises(ValueError):
            interpreters.Interpreter(-1)

    def test_id_type(self):
        main = interpreters.get_main()
        current = interpreters.get_current()
        interp = interpreters.create()
        self.assertIsInstance(main.id, int)
        self.assertIsInstance(current.id, int)
        self.assertIsInstance(interp.id, int)

    def test_id_readonly(self):
        interp = interpreters.create()
        with self.assertRaises(AttributeError):
            interp.id = 1_000_000

    def test_hashable(self):
        interp = interpreters.create()
        expected = hash(interp.id)
        actual = hash(interp)
        self.assertEqual(actual, expected)

    def test_equality(self):
        interp1 = interpreters.create()
        interp2 = interpreters.create()
        self.assertEqual(interp1, interp1)
        self.assertNotEqual(interp1, interp2)

    def test_pickle(self):
        interp = interpreters.create()
        data = pickle.dumps(interp)
        unpickled = pickle.loads(data)
        self.assertEqual(unpickled, interp)


class TestInterpreterIsRunning(TestBase):

    def test_main(self):
        main = interpreters.get_main()
        self.assertTrue(main.is_running())

    @unittest.skip('Fails on FreeBSD')
    def test_subinterpreter(self):
        interp = interpreters.create()
        self.assertFalse(interp.is_running())

        with _running(interp):
            self.assertTrue(interp.is_running())
        self.assertFalse(interp.is_running())

    def test_finished(self):
        r, w = self.pipe()
        interp = interpreters.create()
        interp.exec(f"""if True:
            import os
            os.write({w}, b'x')
            """)
        self.assertFalse(interp.is_running())
        self.assertEqual(os.read(r, 1), b'x')

    def test_from_subinterpreter(self):
        interp = interpreters.create()
        out = _run_output(interp, dedent(f"""
            import _xxsubinterpreters as _interpreters
            if _interpreters.is_running({interp.id}):
                print(True)
            else:
                print(False)
            """))
        self.assertEqual(out.strip(), 'True')

    def test_already_destroyed(self):
        interp = interpreters.create()
        interp.close()
        with self.assertRaises(InterpreterNotFoundError):
            interp.is_running()

    def test_with_only_background_threads(self):
        r_interp, w_interp = self.pipe()
        r_thread, w_thread = self.pipe()

        DONE = b'D'
        FINISHED = b'F'

        interp = interpreters.create()
        interp.exec(f"""if True:
            import os
            import threading

            def task():
                v = os.read({r_thread}, 1)
                assert v == {DONE!r}
                os.write({w_interp}, {FINISHED!r})
            t = threading.Thread(target=task)
            t.start()
            """)
        self.assertFalse(interp.is_running())

        os.write(w_thread, DONE)
        interp.exec('t.join()')
        self.assertEqual(os.read(r_interp, 1), FINISHED)


class TestInterpreterClose(TestBase):

    def test_basic(self):
        main = interpreters.get_main()
        interp1 = interpreters.create()
        interp2 = interpreters.create()
        interp3 = interpreters.create()
        self.assertEqual(set(interpreters.list_all()),
                         {main, interp1, interp2, interp3})
        interp2.close()
        self.assertEqual(set(interpreters.list_all()),
                         {main, interp1, interp3})

    def test_all(self):
        before = set(interpreters.list_all())
        interps = set()
        for _ in range(3):
            interp = interpreters.create()
            interps.add(interp)
        self.assertEqual(set(interpreters.list_all()), before | interps)
        for interp in interps:
            interp.close()
        self.assertEqual(set(interpreters.list_all()), before)

    def test_main(self):
        main, = interpreters.list_all()
        with self.assertRaises(interpreters.InterpreterError):
            main.close()

        def f():
            with self.assertRaises(interpreters.InterpreterError):
                main.close()

        t = threading.Thread(target=f)
        t.start()
        t.join()

    def test_already_destroyed(self):
        interp = interpreters.create()
        interp.close()
        with self.assertRaises(InterpreterNotFoundError):
            interp.close()

    def test_from_current(self):
        main, = interpreters.list_all()
        interp = interpreters.create()
        out = _run_output(interp, dedent(f"""
            from test.support import interpreters
            interp = interpreters.Interpreter({interp.id})
            try:
                interp.close()
            except interpreters.InterpreterError:
                print('failed')
            """))
        self.assertEqual(out.strip(), 'failed')
        self.assertEqual(set(interpreters.list_all()), {main, interp})

    def test_from_sibling(self):
        main, = interpreters.list_all()
        interp1 = interpreters.create()
        interp2 = interpreters.create()
        self.assertEqual(set(interpreters.list_all()),
                         {main, interp1, interp2})
        interp1.exec(dedent(f"""
            from test.support import interpreters
            interp2 = interpreters.Interpreter({interp2.id})
            interp2.close()
            interp3 = interpreters.create()
            interp3.close()
            """))
        self.assertEqual(set(interpreters.list_all()), {main, interp1})

    def test_from_other_thread(self):
        interp = interpreters.create()
        def f():
            interp.close()

        t = threading.Thread(target=f)
        t.start()
        t.join()

    @unittest.skip('Fails on FreeBSD')
    def test_still_running(self):
        main, = interpreters.list_all()
        interp = interpreters.create()
        with _running(interp):
            with self.assertRaises(interpreters.InterpreterError):
                interp.close()
            self.assertTrue(interp.is_running())

    def test_subthreads_still_running(self):
        r_interp, w_interp = self.pipe()
        r_thread, w_thread = self.pipe()

        FINISHED = b'F'

        interp = interpreters.create()
        interp.exec(f"""if True:
            import os
            import threading
            import time

            done = False

            def notify_fini():
                global done
                done = True
                t.join()
            threading._register_atexit(notify_fini)

            def task():
                while not done:
                    time.sleep(0.1)
                os.write({w_interp}, {FINISHED!r})
            t = threading.Thread(target=task)
            t.start()
            """)
        interp.close()

        self.assertEqual(os.read(r_interp, 1), FINISHED)


class TestInterpreterPrepareMain(TestBase):

    def test_empty(self):
        interp = interpreters.create()
        with self.assertRaises(ValueError):
            interp.prepare_main()

    def test_dict(self):
        values = {'spam': 42, 'eggs': 'ham'}
        interp = interpreters.create()
        interp.prepare_main(values)
        out = _run_output(interp, dedent("""
            print(spam, eggs)
            """))
        self.assertEqual(out.strip(), '42 ham')

    def test_tuple(self):
        values = {'spam': 42, 'eggs': 'ham'}
        values = tuple(values.items())
        interp = interpreters.create()
        interp.prepare_main(values)
        out = _run_output(interp, dedent("""
            print(spam, eggs)
            """))
        self.assertEqual(out.strip(), '42 ham')

    def test_kwargs(self):
        values = {'spam': 42, 'eggs': 'ham'}
        interp = interpreters.create()
        interp.prepare_main(**values)
        out = _run_output(interp, dedent("""
            print(spam, eggs)
            """))
        self.assertEqual(out.strip(), '42 ham')

    def test_dict_and_kwargs(self):
        values = {'spam': 42, 'eggs': 'ham'}
        interp = interpreters.create()
        interp.prepare_main(values, foo='bar')
        out = _run_output(interp, dedent("""
            print(spam, eggs, foo)
            """))
        self.assertEqual(out.strip(), '42 ham bar')

    def test_not_shareable(self):
        interp = interpreters.create()
        # XXX TypeError?
        with self.assertRaises(ValueError):
            interp.prepare_main(spam={'spam': 'eggs', 'foo': 'bar'})

        # Make sure neither was actually bound.
        with self.assertRaises(interpreters.ExecutionFailed):
            interp.exec('print(foo)')
        with self.assertRaises(interpreters.ExecutionFailed):
            interp.exec('print(spam)')


class TestInterpreterExec(TestBase):

    def test_success(self):
        interp = interpreters.create()
        script, file = _captured_script('print("it worked!", end="")')
        with file:
            interp.exec(script)
            out = file.read()

        self.assertEqual(out, 'it worked!')

    def test_failure(self):
        interp = interpreters.create()
        with self.assertRaises(interpreters.ExecutionFailed):
            interp.exec('raise Exception')

    def test_display_preserved_exception(self):
        tempdir = self.temp_dir()
        modfile = self.make_module('spam', tempdir, text="""
            def ham():
                raise RuntimeError('uh-oh!')

            def eggs():
                ham()
            """)
        scriptfile = self.make_script('script.py', tempdir, text="""
            from test.support import interpreters

            def script():
                import spam
                spam.eggs()

            interp = interpreters.create()
            interp.exec(script)
            """)

        stdout, stderr = self.assert_python_failure(scriptfile)
        self.maxDiff = None
        interpmod_line, = (l for l in stderr.splitlines() if ' exec' in l)
        #      File "{interpreters.__file__}", line 179, in exec
        self.assertEqual(stderr, dedent(f"""\
            Traceback (most recent call last):
              File "{scriptfile}", line 9, in <module>
                interp.exec(script)
                ~~~~~~~~~~~^^^^^^^^
              {interpmod_line.strip()}
                raise ExecutionFailed(excinfo)
            test.support.interpreters.ExecutionFailed: RuntimeError: uh-oh!

            Uncaught in the interpreter:

            Traceback (most recent call last):
              File "{scriptfile}", line 6, in script
                spam.eggs()
                ~~~~~~~~~^^
              File "{modfile}", line 6, in eggs
                ham()
                ~~~^^
              File "{modfile}", line 3, in ham
                raise RuntimeError('uh-oh!')
            RuntimeError: uh-oh!
            """))
        self.assertEqual(stdout, '')

    def test_in_thread(self):
        interp = interpreters.create()
        script, file = _captured_script('print("it worked!", end="")')
        with file:
            def f():
                interp.exec(script)

            t = threading.Thread(target=f)
            t.start()
            t.join()
            out = file.read()

        self.assertEqual(out, 'it worked!')

    @support.requires_fork()
    def test_fork(self):
        interp = interpreters.create()
        import tempfile
        with tempfile.NamedTemporaryFile('w+', encoding='utf-8') as file:
            file.write('')
            file.flush()

            expected = 'spam spam spam spam spam'
            script = dedent(f"""
                import os
                try:
                    os.fork()
                except RuntimeError:
                    with open('{file.name}', 'w', encoding='utf-8') as out:
                        out.write('{expected}')
                """)
            interp.exec(script)

            file.seek(0)
            content = file.read()
            self.assertEqual(content, expected)

    @unittest.skip('Fails on FreeBSD')
    def test_already_running(self):
        interp = interpreters.create()
        with _running(interp):
            with self.assertRaises(RuntimeError):
                interp.exec('print("spam")')

    def test_bad_script(self):
        interp = interpreters.create()
        with self.assertRaises(TypeError):
            interp.exec(10)

    def test_bytes_for_script(self):
        interp = interpreters.create()
        with self.assertRaises(TypeError):
            interp.exec(b'print("spam")')

    def test_with_background_threads_still_running(self):
        r_interp, w_interp = self.pipe()
        r_thread, w_thread = self.pipe()

        RAN = b'R'
        DONE = b'D'
        FINISHED = b'F'

        interp = interpreters.create()
        interp.exec(f"""if True:
            import os
            import threading

            def task():
                v = os.read({r_thread}, 1)
                assert v == {DONE!r}
                os.write({w_interp}, {FINISHED!r})
            t = threading.Thread(target=task)
            t.start()
            os.write({w_interp}, {RAN!r})
            """)
        interp.exec(f"""if True:
            os.write({w_interp}, {RAN!r})
            """)

        os.write(w_thread, DONE)
        interp.exec('t.join()')
        self.assertEqual(os.read(r_interp, 1), RAN)
        self.assertEqual(os.read(r_interp, 1), RAN)
        self.assertEqual(os.read(r_interp, 1), FINISHED)

    # test_xxsubinterpreters covers the remaining
    # Interpreter.exec() behavior.


def call_func_noop():
    pass


def call_func_return_shareable():
    return (1, None)


def call_func_return_not_shareable():
    return [1, 2, 3]


def call_func_failure():
    raise Exception('spam!')


def call_func_ident(value):
    return value


def get_call_func_closure(value):
    def call_func_closure():
        return value
    return call_func_closure


class Spam:

    @staticmethod
    def noop():
        pass

    @classmethod
    def from_values(cls, *values):
        return cls(values)

    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return (self.value, args, kwargs)

    def __eq__(self, other):
        if not isinstance(other, Spam):
            return NotImplemented
        return self.value == other.value

    def run(self, *args, **kwargs):
        return (self.value, args, kwargs)


def call_func_complex(op, /, value=None, *args, exc=None, **kwargs):
    if exc is not None:
        raise exc
    if op == '':
        raise ValueError('missing op')
    elif op == 'ident':
        if args or kwargs:
            raise Exception((args, kwargs))
        return value
    elif op == 'full-ident':
        return (value, args, kwargs)
    elif op == 'globals':
        if value is not None or args or kwargs:
            raise Exception((value, args, kwargs))
        return __name__
    elif op == 'interpid':
        if value is not None or args or kwargs:
            raise Exception((value, args, kwargs))
        return interpreters.get_current().id
    elif op == 'closure':
        if args or kwargs:
            raise Exception((args, kwargs))
        return get_call_func_closure(value)
    elif op == 'custom':
        if args or kwargs:
            raise Exception((args, kwargs))
        return Spam(value)
    elif op == 'custom-inner':
        if args or kwargs:
            raise Exception((args, kwargs))
        class Eggs(Spam):
            pass
        return Eggs(value)
    elif not isinstance(op, str):
        raise TypeError(op)
    else:
        raise NotImplementedError(op)


class TestInterpreterCall(TestBase):

    # signature
    #  - blank
    #  - args
    #  - kwargs
    #  - args, kwargs
    # return
    #  - nothing (None)
    #  - simple
    #  - closure
    #  - custom
    # ops:
    #  - do nothing
    #  - fail
    #  - echo
    #  - do complex, relative to interpreter
    # scope
    #  - global func
    #  - local closure
    #  - returned closure
    #  - callable type instance
    #  - type
    #  - classmethod
    #  - staticmethod
    #  - instance method
    # exception
    #  - builtin
    #  - custom
    #  - preserves info (e.g. SyntaxError)
    #  - matching error display

    def test_call(self):
        interp = interpreters.create()

        for i, (callable, args, kwargs) in enumerate([
            (call_func_noop, (), {}),
            (call_func_return_shareable, (), {}),
            (call_func_return_not_shareable, (), {}),
            (Spam.noop, (), {}),
        ]):
            with self.subTest(f'success case #{i+1}'):
                res = interp.call(callable)
                self.assertIs(res, None)

        for i, (callable, args, kwargs) in enumerate([
            (call_func_ident, ('spamspamspam',), {}),
            (get_call_func_closure, (42,), {}),
            (get_call_func_closure(42), (), {}),
            (Spam.from_values, (), {}),
            (Spam.from_values, (1, 2, 3), {}),
            (Spam, ('???'), {}),
            (Spam(101), (), {}),
            (Spam(10101).run, (), {}),
            (call_func_complex, ('ident', 'spam'), {}),
            (call_func_complex, ('full-ident', 'spam'), {}),
            (call_func_complex, ('full-ident', 'spam', 'ham'), {'eggs': '!!!'}),
            (call_func_complex, ('globals',), {}),
            (call_func_complex, ('interpid',), {}),
            (call_func_complex, ('closure',), {'value': '~~~'}),
            (call_func_complex, ('custom', 'spam!'), {}),
            (call_func_complex, ('custom-inner', 'eggs!'), {}),
            (call_func_complex, ('???',), {'exc': ValueError('spam')}),
        ]):
            with self.subTest(f'invalid case #{i+1}'):
                with self.assertRaises(Exception):
                    if args or kwargs:
                        raise Exception((args, kwargs))
                    interp.call(callable)

        with self.assertRaises(interpreters.ExecutionFailed):
            interp.call(call_func_failure)

    def test_call_in_thread(self):
        interp = interpreters.create()

        for i, (callable, args, kwargs) in enumerate([
            (call_func_noop, (), {}),
            (call_func_return_shareable, (), {}),
            (call_func_return_not_shareable, (), {}),
            (Spam.noop, (), {}),
        ]):
            with self.subTest(f'success case #{i+1}'):
                with self.captured_thread_exception() as ctx:
                    t = interp.call_in_thread(callable)
                    t.join()
                self.assertIsNone(ctx.caught)

        for i, (callable, args, kwargs) in enumerate([
            (call_func_ident, ('spamspamspam',), {}),
            (get_call_func_closure, (42,), {}),
            (get_call_func_closure(42), (), {}),
            (Spam.from_values, (), {}),
            (Spam.from_values, (1, 2, 3), {}),
            (Spam, ('???'), {}),
            (Spam(101), (), {}),
            (Spam(10101).run, (), {}),
            (call_func_complex, ('ident', 'spam'), {}),
            (call_func_complex, ('full-ident', 'spam'), {}),
            (call_func_complex, ('full-ident', 'spam', 'ham'), {'eggs': '!!!'}),
            (call_func_complex, ('globals',), {}),
            (call_func_complex, ('interpid',), {}),
            (call_func_complex, ('closure',), {'value': '~~~'}),
            (call_func_complex, ('custom', 'spam!'), {}),
            (call_func_complex, ('custom-inner', 'eggs!'), {}),
            (call_func_complex, ('???',), {'exc': ValueError('spam')}),
        ]):
            with self.subTest(f'invalid case #{i+1}'):
                if args or kwargs:
                    continue
                with self.captured_thread_exception() as ctx:
                    t = interp.call_in_thread(callable)
                    t.join()
                self.assertIsNotNone(ctx.caught)

        with self.captured_thread_exception() as ctx:
            t = interp.call_in_thread(call_func_failure)
            t.join()
        self.assertIsNotNone(ctx.caught)


class TestIsShareable(TestBase):

    def test_default_shareables(self):
        shareables = [
                # singletons
                None,
                # builtin objects
                b'spam',
                'spam',
                10,
                -10,
                True,
                False,
                100.0,
                (),
                (1, ('spam', 'eggs'), True),
                ]
        for obj in shareables:
            with self.subTest(obj):
                shareable = interpreters.is_shareable(obj)
                self.assertTrue(shareable)

    def test_not_shareable(self):
        class Cheese:
            def __init__(self, name):
                self.name = name
            def __str__(self):
                return self.name

        class SubBytes(bytes):
            """A subclass of a shareable type."""

        not_shareables = [
                # singletons
                NotImplemented,
                ...,
                # builtin types and objects
                type,
                object,
                object(),
                Exception(),
                # user-defined types and objects
                Cheese,
                Cheese('Wensleydale'),
                SubBytes(b'spam'),
                ]
        for obj in not_shareables:
            with self.subTest(repr(obj)):
                self.assertFalse(
                    interpreters.is_shareable(obj))


class LowLevelTests(TestBase):

    # The behaviors in the low-level module are important in as much
    # as they are exercised by the high-level module.  Therefore the
    # most important testing happens in the high-level tests.
    # These low-level tests cover corner cases that are not
    # encountered by the high-level module, thus they
    # mostly shouldn't matter as much.

    def _run_string(self, interpid, script, maxout):
        with CapturingScript(script, combined=False) as captured:
            err = _interpreters.run_string(interpid, captured.script)
            if err is not None:
                return None, err
            raw = b''
            #raw = captured.read(maxout)
        return raw.decode('utf-8'), None

    def run_and_capture(self, interpid, script, maxout=1000):
        text, err = self._run_string(interpid, script, maxout)
        if err is not None:
            print()
            print(err.errdisplay, file=sys.stderr)
            raise Exception(f'subinterpreter failed: {err.formatted}')
        else:
            return text

    def test_new_config(self):
        # This test overlaps with
        # test.test_capi.test_misc.InterpreterConfigTests.

        default = _interpreters.new_config('isolated')
        with self.subTest('no arg'):
            config = _interpreters.new_config()
            self.assert_ns_equal(config, default)
            self.assertIsNot(config, default)

        with self.subTest('default'):
            config1 = _interpreters.new_config('default')
            self.assert_ns_equal(config1, default)
            self.assertIsNot(config1, default)

            config2 = _interpreters.new_config('default')
            self.assert_ns_equal(config2, config1)
            self.assertIsNot(config2, config1)

        for arg in ['', 'default']:
            with self.subTest(f'default ({arg!r})'):
                config = _interpreters.new_config(arg)
                self.assert_ns_equal(config, default)
                self.assertIsNot(config, default)

        supported = {
            'isolated': types.SimpleNamespace(
                use_main_obmalloc=False,
                allow_fork=False,
                allow_exec=False,
                allow_threads=True,
                allow_daemon_threads=False,
                check_multi_interp_extensions=True,
                gil='own',
            ),
            'legacy': types.SimpleNamespace(
                use_main_obmalloc=True,
                allow_fork=True,
                allow_exec=True,
                allow_threads=True,
                allow_daemon_threads=True,
                check_multi_interp_extensions=False,
                gil='shared',
            ),
            'empty': types.SimpleNamespace(
                use_main_obmalloc=False,
                allow_fork=False,
                allow_exec=False,
                allow_threads=False,
                allow_daemon_threads=False,
                check_multi_interp_extensions=False,
                gil='default',
            ),
        }
        gil_supported = ['default', 'shared', 'own']

        for name, vanilla in supported.items():
            with self.subTest(f'supported ({name})'):
                expected = vanilla
                config1 = _interpreters.new_config(name)
                self.assert_ns_equal(config1, expected)
                self.assertIsNot(config1, expected)

                config2 = _interpreters.new_config(name)
                self.assert_ns_equal(config2, config1)
                self.assertIsNot(config2, config1)

            with self.subTest(f'noop override ({name})'):
                expected = vanilla
                overrides = vars(vanilla)
                config = _interpreters.new_config(name, **overrides)
                self.assert_ns_equal(config, expected)

            with self.subTest(f'override all ({name})'):
                overrides = {k: not v for k, v in vars(vanilla).items()}
                for gil in gil_supported:
                    if vanilla.gil == gil:
                        continue
                    overrides['gil'] = gil
                    expected = types.SimpleNamespace(**overrides)
                    config = _interpreters.new_config(name, **overrides)
                    self.assert_ns_equal(config, expected)

            # Override individual fields.
            for field, old in vars(vanilla).items():
                if field == 'gil':
                    values = [v for v in gil_supported if v != old]
                else:
                    values = [not old]
                for val in values:
                    with self.subTest(f'{name}.{field} ({old!r} -> {val!r})'):
                        overrides = {field: val}
                        expected = types.SimpleNamespace(
                            **dict(vars(vanilla), **overrides),
                        )
                        config = _interpreters.new_config(name, **overrides)
                        self.assert_ns_equal(config, expected)

        with self.subTest('extra override'):
            with self.assertRaises(ValueError):
                _interpreters.new_config(spam=True)

        # Bad values for bool fields.
        for field, value in vars(supported['empty']).items():
            if field == 'gil':
                continue
            assert isinstance(value, bool)
            for value in [1, '', 'spam', 1.0, None, object()]:
                with self.subTest(f'bad override ({field}={value!r})'):
                    with self.assertRaises(TypeError):
                        _interpreters.new_config(**{field: value})

        # Bad values for .gil.
        for value in [True, 1, 1.0, None, object()]:
            with self.subTest(f'bad override (gil={value!r})'):
                with self.assertRaises(TypeError):
                    _interpreters.new_config(gil=value)
        for value in ['', 'spam']:
            with self.subTest(f'bad override (gil={value!r})'):
                with self.assertRaises(ValueError):
                    _interpreters.new_config(gil=value)

    def test_get_config(self):
        # This test overlaps with
        # test.test_capi.test_misc.InterpreterConfigTests.

        with self.subTest('main'):
            expected = _interpreters.new_config('legacy')
            expected.gil = 'own'
            interpid, _ = _interpreters.get_main()
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, expected)

    def test_get_main(self):
        interpid, owned = _interpreters.get_main()
        self.assertEqual(interpid, 0)
        self.assertFalse(owned)

    def test_get_current(self):
        with self.subTest('main'):
            main, _ = _interpreters.get_main()
            interpid, owned = _interpreters.get_current()
            self.assertEqual(interpid, main)
            self.assertFalse(owned)

        with self.subTest('owned'):
            orig = _interpreters.create()
            text = self.run_and_capture(orig, f"""
                import {_interpreters.__name__} as _interpreters
                interpid, owned = _interpreters.get_current()
                print(interpid)
                print(owned)
                """)
            parts = text.split()
            assert len(parts) == 2, parts
            interpid, owned = parts
            interpid = int(interpid)
            owned = eval(owned)
            self.assertEqual(interpid, orig)
            self.assertTrue(owned)

        with self.subTest('external'):
            err, text = self.run_external(f"""
                import {_interpreters.__name__} as _interpreters
                interpid, owned = _interpreters.get_current()
                print(interpid)
                print(owned)
                """)
            assert err is None, err
            interpid, owned = text.split()
            interpid = int(interpid)
            owned = eval(owned)
            self.assertEqual(interpid, orig)
            self.assertTrue(owned)

    def test_list_all(self):
        ...

    def test_create(self):
        isolated = _interpreters.new_config('isolated')
        legacy = _interpreters.new_config('legacy')
        default = isolated

        with self.subTest('no arg'):
            interpid = _interpreters.create()
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, default)

        with self.subTest('arg: None'):
            interpid = _interpreters.create(None)
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, default)

        with self.subTest('arg: \'empty\''):
            with self.assertRaises(interpreters.InterpreterError):
                # The "empty" config isn't viable on its own.
                _interpreters.create('empty')

        for arg, expected in {
            '': default,
            'default': default,
            'isolated': isolated,
            'legacy': legacy,
        }.items():
            with self.subTest(f'str arg: {arg!r}'):
                interpid = _interpreters.create(arg)
                config = _interpreters.get_config(interpid)
                self.assert_ns_equal(config, expected)

        with self.subTest('custom'):
            orig = _interpreters.new_config('empty')
            orig.use_main_obmalloc = True
            orig.gil = 'shared'
            interpid = _interpreters.create(orig)
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, orig)

        with self.subTest('missing fields'):
            orig = _interpreters.new_config()
            del orig.gil
            with self.assertRaises(ValueError):
                _interpreters.create(orig)

        with self.subTest('extra fields'):
            orig = _interpreters.new_config()
            orig.spam = True
            with self.assertRaises(ValueError):
                _interpreters.create(orig)

    def test_get_config(self):
        with self.subTest('main'):
            expected = _interpreters.new_config('legacy')
            expected.gil = 'own'
            interpid, _ = _interpreters.get_main()
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, expected)

        with self.subTest('isolated'):
            expected = _interpreters.new_config('isolated')
            interpid = _interpreters.create('isolated')
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, expected)

        with self.subTest('legacy'):
            expected = _interpreters.new_config('legacy')
            interpid = _interpreters.create('legacy')
            config = _interpreters.get_config(interpid)
            self.assert_ns_equal(config, expected)


if __name__ == '__main__':
    # Test needs to be a package, so we can do relative imports.
    unittest.main()
