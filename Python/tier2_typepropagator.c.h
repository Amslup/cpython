// This file is generated by Tools/cases_generator/generate_cases.py @TODO: make this a seperate argument
// from:
//   Python/bytecodes.c
// Do not edit!

        TARGET(NOP) {
            break;
        }

        TARGET(RESUME) {
            break;
        }

        TARGET(RESUME_QUICK) {
            break;
        }

        TARGET(LOAD_CLOSURE) {
            STACK_GROW(1);
            TYPE_OVERWRITE(TYPELOCALS_GET(oparg), TYPESTACK_PEEK(1), false);
            break;
        }

        TARGET(LOAD_FAST_CHECK) {
            STACK_GROW(1);
            TYPE_OVERWRITE(TYPELOCALS_GET(oparg), TYPESTACK_PEEK(1), false);
            break;
        }

        TARGET(LOAD_FAST) {
            STACK_GROW(1);
            TYPE_OVERWRITE(TYPELOCALS_GET(oparg), TYPESTACK_PEEK(1), false);
            break;
        }

        TARGET(LOAD_FAST_NO_INCREF) {
            STACK_GROW(1);
            TYPE_OVERWRITE(TYPELOCALS_GET(oparg), TYPESTACK_PEEK(1), false);
            break;
        }

        TARGET(LOAD_CONST) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)TYPECONST_GET(oparg), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(STORE_FAST) {
            _Py_TYPENODE_t *value = TYPESTACK_PEEK(1);
            TYPE_OVERWRITE(value, TYPELOCALS_GET(oparg), false);
            STACK_SHRINK(1);
            break;
        }

        TARGET(STORE_FAST_BOXED_UNBOXED) {
            _Py_TYPENODE_t *value = TYPESTACK_PEEK(1);
            TYPE_OVERWRITE(value, TYPELOCALS_GET(oparg), false);
            STACK_SHRINK(1);
            break;
        }

        TARGET(STORE_FAST_UNBOXED_BOXED) {
            _Py_TYPENODE_t *value = TYPESTACK_PEEK(1);
            TYPE_OVERWRITE(value, TYPELOCALS_GET(oparg), false);
            STACK_SHRINK(1);
            break;
        }

        TARGET(STORE_FAST_UNBOXED_UNBOXED) {
            _Py_TYPENODE_t *value = TYPESTACK_PEEK(1);
            TYPE_OVERWRITE(value, TYPELOCALS_GET(oparg), false);
            STACK_SHRINK(1);
            break;
        }

        TARGET(POP_TOP) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(POP_TOP_NO_DECREF) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(PUSH_NULL) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(END_FOR) {
            {
                STACK_SHRINK(1);
            }
            {
                STACK_SHRINK(1);
            }
            break;
        }

        TARGET(UNARY_NEGATIVE) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(UNARY_NOT) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(UNARY_INVERT) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_MULTIPLY_INT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_MULTIPLY_INT_REST) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyLong_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_MULTIPLY_FLOAT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_SUBTRACT_INT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_SUBTRACT_INT_REST) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyLong_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_SUBTRACT_FLOAT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_ADD_UNICODE) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_INPLACE_ADD_UNICODE) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(BINARY_OP_ADD_FLOAT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CHECK_FLOAT) {
            TYPE_SET((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyFloat_Type), TYPESTACK_PEEK(1 + oparg), true);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyRawFloat_Type), TYPESTACK_PEEK(1 + oparg), true);
            break;
        }

        TARGET(BINARY_OP_ADD_FLOAT_UNBOXED) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyRawFloat_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_SUBTRACT_FLOAT_UNBOXED) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyRawFloat_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_OP_MULTIPLY_FLOAT_UNBOXED) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyRawFloat_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(UNBOX_FLOAT) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyRawFloat_Type), TYPESTACK_PEEK(1 + oparg), true);
            break;
        }

        TARGET(BOX_FLOAT) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyFloat_Type), TYPESTACK_PEEK(1 + oparg), true);
            break;
        }

        TARGET(BINARY_OP_ADD_INT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CHECK_INT) {
            TYPE_SET((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyLong_Type), TYPESTACK_PEEK(1 + oparg), true);
            break;
        }

        TARGET(BINARY_OP_ADD_INT_REST) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyLong_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_SUBSCR) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_SLICE) {
            STACK_SHRINK(2);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(STORE_SLICE) {
            STACK_SHRINK(4);
            break;
        }

        TARGET(BINARY_SUBSCR_LIST_INT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_SUBSCR_LIST_INT_REST) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CHECK_LIST) {
            TYPE_SET((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyList_Type), TYPESTACK_PEEK(1 + oparg), true);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyList_Type), TYPESTACK_PEEK(1 + oparg), true);
            break;
        }

        TARGET(BINARY_SUBSCR_TUPLE_INT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_SUBSCR_DICT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BINARY_SUBSCR_GETITEM) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(LIST_APPEND) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyList_Type), TYPESTACK_PEEK(1 + (oparg-1)), true);
            break;
        }

        TARGET(SET_ADD) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(STORE_SUBSCR) {
            STACK_SHRINK(3);
            break;
        }

        TARGET(STORE_SUBSCR_LIST_INT) {
            STACK_SHRINK(3);
            break;
        }

        TARGET(STORE_SUBSCR_LIST_INT_REST) {
            STACK_SHRINK(3);
            break;
        }

        TARGET(STORE_SUBSCR_DICT) {
            STACK_SHRINK(3);
            break;
        }

        TARGET(DELETE_SUBSCR) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(CALL_INTRINSIC_1) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_INTRINSIC_2) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(INTERPRETER_EXIT) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(RETURN_VALUE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(RETURN_CONST) {
            break;
        }

        TARGET(GET_AITER) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(GET_ANEXT) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(GET_AWAITABLE) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(END_ASYNC_FOR) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(CLEANUP_THROW) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(2), true);
            break;
        }

        TARGET(LOAD_ASSERTION_ERROR) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(LOAD_BUILD_CLASS) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(STORE_NAME) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(DELETE_NAME) {
            break;
        }

        TARGET(UNPACK_SEQUENCE) {
            STACK_SHRINK(1);
            STACK_GROW(oparg);
            for (int i = 0; i < (oparg); i++) {TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(oparg - i), true);}
            break;
        }

        TARGET(UNPACK_SEQUENCE_TWO_TUPLE) {
            STACK_SHRINK(1);
            STACK_GROW(oparg);
            for (int i = 0; i < (oparg); i++) {TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(oparg - i), true);}
            break;
        }

        TARGET(UNPACK_SEQUENCE_TUPLE) {
            STACK_SHRINK(1);
            STACK_GROW(oparg);
            for (int i = 0; i < (oparg); i++) {TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(oparg - i), true);}
            break;
        }

        TARGET(UNPACK_SEQUENCE_LIST) {
            STACK_SHRINK(1);
            STACK_GROW(oparg);
            for (int i = 0; i < (oparg); i++) {TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(oparg - i), true);}
            break;
        }

        TARGET(UNPACK_EX) {
            STACK_GROW((oparg >> 8) + (oparg & 0xFF));
            for (int i = 0; i < (oparg & 0xFF); i++) {TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK((oparg & 0xFF) - i), true);}
            break;
        }

        TARGET(STORE_ATTR) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(DELETE_ATTR) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(STORE_GLOBAL) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(DELETE_GLOBAL) {
            break;
        }

        TARGET(LOAD_NAME) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(LOAD_GLOBAL) {
            STACK_GROW(1);
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_GLOBAL_MODULE) {
            STACK_GROW(1);
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_GLOBAL_BUILTIN) {
            STACK_GROW(1);
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(DELETE_DEREF) {
            break;
        }

        TARGET(LOAD_CLASSDEREF) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(STORE_DEREF) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(COPY_FREE_VARS) {
            break;
        }

        TARGET(BUILD_STRING) {
            STACK_SHRINK(oparg);
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyUnicode_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BUILD_TUPLE) {
            STACK_SHRINK(oparg);
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyTuple_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BUILD_LIST) {
            STACK_SHRINK(oparg);
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyList_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(LIST_EXTEND) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(SET_UPDATE) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PySet_Type), TYPESTACK_PEEK(1 + (oparg-1)), true);
            break;
        }

        TARGET(BUILD_SET) {
            STACK_SHRINK(oparg);
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PySet_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BUILD_MAP) {
            STACK_SHRINK(oparg*2);
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyDict_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(SETUP_ANNOTATIONS) {
            break;
        }

        TARGET(BUILD_CONST_KEY_MAP) {
            STACK_SHRINK(oparg);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyDict_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(DICT_UPDATE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(DICT_MERGE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(MAP_ADD) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(LOAD_ATTR) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_INSTANCE_VALUE) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_MODULE) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_WITH_HINT) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_SLOT) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_CLASS) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_PROPERTY) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            break;
        }

        TARGET(LOAD_ATTR_GETATTRIBUTE_OVERRIDDEN) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            break;
        }

        TARGET(STORE_ATTR_INSTANCE_VALUE) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(STORE_ATTR_WITH_HINT) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(STORE_ATTR_SLOT) {
            STACK_SHRINK(2);
            break;
        }

        TARGET(COMPARE_OP) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(COMPARE_OP_FLOAT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(COMPARE_OP_INT) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(COMPARE_OP_STR) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(IS_OP) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyBool_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CONTAINS_OP) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyBool_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CHECK_EG_MATCH) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(2), true);
            break;
        }

        TARGET(CHECK_EXC_MATCH) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyBool_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(IMPORT_NAME) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(IMPORT_FROM) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(JUMP_FORWARD) {
            break;
        }

        TARGET(JUMP_BACKWARD) {
            break;
        }

        TARGET(JUMP_BACKWARD_QUICK) {
            break;
        }

        TARGET(POP_JUMP_IF_FALSE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(BB_TEST_POP_IF_FALSE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(POP_JUMP_IF_TRUE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(BB_TEST_POP_IF_TRUE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(POP_JUMP_IF_NOT_NONE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(BB_TEST_POP_IF_NOT_NONE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(POP_JUMP_IF_NONE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(BB_TEST_POP_IF_NONE) {
            STACK_SHRINK(1);
            break;
        }

        TARGET(JUMP_BACKWARD_NO_INTERRUPT) {
            break;
        }

        TARGET(GET_LEN) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_MAKE_ROOT((_Py_TYPENODE_t)&PyLong_Type), TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(MATCH_CLASS) {
            STACK_SHRINK(2);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(GET_ITER) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(GET_YIELD_FROM_ITER) {
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BB_TEST_ITER) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(FOR_ITER_LIST) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BB_TEST_ITER_LIST) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(FOR_ITER_TUPLE) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BB_TEST_ITER_TUPLE) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(FOR_ITER_RANGE) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(BB_TEST_ITER_RANGE) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(FOR_ITER_GEN) {
            STACK_GROW(1);
            break;
        }

        TARGET(BEFORE_ASYNC_WITH) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(2), true);
            break;
        }

        TARGET(BEFORE_WITH) {
            STACK_GROW(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(2), true);
            break;
        }

        TARGET(LOAD_ATTR_METHOD_WITH_VALUES) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_METHOD_NO_DICT) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(LOAD_ATTR_METHOD_LAZY_DICT) {
            STACK_GROW(((oparg & 1) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            if (oparg & 1) { TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1 + ((oparg & 1) ? 1 : 0)), true); }
            break;
        }

        TARGET(KW_NAMES) {
            break;
        }

        TARGET(CALL) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_BOUND_METHOD_EXACT_ARGS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            break;
        }

        TARGET(CALL_PY_EXACT_ARGS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            break;
        }

        TARGET(CALL_PY_WITH_DEFAULTS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            break;
        }

        TARGET(CALL_NO_KW_TYPE_1) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_STR_1) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_TUPLE_1) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_BUILTIN_CLASS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_BUILTIN_O) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_BUILTIN_FAST) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_BUILTIN_FAST_WITH_KEYWORDS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_LEN) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_ISINSTANCE) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_LIST_APPEND) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            break;
        }

        TARGET(CALL_NO_KW_METHOD_DESCRIPTOR_O) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_METHOD_DESCRIPTOR_FAST_WITH_KEYWORDS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_METHOD_DESCRIPTOR_NOARGS) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_NO_KW_METHOD_DESCRIPTOR_FAST) {
            STACK_SHRINK(oparg);
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CALL_FUNCTION_EX) {
            STACK_SHRINK(((oparg & 1) ? 1 : 0));
            STACK_SHRINK(2);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(MAKE_FUNCTION) {
            STACK_SHRINK(((oparg & 0x01) ? 1 : 0) + ((oparg & 0x02) ? 1 : 0) + ((oparg & 0x04) ? 1 : 0) + ((oparg & 0x08) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(RETURN_GENERATOR) {
            break;
        }

        TARGET(BUILD_SLICE) {
            STACK_SHRINK(((oparg == 3) ? 1 : 0));
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(FORMAT_VALUE) {
            STACK_SHRINK((((oparg & FVS_MASK) == FVS_HAVE_SPEC) ? 1 : 0));
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(COPY) {
            _Py_TYPENODE_t *bottom = TYPESTACK_PEEK(1 + (oparg-1));
            STACK_GROW(1);
            TYPE_OVERWRITE(bottom, TYPESTACK_PEEK(1), false);
            break;
        }

        TARGET(COPY_NO_INCREF) {
            _Py_TYPENODE_t *bottom = TYPESTACK_PEEK(1 + (oparg - 1));
            STACK_GROW(1);
            TYPE_OVERWRITE(bottom, TYPESTACK_PEEK(1), false);
            break;
        }

        TARGET(BINARY_OP) {
            STACK_SHRINK(1);
            TYPE_OVERWRITE((_Py_TYPENODE_t *)_Py_TYPENODE_NULLROOT, TYPESTACK_PEEK(1), true);
            break;
        }

        TARGET(CACHE) {
            break;
        }

        TARGET(BB_BRANCH) {
            break;
        }

        TARGET(BB_BRANCH_IF_FLAG_UNSET) {
            break;
        }

        TARGET(BB_JUMP_IF_FLAG_UNSET) {
            break;
        }

        TARGET(BB_BRANCH_IF_FLAG_SET) {
            break;
        }

        TARGET(BB_JUMP_IF_FLAG_SET) {
            break;
        }

        TARGET(BB_JUMP_BACKWARD_LAZY) {
            break;
        }
