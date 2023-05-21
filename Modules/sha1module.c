/* SHA1 module */

/* This module provides an interface to the SHA1 algorithm */

/* See below for information about the original code this module was
   based upon. Additional work performed by:

   Andrew Kuchling (amk@amk.ca)
   Greg Stein (gstein@lyra.org)
   Trevor Perrin (trevp@trevp.net)

   Copyright (C) 2005-2007   Gregory P. Smith (greg@krypto.org)
   Licensed to PSF under a Contributor Agreement.

*/

/* SHA1 objects */
#ifndef Py_BUILD_CORE_BUILTIN
#  define Py_BUILD_CORE_MODULE 1
#endif

#include "Python.h"
#include "hashlib.h"
#include "pycore_strhex.h"        // _Py_strhex()
#include "pycore_typeobject.h"    // _PyType_GetModuleState()

/*[clinic input]
module _sha1
class SHA1Type "SHA1object *" "&PyType_Type"
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=3dc9a20d1becb759]*/

/* Some useful types */

#if SIZEOF_INT == 4
typedef unsigned int SHA1_INT32;        /* 32-bit integer */
typedef long long SHA1_INT64;        /* 64-bit integer */
#else
/* not defined. compilation will die. */
#endif

/* The SHA1 block size and message digest sizes, in bytes */

#define SHA1_BLOCKSIZE    64
#define SHA1_DIGESTSIZE   20

#include "_hacl/Hacl_Hash_SHA1.h"

typedef struct {
    PyObject_HEAD

    Hacl_Streaming_SHA1_state *hash_state;
} SHA1object;

#include "clinic/sha1module.c.h"


typedef struct {
    PyTypeObject* sha1_type;
} SHA1State;

static inline SHA1State*
sha1_get_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (SHA1State *)state;
}

static SHA1object *
newSHA1object(SHA1State *st)
{
    SHA1object *sha = (SHA1object *)PyObject_GC_New(SHA1object, st->sha1_type);
    PyObject_GC_Track(sha);
    return sha;
}


/* Internal methods for a hash object */
static int
SHA1_traverse(PyObject *ptr, visitproc visit, void *arg)
{
    Py_VISIT(Py_TYPE(ptr));
    return 0;
}

static void
SHA1_dealloc(SHA1object *ptr)
{
    Hacl_Streaming_SHA1_legacy_free(ptr->hash_state);
    PyTypeObject *tp = Py_TYPE(ptr);
    PyObject_GC_UnTrack(ptr);
    PyObject_GC_Del(ptr);
    Py_DECREF(tp);
}


/* External methods for a hash object */

/*[clinic input]
SHA1Type.copy

    cls: defining_class

Return a copy of the hash object.
[clinic start generated code]*/

static PyObject *
SHA1Type_copy_impl(SHA1object *self, PyTypeObject *cls)
/*[clinic end generated code: output=b32d4461ce8bc7a7 input=6c22e66fcc34c58e]*/
{
    SHA1State *st = _PyType_GetModuleState(cls);

    SHA1object *newobj;
    if ((newobj = newSHA1object(st)) == NULL)
        return NULL;

    newobj->hash_state = Hacl_Streaming_SHA1_legacy_copy(self->hash_state);
    return (PyObject *)newobj;
}

/*[clinic input]
SHA1Type.digest

Return the digest value as a bytes object.
[clinic start generated code]*/

static PyObject *
SHA1Type_digest_impl(SHA1object *self)
/*[clinic end generated code: output=2f05302a7aa2b5cb input=13824b35407444bd]*/
{
    unsigned char digest[SHA1_DIGESTSIZE];
    Hacl_Streaming_SHA1_legacy_finish(self->hash_state, digest);
    return PyBytes_FromStringAndSize((const char *)digest, SHA1_DIGESTSIZE);
}

/*[clinic input]
SHA1Type.hexdigest

Return the digest value as a string of hexadecimal digits.
[clinic start generated code]*/

static PyObject *
SHA1Type_hexdigest_impl(SHA1object *self)
/*[clinic end generated code: output=4161fd71e68c6659 input=97691055c0c74ab0]*/
{
    unsigned char digest[SHA1_DIGESTSIZE];
    Hacl_Streaming_SHA1_legacy_finish(self->hash_state, digest);
    return _Py_strhex((const char *)digest, SHA1_DIGESTSIZE);
}

static void update(Hacl_Streaming_SHA1_state *state, uint8_t *buf, Py_ssize_t len) {
#if PY_SSIZE_T_MAX > UINT32_MAX
  while (len > UINT32_MAX) {
    Hacl_Streaming_SHA1_legacy_update(state, buf, UINT32_MAX);
    len -= UINT32_MAX;
    buf += UINT32_MAX;
  }
#endif
  Hacl_Streaming_SHA1_legacy_update(state, buf, (uint32_t) len);
}

/*[clinic input]
SHA1Type.update

    obj: object
    /

Update this hash object's state with the provided string.
[clinic start generated code]*/

