/* Auto-generated by Tools/scripts/generate_opcode_h.py from Lib/opcode.py */
#ifndef Py_OPCODE_H
#define Py_OPCODE_H
#ifdef __cplusplus
extern "C" {
#endif


/* Instruction opcodes for compiled code */
#define POP_TOP                           1
#define PUSH_NULL                         2
#define CACHE                             3
#define NOP                               9
#define UNARY_POSITIVE                   10
#define UNARY_NEGATIVE                   11
#define UNARY_NOT                        12
#define UNARY_INVERT                     15
#define BINARY_SUBSCR                    25
#define GET_LEN                          30
#define MATCH_MAPPING                    31
#define MATCH_SEQUENCE                   32
#define MATCH_KEYS                       33
#define PUSH_EXC_INFO                    35
#define WITH_EXCEPT_START                49
#define GET_AITER                        50
#define GET_ANEXT                        51
#define BEFORE_ASYNC_WITH                52
#define BEFORE_WITH                      53
#define END_ASYNC_FOR                    54
#define STORE_SUBSCR                     60
#define DELETE_SUBSCR                    61
#define GET_ITER                         68
#define GET_YIELD_FROM_ITER              69
#define PRINT_EXPR                       70
#define LOAD_BUILD_CLASS                 71
#define GET_AWAITABLE                    73
#define LOAD_ASSERTION_ERROR             74
#define RETURN_GENERATOR                 75
#define LIST_TO_TUPLE                    82
#define RETURN_VALUE                     83
#define IMPORT_STAR                      84
#define SETUP_ANNOTATIONS                85
#define YIELD_VALUE                      86
#define ASYNC_GEN_WRAP                   87
#define PREP_RERAISE_STAR                88
#define POP_EXCEPT                       89
#define HAVE_ARGUMENT                    90
#define STORE_NAME                       90
#define DELETE_NAME                      91
#define UNPACK_SEQUENCE                  92
#define FOR_ITER                         93
#define UNPACK_EX                        94
#define STORE_ATTR                       95
#define DELETE_ATTR                      96
#define STORE_GLOBAL                     97
#define DELETE_GLOBAL                    98
#define SWAP                             99
#define LOAD_CONST                      100
#define LOAD_NAME                       101
#define BUILD_TUPLE                     102
#define BUILD_LIST                      103
#define BUILD_SET                       104
#define BUILD_MAP                       105
#define LOAD_ATTR                       106
#define COMPARE_OP                      107
#define IMPORT_NAME                     108
#define IMPORT_FROM                     109
#define JUMP_FORWARD                    110
#define JUMP_IF_FALSE_OR_POP            111
#define JUMP_IF_TRUE_OR_POP             112
#define JUMP_ABSOLUTE                   113
#define POP_JUMP_IF_FALSE               114
#define POP_JUMP_IF_TRUE                115
#define LOAD_GLOBAL                     116
#define IS_OP                           117
#define CONTAINS_OP                     118
#define RERAISE                         119
#define COPY                            120
#define JUMP_IF_NOT_EXC_MATCH           121
#define BINARY_OP                       122
#define SEND                            123
#define LOAD_FAST                       124
#define STORE_FAST                      125
#define DELETE_FAST                     126
#define JUMP_IF_NOT_EG_MATCH            127
#define POP_JUMP_IF_NOT_NONE            128
#define POP_JUMP_IF_NONE                129
#define RAISE_VARARGS                   130
#define MAKE_FUNCTION                   132
#define BUILD_SLICE                     133
#define JUMP_NO_INTERRUPT               134
#define MAKE_CELL                       135
#define LOAD_CLOSURE                    136
#define LOAD_DEREF                      137
#define STORE_DEREF                     138
#define DELETE_DEREF                    139
#define CALL_FUNCTION_EX                142
#define EXTENDED_ARG                    144
#define LIST_APPEND                     145
#define SET_ADD                         146
#define MAP_ADD                         147
#define LOAD_CLASSDEREF                 148
#define COPY_FREE_VARS                  149
#define RESUME                          151
#define MATCH_CLASS                     152
#define FORMAT_VALUE                    155
#define BUILD_CONST_KEY_MAP             156
#define BUILD_STRING                    157
#define LOAD_METHOD                     160
#define LIST_EXTEND                     162
#define SET_UPDATE                      163
#define DICT_MERGE                      164
#define DICT_UPDATE                     165
#define PRECALL                         166
#define CALL                            171
#define KW_NAMES                        172
#define BINARY_OP_ADAPTIVE                4
#define BINARY_OP_ADD_INT                 5
#define BINARY_OP_ADD_FLOAT               6
#define BINARY_OP_ADD_UNICODE             7
#define BINARY_OP_INPLACE_ADD_UNICODE     8
#define BINARY_OP_MULTIPLY_INT           13
#define BINARY_OP_MULTIPLY_FLOAT         14
#define BINARY_OP_SUBTRACT_INT           16
#define BINARY_OP_SUBTRACT_FLOAT         17
#define COMPARE_OP_ADAPTIVE              18
#define COMPARE_OP_FLOAT_JUMP            19
#define COMPARE_OP_INT_JUMP              20
#define COMPARE_OP_STR_JUMP              21
#define BINARY_SUBSCR_ADAPTIVE           22
#define BINARY_SUBSCR_GETITEM            23
#define BINARY_SUBSCR_LIST_INT           24
#define BINARY_SUBSCR_TUPLE_INT          26
#define BINARY_SUBSCR_DICT               27
#define STORE_SUBSCR_ADAPTIVE            28
#define STORE_SUBSCR_LIST_INT            29
#define STORE_SUBSCR_DICT                34
#define CALL_ADAPTIVE                    36
#define CALL_PY_EXACT_ARGS               37
#define CALL_PY_WITH_DEFAULTS            38
#define JUMP_ABSOLUTE_QUICK              39
#define LOAD_ATTR_ADAPTIVE               40
#define LOAD_ATTR_INSTANCE_VALUE         41
#define LOAD_ATTR_WITH_HINT              42
#define LOAD_ATTR_SLOT                   43
#define LOAD_ATTR_MODULE                 44
#define LOAD_GLOBAL_ADAPTIVE             45
#define LOAD_GLOBAL_MODULE               46
#define LOAD_GLOBAL_BUILTIN              47
#define LOAD_METHOD_ADAPTIVE             48
#define LOAD_METHOD_CLASS                55
#define LOAD_METHOD_MODULE               56
#define LOAD_METHOD_NO_DICT              57
#define LOAD_METHOD_WITH_DICT            58
#define LOAD_METHOD_WITH_VALUES          59
#define PRECALL_ADAPTIVE                 62
#define PRECALL_BUILTIN_CLASS            63
#define PRECALL_NO_KW_BUILTIN_O          64
#define PRECALL_NO_KW_BUILTIN_FAST       65
#define PRECALL_BUILTIN_FAST_WITH_KEYWORDS  66
#define PRECALL_NO_KW_LEN                67
#define PRECALL_NO_KW_ISINSTANCE         72
#define PRECALL_NO_KW_LIST_APPEND        76
#define PRECALL_NO_KW_METHOD_DESCRIPTOR_O  77
#define PRECALL_NO_KW_METHOD_DESCRIPTOR_NOARGS  78
#define PRECALL_NO_KW_STR_1              79
#define PRECALL_NO_KW_TUPLE_1            80
#define PRECALL_NO_KW_TYPE_1             81
#define PRECALL_NO_KW_METHOD_DESCRIPTOR_FAST 131
#define PRECALL_BOUND_METHOD            140
#define PRECALL_PYFUNC                  141
#define RESUME_QUICK                    143
#define STORE_ATTR_ADAPTIVE             150
#define STORE_ATTR_INSTANCE_VALUE       153
#define STORE_ATTR_SLOT                 154
#define STORE_ATTR_WITH_HINT            158
#define UNPACK_SEQUENCE_ADAPTIVE        159
#define UNPACK_SEQUENCE_LIST            161
#define UNPACK_SEQUENCE_TUPLE           167
#define UNPACK_SEQUENCE_TWO_TUPLE       168
#define LOAD_FAST__LOAD_FAST            169
#define STORE_FAST__LOAD_FAST           170
#define LOAD_FAST__LOAD_CONST           173
#define LOAD_CONST__LOAD_FAST           174
#define STORE_FAST__STORE_FAST          175
#define LOAD_FAST__LOAD_ATTR_INSTANCE_VALUE 176
#define DO_TRACING                      255

extern const uint8_t _PyOpcode_InlineCacheEntries[256];

#ifdef NEED_OPCODE_TABLES
static const uint32_t _PyOpcode_RelativeJump[8] = {
    0U,
    0U,
    536870912U,
    134234112U,
    0U,
    0U,
    0U,
    0U,
};
static const uint32_t _PyOpcode_Jump[8] = {
    0U,
    0U,
    536870912U,
    2316288000U,
    67U,
    0U,
    0U,
    0U,
};

const uint8_t _PyOpcode_InlineCacheEntries[256] = {
    [UNPACK_SEQUENCE] = 1,
    [COMPARE_OP] = 2,
    [LOAD_GLOBAL] = 5,
    [BINARY_OP] = 1,
};
#endif /* OPCODE_TABLES */

#define HAS_CONST(op) (false\
    || ((op) == 100) \
    || ((op) == 172) \
    )

