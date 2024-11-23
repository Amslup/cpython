import ctypes
import gc
import sys
import unittest
from ctypes import POINTER, byref, c_void_p
from ctypes.wintypes import BYTE, DWORD, WORD

if sys.platform != "win32":
    raise unittest.SkipTest("Windows-specific test")


from _ctypes import COMError, CopyComPointer
from ctypes import HRESULT


COINIT_APARTMENTTHREADED = 0x2
CLSCTX_SERVER = 5
S_OK = 0
OUT = 2
TRUE = 1
E_NOINTERFACE = -2147467262


class GUID(ctypes.Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/guiddef/ns-guiddef-guid
    _fields_ = [
        ("Data1", DWORD),
        ("Data2", WORD),
        ("Data3", WORD),
        ("Data4", BYTE * 8),
    ]


def create_proto_com_method(name, index, restype, *argtypes):
    proto = ctypes.WINFUNCTYPE(restype, *argtypes)

    def make_method(*args):
        foreign_func = proto(index, name, *args)

        def call(self, *args, **kwargs):
            return foreign_func(self, *args, **kwargs)

        return call

    return make_method


def create_guid(name):
    guid = GUID()
    # https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-clsidfromstring
    ole32.CLSIDFromString(name, byref(guid))
    return guid


def is_equal_guid(guid1, guid2):
    # https://learn.microsoft.com/en-us/windows/win32/api/objbase/nf-objbase-isequalguid
    return ole32.IsEqualGUID(byref(guid1), byref(guid2))


ole32 = ctypes.oledll.ole32

IID_IUnknown = create_guid("{00000000-0000-0000-C000-000000000046}")
IID_IStream = create_guid("{0000000C-0000-0000-C000-000000000046}")
IID_IPersist = create_guid("{0000010C-0000-0000-C000-000000000046}")
CLSID_ShellLink = create_guid("{00021401-0000-0000-C000-000000000046}")

# https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-queryinterface(refiid_void)
proto_query_interface = create_proto_com_method(
    "QueryInterface", 0, HRESULT, POINTER(GUID), POINTER(c_void_p)
)
# https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-addref
proto_add_ref = create_proto_com_method("AddRef", 1, ctypes.c_long)
# https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-release
proto_release = create_proto_com_method("Release", 2, ctypes.c_long)
# https://learn.microsoft.com/en-us/windows/win32/api/objidl/nf-objidl-ipersist-getclassid
proto_get_class_id = create_proto_com_method(
    "GetClassID", 3, HRESULT, POINTER(GUID)
)


def create_shelllink_persist(typ):
    ppst = typ()
    # https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance
    ole32.CoCreateInstance(
        byref(CLSID_ShellLink),
        None,
        CLSCTX_SERVER,
        byref(IID_IPersist),
        byref(ppst),
    )
    return ppst


class ForeignFunctionsThatWillCallComMethodsTests(unittest.TestCase):
    def setUp(self):
        # https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coinitializeex
        ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)

    def tearDown(self):
        # https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-couninitialize
        ole32.CoUninitialize()
        gc.collect()

    def test_without_paramflags_and_iid(self):
        class IUnknown(c_void_p):
            QueryInterface = proto_query_interface()
            AddRef = proto_add_ref()
            Release = proto_release()

        class IPersist(IUnknown):
            GetClassID = proto_get_class_id()

        ppst = create_shelllink_persist(IPersist)

        clsid = GUID()
        hr_getclsid = ppst.GetClassID(byref(clsid))
        self.assertEqual(S_OK, hr_getclsid)
        self.assertEqual(TRUE, is_equal_guid(CLSID_ShellLink, clsid))

        self.assertEqual(2, ppst.AddRef())
        self.assertEqual(3, ppst.AddRef())

        punk = IUnknown()
        hr_qi = ppst.QueryInterface(IID_IUnknown, punk)
        self.assertEqual(S_OK, hr_qi)
        self.assertEqual(3, punk.Release())

        with self.assertRaises(OSError) as e:
            punk.QueryInterface(IID_IStream, IUnknown())
        self.assertEqual(E_NOINTERFACE, e.exception.winerror)

        self.assertEqual(2, ppst.Release())
        self.assertEqual(1, ppst.Release())
        self.assertEqual(0, ppst.Release())

    def test_with_paramflags_and_without_iid(self):
        class IUnknown(c_void_p):
            QueryInterface = proto_query_interface(None)
            AddRef = proto_add_ref()
            Release = proto_release()

        class IPersist(IUnknown):
            GetClassID = proto_get_class_id(((OUT, "pClassID"),))

        ppst = create_shelllink_persist(IPersist)

        clsid = ppst.GetClassID()
        self.assertEqual(TRUE, is_equal_guid(CLSID_ShellLink, clsid))

        punk = IUnknown()
        hr_qi = ppst.QueryInterface(IID_IUnknown, punk)
        self.assertEqual(S_OK, hr_qi)
        self.assertEqual(1, punk.Release())

        with self.assertRaises(OSError) as e:
            ppst.QueryInterface(IID_IStream, IUnknown())
        self.assertEqual(E_NOINTERFACE, e.exception.winerror)

        self.assertEqual(0, ppst.Release())

    def test_with_paramflags_and_iid(self):
        class IUnknown(c_void_p):
            QueryInterface = proto_query_interface(None, IID_IUnknown)
            AddRef = proto_add_ref()
            Release = proto_release()

        class IPersist(IUnknown):
            GetClassID = proto_get_class_id(((OUT, "pClassID"),), IID_IPersist)

        ppst = create_shelllink_persist(IPersist)

        clsid = ppst.GetClassID()
        self.assertEqual(TRUE, is_equal_guid(CLSID_ShellLink, clsid))

        punk = IUnknown()
        hr_qi = ppst.QueryInterface(IID_IUnknown, punk)
        self.assertEqual(S_OK, hr_qi)
        self.assertEqual(1, punk.Release())

        with self.assertRaises(COMError) as e:
            ppst.QueryInterface(IID_IStream, IUnknown())
        self.assertEqual(E_NOINTERFACE, e.exception.hresult)

        self.assertEqual(0, ppst.Release())


class CopyComPointerTests(unittest.TestCase):
    def setUp(self):
        ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)

    def tearDown(self):
        ole32.CoUninitialize()
        gc.collect()

    def test_copy_com_pointer(self):
        class IUnknown(c_void_p):
            QueryInterface = proto_query_interface(None, IID_IUnknown)
            AddRef = proto_add_ref()
            Release = proto_release()

        class IPersist(IUnknown):
            GetClassID = proto_get_class_id(((OUT, "pClassID"),), IID_IPersist)

        src = create_shelllink_persist(IPersist)
        dst = IPersist()

        self.assertIsNone(dst.value)
        with self.assertRaises(ValueError):
            dst.GetClassID()  # NULL COM pointer access

        hr = CopyComPointer(src, byref(dst))

        self.assertEqual(S_OK, hr)
        self.assertEqual(dst.value, src.value)

        clsid = dst.GetClassID()
        self.assertEqual(TRUE, is_equal_guid(CLSID_ShellLink, clsid))

        # The refcount of a COM pointer created by `CoCreateInstance` is 1.
        # `CopyComPointer` calls `AddRef` internally (thus, +1 to the refcount).
        # Here, the refcount is decremented from 2 to 1.
        self.assertEqual(1, dst.Release())
        self.assertEqual(0, src.Release())


if __name__ == '__main__':
    unittest.main()