static PyObject *
SHA1Type_update(SHA1object *self, PyObject *obj)
/*[clinic end generated code: output=d9902f0e5015e9ae input=aad8e07812edbba3]*/
{
    Py_buffer buf;

    GET_BUFFER_VIEW_OR_ERROUT(obj, &buf);

    update(self->hash_state, buf.buf, buf.len);

    PyBuffer_Release(&buf);
    Py_RETURN_NONE;
}

static PyMethodDef SHA1_methods[] = {
    SHA1TYPE_COPY_METHODDEF
    SHA1TYPE_DIGEST_METHODDEF
    SHA1TYPE_HEXDIGEST_METHODDEF
    SHA1TYPE_UPDATE_METHODDEF
    {NULL,        NULL}         /* sentinel */
};

static PyObject *
SHA1_get_block_size(PyObject *self, void *closure)
{
    return PyLong_FromLong(SHA1_BLOCKSIZE);
}

static PyObject *
SHA1_get_name(PyObject *self, void *closure)
{
    return PyUnicode_FromStringAndSize("sha1", 4);
}

static PyObject *
sha1_get_digest_size(PyObject *self, void *closure)
{
    return PyLong_FromLong(SHA1_DIGESTSIZE);
}

static PyGetSetDef SHA1_getseters[] = {
    {"block_size",
     (getter)SHA1_get_block_size, NULL,
     NULL,
     NULL},
    {"name",
     (getter)SHA1_get_name, NULL,
     NULL,
     NULL},
    {"digest_size",
     (getter)sha1_get_digest_size, NULL,
     NULL,
     NULL},
    {NULL}  /* Sentinel */
};

static PyType_Slot sha1_type_slots[] = {
    {Py_tp_dealloc, SHA1_dealloc},
    {Py_tp_methods, SHA1_methods},
    {Py_tp_getset, SHA1_getseters},
    {Py_tp_traverse, SHA1_traverse},
    {0,0}
};

static PyType_Spec sha1_type_spec = {
    .name = "_sha1.sha1",
    .basicsize =  sizeof(SHA1object),
    .flags = (Py_TPFLAGS_DEFAULT | Py_TPFLAGS_DISALLOW_INSTANTIATION |
              Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_HAVE_GC),
    .slots = sha1_type_slots
};

/* The single module-level function: new() */

/*[clinic input]
_sha1.sha1

    string: object(c_default="NULL") = b''
    *
    usedforsecurity: bool = True

Return a new SHA1 hash object; optionally initialized with a string.
[clinic start generated code]*/

static PyObject *
_sha1_sha1_impl(PyObject *module, PyObject *string, int usedforsecurity)
/*[clinic end generated code: output=6f8b3af05126e18e input=bd54b68e2bf36a8a]*/
{
    SHA1object *new;
    Py_buffer buf;

    if (string)
        GET_BUFFER_VIEW_OR_ERROUT(string, &buf);

    SHA1State *st = sha1_get_state(module);
    if ((new = newSHA1object(st)) == NULL) {
        if (string)
            PyBuffer_Release(&buf);
        return NULL;
    }

    new->hash_state = Hacl_Streaming_SHA1_legacy_create_in();

    if (PyErr_Occurred()) {
        Py_DECREF(new);
        if (string)
            PyBuffer_Release(&buf);
        return NULL;
    }
    if (string) {
        update(new->hash_state, buf.buf, buf.len);
        PyBuffer_Release(&buf);
    }

    return (PyObject *)new;
}


/* List of functions exported by this module */

static struct PyMethodDef SHA1_functions[] = {
    _SHA1_SHA1_METHODDEF
    {NULL,      NULL}            /* Sentinel */
};

static int
_sha1_traverse(PyObject *module, visitproc visit, void *arg)
{
    SHA1State *state = sha1_get_state(module);
    Py_VISIT(state->sha1_type);
    return 0;
}

static int
_sha1_clear(PyObject *module)
{
    SHA1State *state = sha1_get_state(module);
    Py_CLEAR(state->sha1_type);
    return 0;
}

static void
_sha1_free(void *module)
{
    _sha1_clear((PyObject *)module);
}

static int
_sha1_exec(PyObject *module)
{
    SHA1State* st = sha1_get_state(module);

    st->sha1_type = (PyTypeObject *)PyType_FromModuleAndSpec(
        module, &sha1_type_spec, NULL);

    if (st->sha1_type == NULL) {
        return -1;
    }

    Py_INCREF(st->sha1_type);
    if (PyModule_AddObject(module,
                           "SHA1Type",
                           (PyObject *)st->sha1_type) < 0) {
        Py_DECREF(st->sha1_type);
        return -1;
    }

    return 0;
}


/* Initialize this module. */

static PyModuleDef_Slot _sha1_slots[] = {
    {Py_mod_exec, _sha1_exec},
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    {0, NULL}
};

static struct PyModuleDef _sha1module = {
        PyModuleDef_HEAD_INIT,
        .m_name = "_sha1",
        .m_size = sizeof(SHA1State),
        .m_methods = SHA1_functions,
        .m_slots = _sha1_slots,
        .m_traverse = _sha1_traverse,
        .m_clear = _sha1_clear,
        .m_free = _sha1_free
};

PyMODINIT_FUNC
PyInit__sha1(void)
{
    return PyModuleDef_Init(&_sha1module);
}