#define NB_ADD                            0
#define NB_AND                            1
#define NB_FLOOR_DIVIDE                   2
#define NB_LSHIFT                         3
#define NB_MATRIX_MULTIPLY                4
#define NB_MULTIPLY                       5
#define NB_REMAINDER                      6
#define NB_OR                             7
#define NB_POWER                          8
#define NB_RSHIFT                         9
#define NB_SUBTRACT                      10
#define NB_TRUE_DIVIDE                   11
#define NB_XOR                           12
#define NB_INPLACE_ADD                   13
#define NB_INPLACE_AND                   14
#define NB_INPLACE_FLOOR_DIVIDE          15
#define NB_INPLACE_LSHIFT                16
#define NB_INPLACE_MATRIX_MULTIPLY       17
#define NB_INPLACE_MULTIPLY              18
#define NB_INPLACE_REMAINDER             19
#define NB_INPLACE_OR                    20
#define NB_INPLACE_POWER                 21
#define NB_INPLACE_RSHIFT                22
#define NB_INPLACE_SUBTRACT              23
#define NB_INPLACE_TRUE_DIVIDE           24
#define NB_INPLACE_XOR                   25

#define HAS_ARG(op) ((op) >= HAVE_ARGUMENT)

/* Reserve some bytecodes for internal use in the compiler.
 * The value of 240 is arbitrary. */
#define IS_ARTIFICIAL(op) ((op) > 240)

#ifdef __cplusplus
}
#endif
#endif /* !Py_OPCODE_H */
