#ifndef Py_INTERNAL_CODE_H
#define Py_INTERNAL_CODE_H
#ifdef __cplusplus
extern "C" {
#endif
 
typedef struct {
    PyObject *ptr;  /* Cached pointer (borrowed reference) */
    uint64_t globals_ver;  /* ma_version of global dict */
    uint64_t builtins_ver; /* ma_version of builtin dict */
} _PyOpcache_LoadGlobal;

typedef struct {
    PyTypeObject *type;
    Py_ssize_t hint;
    unsigned int tp_version_tag;
} _PyOpCodeOpt_LoadAttr;

struct _PyOpcache {
    union {
        _PyOpcache_LoadGlobal lg;
        _PyOpCodeOpt_LoadAttr la;
    } u;
    char optimized;
};


struct _PyCodeConstructor {
    /* metadata */
    PyObject *filename;
    PyObject *name;
    int flags;

    /* the code */
    PyObject *code;
    int firstlineno;
    PyObject *linetable;

	/* used by the code */
    PyObject *consts;
    PyObject *names;

	/* mapping frame offsets to information */
    PyObject *varnames;
    PyObject *cellvars;
    PyObject *freevars;

    /* args (within varnames) */
    int argcount;
    int posonlyargcount;
    int kwonlyargcount;

    /* needed to create the frame */
    int stacksize;

	/* used by the eval loop */
    PyObject *exceptiontable;
};

PyAPI_FUNC(PyCodeObject *) _PyCode_New(struct _PyCodeConstructor *);


/* Private API */

int _PyCode_InitOpcache(PyCodeObject *co);


#ifdef __cplusplus
}
#endif
#endif /* !Py_INTERNAL_CODE_H */
