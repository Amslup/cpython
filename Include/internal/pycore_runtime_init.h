#ifndef Py_INTERNAL_RUNTIME_INIT_H
#define Py_INTERNAL_RUNTIME_INIT_H
#ifdef __cplusplus
extern "C" {
#endif

#ifndef Py_BUILD_CORE
#  error "this header requires Py_BUILD_CORE define"
#endif

#include "pycore_object.h"


/* The static initializers defined here should only be used
   in the runtime init code (in pystate.c and pylifecycle.c). */


#define _PyRuntimeState_INIT \
    { \
        .gilstate = { \
            .check_enabled = 1, \
            /* A TSS key must be initialized with Py_tss_NEEDS_INIT \
               in accordance with the specification. */ \
            .autoTSSkey = Py_tss_NEEDS_INIT, \
        }, \
        .interpreters = { \
            /* This prevents interpreters from getting created \
              until _PyInterpreterState_Enable() is called. */ \
            .next_id = -1, \
        }, \
        .global_objects = _Py_global_objects_INIT, \
        ._main_interpreter = _PyInterpreterState_INIT, \
    }

#ifdef HAVE_DLOPEN
#  include <dlfcn.h>
#  if HAVE_DECL_RTLD_NOW
#    define _Py_DLOPEN_FLAGS RTLD_NOW
#  else
#    define _Py_DLOPEN_FLAGS RTLD_LAZY
#  endif
#  define DLOPENFLAGS_INIT .dlopenflags = _Py_DLOPEN_FLAGS,
#else
#  define _Py_DLOPEN_FLAGS 0
#  define DLOPENFLAGS_INIT
#endif

#define _PyInterpreterState_INIT \
    { \
        ._static = 1, \
        .id_refcount = -1, \
        DLOPENFLAGS_INIT \
        .ceval = { \
            .recursion_limit = Py_DEFAULT_RECURSION_LIMIT, \
        }, \
        .gc = { \
            .enabled = 1, \
            .generations = { \
                /* .head is set in _PyGC_InitState(). */ \
                { .threshold = 700, }, \
                { .threshold = 10, }, \
                { .threshold = 10, }, \
            }, \
        }, \
        ._initial_thread = _PyThreadState_INIT, \
    }

#define _PyThreadState_INIT \
    { \
        ._static = 1, \
        .recursion_limit = Py_DEFAULT_RECURSION_LIMIT, \
        .context_ver = 1, \
    }


// global objects

#define _PyLong_DIGIT_INIT(val) \
    { \
        _PyVarObject_IMMORTAL_INIT(&PyLong_Type, \
                                   ((val) == 0 ? 0 : ((val) > 0 ? 1 : -1))), \
        .ob_digit = { ((val) >= 0 ? (val) : -(val)) }, \
    }

#define _PyBytes_SIMPLE_INIT(CH, LEN) \
    { \
        _PyVarObject_IMMORTAL_INIT(&PyBytes_Type, LEN), \
        .ob_shash = -1, \
        .ob_sval = { CH }, \
    }
#define _PyBytes_CHAR_INIT(CH) \
    { \
        _PyBytes_SIMPLE_INIT(CH, 1) \
    }

#define _PyASCIIObject_INIT(LITERAL) \
    { \
        ._ascii = { \
            .ob_base = { \
                .ob_refcnt = 999999999, \
                .ob_type = &PyUnicode_Type, \
            }, \
            .length = _Py_STRING_LENGTH(LITERAL) - 1, \
            .hash = -1, \
            .state = { \
                .kind = 1, \
                .compact = 1, \
                .ascii = 1, \
                .ready = 1, \
            }, \
        }, \
        ._data = LITERAL, \
    }
#define INIT_STR(NAME, LITERAL) \
    .$ ## NAME = _PyASCIIObject_INIT(LITERAL)
#define INIT_ID(NAME) \
    INIT_STR(NAME, #NAME)


/* The following is auto-generated by Tools/scripts/generate_global_objects.py. */
#define _Py_global_objects_INIT { \
    .singletons = { \
        .small_ints = { \
            _PyLong_DIGIT_INIT(-5), \
            _PyLong_DIGIT_INIT(-4), \
            _PyLong_DIGIT_INIT(-3), \
            _PyLong_DIGIT_INIT(-2), \
            _PyLong_DIGIT_INIT(-1), \
            _PyLong_DIGIT_INIT(0), \
            _PyLong_DIGIT_INIT(1), \
            _PyLong_DIGIT_INIT(2), \
            _PyLong_DIGIT_INIT(3), \
            _PyLong_DIGIT_INIT(4), \
            _PyLong_DIGIT_INIT(5), \
            _PyLong_DIGIT_INIT(6), \
            _PyLong_DIGIT_INIT(7), \
            _PyLong_DIGIT_INIT(8), \
            _PyLong_DIGIT_INIT(9), \
            _PyLong_DIGIT_INIT(10), \
            _PyLong_DIGIT_INIT(11), \
            _PyLong_DIGIT_INIT(12), \
            _PyLong_DIGIT_INIT(13), \
            _PyLong_DIGIT_INIT(14), \
            _PyLong_DIGIT_INIT(15), \
            _PyLong_DIGIT_INIT(16), \
            _PyLong_DIGIT_INIT(17), \
            _PyLong_DIGIT_INIT(18), \
            _PyLong_DIGIT_INIT(19), \
            _PyLong_DIGIT_INIT(20), \
            _PyLong_DIGIT_INIT(21), \
            _PyLong_DIGIT_INIT(22), \
            _PyLong_DIGIT_INIT(23), \
            _PyLong_DIGIT_INIT(24), \
            _PyLong_DIGIT_INIT(25), \
            _PyLong_DIGIT_INIT(26), \
            _PyLong_DIGIT_INIT(27), \
            _PyLong_DIGIT_INIT(28), \
            _PyLong_DIGIT_INIT(29), \
            _PyLong_DIGIT_INIT(30), \
            _PyLong_DIGIT_INIT(31), \
            _PyLong_DIGIT_INIT(32), \
            _PyLong_DIGIT_INIT(33), \
            _PyLong_DIGIT_INIT(34), \
            _PyLong_DIGIT_INIT(35), \
            _PyLong_DIGIT_INIT(36), \
            _PyLong_DIGIT_INIT(37), \
            _PyLong_DIGIT_INIT(38), \
            _PyLong_DIGIT_INIT(39), \
            _PyLong_DIGIT_INIT(40), \
            _PyLong_DIGIT_INIT(41), \
            _PyLong_DIGIT_INIT(42), \
            _PyLong_DIGIT_INIT(43), \
            _PyLong_DIGIT_INIT(44), \
            _PyLong_DIGIT_INIT(45), \
            _PyLong_DIGIT_INIT(46), \
            _PyLong_DIGIT_INIT(47), \
            _PyLong_DIGIT_INIT(48), \
            _PyLong_DIGIT_INIT(49), \
            _PyLong_DIGIT_INIT(50), \
            _PyLong_DIGIT_INIT(51), \
            _PyLong_DIGIT_INIT(52), \
            _PyLong_DIGIT_INIT(53), \
            _PyLong_DIGIT_INIT(54), \
            _PyLong_DIGIT_INIT(55), \
            _PyLong_DIGIT_INIT(56), \
            _PyLong_DIGIT_INIT(57), \
            _PyLong_DIGIT_INIT(58), \
            _PyLong_DIGIT_INIT(59), \
            _PyLong_DIGIT_INIT(60), \
            _PyLong_DIGIT_INIT(61), \
            _PyLong_DIGIT_INIT(62), \
            _PyLong_DIGIT_INIT(63), \
            _PyLong_DIGIT_INIT(64), \
            _PyLong_DIGIT_INIT(65), \
            _PyLong_DIGIT_INIT(66), \
            _PyLong_DIGIT_INIT(67), \
            _PyLong_DIGIT_INIT(68), \
            _PyLong_DIGIT_INIT(69), \
            _PyLong_DIGIT_INIT(70), \
            _PyLong_DIGIT_INIT(71), \
            _PyLong_DIGIT_INIT(72), \
            _PyLong_DIGIT_INIT(73), \
            _PyLong_DIGIT_INIT(74), \
            _PyLong_DIGIT_INIT(75), \
            _PyLong_DIGIT_INIT(76), \
            _PyLong_DIGIT_INIT(77), \
            _PyLong_DIGIT_INIT(78), \
            _PyLong_DIGIT_INIT(79), \
            _PyLong_DIGIT_INIT(80), \
            _PyLong_DIGIT_INIT(81), \
            _PyLong_DIGIT_INIT(82), \
            _PyLong_DIGIT_INIT(83), \
            _PyLong_DIGIT_INIT(84), \
            _PyLong_DIGIT_INIT(85), \
            _PyLong_DIGIT_INIT(86), \
            _PyLong_DIGIT_INIT(87), \
            _PyLong_DIGIT_INIT(88), \
            _PyLong_DIGIT_INIT(89), \
            _PyLong_DIGIT_INIT(90), \
            _PyLong_DIGIT_INIT(91), \
            _PyLong_DIGIT_INIT(92), \
            _PyLong_DIGIT_INIT(93), \
            _PyLong_DIGIT_INIT(94), \
            _PyLong_DIGIT_INIT(95), \
            _PyLong_DIGIT_INIT(96), \
            _PyLong_DIGIT_INIT(97), \
            _PyLong_DIGIT_INIT(98), \
            _PyLong_DIGIT_INIT(99), \
            _PyLong_DIGIT_INIT(100), \
            _PyLong_DIGIT_INIT(101), \
            _PyLong_DIGIT_INIT(102), \
            _PyLong_DIGIT_INIT(103), \
            _PyLong_DIGIT_INIT(104), \
            _PyLong_DIGIT_INIT(105), \
            _PyLong_DIGIT_INIT(106), \
            _PyLong_DIGIT_INIT(107), \
            _PyLong_DIGIT_INIT(108), \
            _PyLong_DIGIT_INIT(109), \
            _PyLong_DIGIT_INIT(110), \
            _PyLong_DIGIT_INIT(111), \
            _PyLong_DIGIT_INIT(112), \
            _PyLong_DIGIT_INIT(113), \
            _PyLong_DIGIT_INIT(114), \
            _PyLong_DIGIT_INIT(115), \
            _PyLong_DIGIT_INIT(116), \
            _PyLong_DIGIT_INIT(117), \
            _PyLong_DIGIT_INIT(118), \
            _PyLong_DIGIT_INIT(119), \
            _PyLong_DIGIT_INIT(120), \
            _PyLong_DIGIT_INIT(121), \
            _PyLong_DIGIT_INIT(122), \
            _PyLong_DIGIT_INIT(123), \
            _PyLong_DIGIT_INIT(124), \
            _PyLong_DIGIT_INIT(125), \
            _PyLong_DIGIT_INIT(126), \
            _PyLong_DIGIT_INIT(127), \
            _PyLong_DIGIT_INIT(128), \
            _PyLong_DIGIT_INIT(129), \
            _PyLong_DIGIT_INIT(130), \
            _PyLong_DIGIT_INIT(131), \
            _PyLong_DIGIT_INIT(132), \
            _PyLong_DIGIT_INIT(133), \
            _PyLong_DIGIT_INIT(134), \
            _PyLong_DIGIT_INIT(135), \
            _PyLong_DIGIT_INIT(136), \
            _PyLong_DIGIT_INIT(137), \
            _PyLong_DIGIT_INIT(138), \
            _PyLong_DIGIT_INIT(139), \
            _PyLong_DIGIT_INIT(140), \
            _PyLong_DIGIT_INIT(141), \
            _PyLong_DIGIT_INIT(142), \
            _PyLong_DIGIT_INIT(143), \
            _PyLong_DIGIT_INIT(144), \
            _PyLong_DIGIT_INIT(145), \
            _PyLong_DIGIT_INIT(146), \
            _PyLong_DIGIT_INIT(147), \
            _PyLong_DIGIT_INIT(148), \
            _PyLong_DIGIT_INIT(149), \
            _PyLong_DIGIT_INIT(150), \
            _PyLong_DIGIT_INIT(151), \
            _PyLong_DIGIT_INIT(152), \
            _PyLong_DIGIT_INIT(153), \
            _PyLong_DIGIT_INIT(154), \
            _PyLong_DIGIT_INIT(155), \
            _PyLong_DIGIT_INIT(156), \
            _PyLong_DIGIT_INIT(157), \
            _PyLong_DIGIT_INIT(158), \
            _PyLong_DIGIT_INIT(159), \
            _PyLong_DIGIT_INIT(160), \
            _PyLong_DIGIT_INIT(161), \
            _PyLong_DIGIT_INIT(162), \
            _PyLong_DIGIT_INIT(163), \
            _PyLong_DIGIT_INIT(164), \
            _PyLong_DIGIT_INIT(165), \
            _PyLong_DIGIT_INIT(166), \
            _PyLong_DIGIT_INIT(167), \
            _PyLong_DIGIT_INIT(168), \
            _PyLong_DIGIT_INIT(169), \
            _PyLong_DIGIT_INIT(170), \
            _PyLong_DIGIT_INIT(171), \
            _PyLong_DIGIT_INIT(172), \
            _PyLong_DIGIT_INIT(173), \
            _PyLong_DIGIT_INIT(174), \
            _PyLong_DIGIT_INIT(175), \
            _PyLong_DIGIT_INIT(176), \
            _PyLong_DIGIT_INIT(177), \
            _PyLong_DIGIT_INIT(178), \
            _PyLong_DIGIT_INIT(179), \
            _PyLong_DIGIT_INIT(180), \
            _PyLong_DIGIT_INIT(181), \
            _PyLong_DIGIT_INIT(182), \
            _PyLong_DIGIT_INIT(183), \
            _PyLong_DIGIT_INIT(184), \
            _PyLong_DIGIT_INIT(185), \
            _PyLong_DIGIT_INIT(186), \
            _PyLong_DIGIT_INIT(187), \
            _PyLong_DIGIT_INIT(188), \
            _PyLong_DIGIT_INIT(189), \
            _PyLong_DIGIT_INIT(190), \
            _PyLong_DIGIT_INIT(191), \
            _PyLong_DIGIT_INIT(192), \
            _PyLong_DIGIT_INIT(193), \
            _PyLong_DIGIT_INIT(194), \
            _PyLong_DIGIT_INIT(195), \
            _PyLong_DIGIT_INIT(196), \
            _PyLong_DIGIT_INIT(197), \
            _PyLong_DIGIT_INIT(198), \
            _PyLong_DIGIT_INIT(199), \
            _PyLong_DIGIT_INIT(200), \
            _PyLong_DIGIT_INIT(201), \
            _PyLong_DIGIT_INIT(202), \
            _PyLong_DIGIT_INIT(203), \
            _PyLong_DIGIT_INIT(204), \
            _PyLong_DIGIT_INIT(205), \
            _PyLong_DIGIT_INIT(206), \
            _PyLong_DIGIT_INIT(207), \
            _PyLong_DIGIT_INIT(208), \
            _PyLong_DIGIT_INIT(209), \
            _PyLong_DIGIT_INIT(210), \
            _PyLong_DIGIT_INIT(211), \
            _PyLong_DIGIT_INIT(212), \
            _PyLong_DIGIT_INIT(213), \
            _PyLong_DIGIT_INIT(214), \
            _PyLong_DIGIT_INIT(215), \
            _PyLong_DIGIT_INIT(216), \
            _PyLong_DIGIT_INIT(217), \
            _PyLong_DIGIT_INIT(218), \
            _PyLong_DIGIT_INIT(219), \
            _PyLong_DIGIT_INIT(220), \
            _PyLong_DIGIT_INIT(221), \
            _PyLong_DIGIT_INIT(222), \
            _PyLong_DIGIT_INIT(223), \
            _PyLong_DIGIT_INIT(224), \
            _PyLong_DIGIT_INIT(225), \
            _PyLong_DIGIT_INIT(226), \
            _PyLong_DIGIT_INIT(227), \
            _PyLong_DIGIT_INIT(228), \
            _PyLong_DIGIT_INIT(229), \
            _PyLong_DIGIT_INIT(230), \
            _PyLong_DIGIT_INIT(231), \
            _PyLong_DIGIT_INIT(232), \
            _PyLong_DIGIT_INIT(233), \
            _PyLong_DIGIT_INIT(234), \
            _PyLong_DIGIT_INIT(235), \
            _PyLong_DIGIT_INIT(236), \
            _PyLong_DIGIT_INIT(237), \
            _PyLong_DIGIT_INIT(238), \
            _PyLong_DIGIT_INIT(239), \
            _PyLong_DIGIT_INIT(240), \
            _PyLong_DIGIT_INIT(241), \
            _PyLong_DIGIT_INIT(242), \
            _PyLong_DIGIT_INIT(243), \
            _PyLong_DIGIT_INIT(244), \
            _PyLong_DIGIT_INIT(245), \
            _PyLong_DIGIT_INIT(246), \
            _PyLong_DIGIT_INIT(247), \
            _PyLong_DIGIT_INIT(248), \
            _PyLong_DIGIT_INIT(249), \
            _PyLong_DIGIT_INIT(250), \
            _PyLong_DIGIT_INIT(251), \
            _PyLong_DIGIT_INIT(252), \
            _PyLong_DIGIT_INIT(253), \
            _PyLong_DIGIT_INIT(254), \
            _PyLong_DIGIT_INIT(255), \
            _PyLong_DIGIT_INIT(256), \
        }, \
        \
        .bytes_empty = _PyBytes_SIMPLE_INIT(0, 0), \
        .bytes_characters = { \
            _PyBytes_CHAR_INIT(0), \
            _PyBytes_CHAR_INIT(1), \
            _PyBytes_CHAR_INIT(2), \
            _PyBytes_CHAR_INIT(3), \
            _PyBytes_CHAR_INIT(4), \
            _PyBytes_CHAR_INIT(5), \
            _PyBytes_CHAR_INIT(6), \
            _PyBytes_CHAR_INIT(7), \
            _PyBytes_CHAR_INIT(8), \
            _PyBytes_CHAR_INIT(9), \
            _PyBytes_CHAR_INIT(10), \
            _PyBytes_CHAR_INIT(11), \
            _PyBytes_CHAR_INIT(12), \
            _PyBytes_CHAR_INIT(13), \
            _PyBytes_CHAR_INIT(14), \
            _PyBytes_CHAR_INIT(15), \
            _PyBytes_CHAR_INIT(16), \
            _PyBytes_CHAR_INIT(17), \
            _PyBytes_CHAR_INIT(18), \
            _PyBytes_CHAR_INIT(19), \
            _PyBytes_CHAR_INIT(20), \
            _PyBytes_CHAR_INIT(21), \
            _PyBytes_CHAR_INIT(22), \
            _PyBytes_CHAR_INIT(23), \
            _PyBytes_CHAR_INIT(24), \
            _PyBytes_CHAR_INIT(25), \
            _PyBytes_CHAR_INIT(26), \
            _PyBytes_CHAR_INIT(27), \
            _PyBytes_CHAR_INIT(28), \
            _PyBytes_CHAR_INIT(29), \
            _PyBytes_CHAR_INIT(30), \
            _PyBytes_CHAR_INIT(31), \
            _PyBytes_CHAR_INIT(32), \
            _PyBytes_CHAR_INIT(33), \
            _PyBytes_CHAR_INIT(34), \
            _PyBytes_CHAR_INIT(35), \
            _PyBytes_CHAR_INIT(36), \
            _PyBytes_CHAR_INIT(37), \
            _PyBytes_CHAR_INIT(38), \
            _PyBytes_CHAR_INIT(39), \
            _PyBytes_CHAR_INIT(40), \
            _PyBytes_CHAR_INIT(41), \
            _PyBytes_CHAR_INIT(42), \
            _PyBytes_CHAR_INIT(43), \
            _PyBytes_CHAR_INIT(44), \
            _PyBytes_CHAR_INIT(45), \
            _PyBytes_CHAR_INIT(46), \
            _PyBytes_CHAR_INIT(47), \
            _PyBytes_CHAR_INIT(48), \
            _PyBytes_CHAR_INIT(49), \
            _PyBytes_CHAR_INIT(50), \
            _PyBytes_CHAR_INIT(51), \
            _PyBytes_CHAR_INIT(52), \
            _PyBytes_CHAR_INIT(53), \
            _PyBytes_CHAR_INIT(54), \
            _PyBytes_CHAR_INIT(55), \
            _PyBytes_CHAR_INIT(56), \
            _PyBytes_CHAR_INIT(57), \
            _PyBytes_CHAR_INIT(58), \
            _PyBytes_CHAR_INIT(59), \
            _PyBytes_CHAR_INIT(60), \
            _PyBytes_CHAR_INIT(61), \
            _PyBytes_CHAR_INIT(62), \
            _PyBytes_CHAR_INIT(63), \
            _PyBytes_CHAR_INIT(64), \
            _PyBytes_CHAR_INIT(65), \
            _PyBytes_CHAR_INIT(66), \
            _PyBytes_CHAR_INIT(67), \
            _PyBytes_CHAR_INIT(68), \
            _PyBytes_CHAR_INIT(69), \
            _PyBytes_CHAR_INIT(70), \
            _PyBytes_CHAR_INIT(71), \
            _PyBytes_CHAR_INIT(72), \
            _PyBytes_CHAR_INIT(73), \
            _PyBytes_CHAR_INIT(74), \
            _PyBytes_CHAR_INIT(75), \
            _PyBytes_CHAR_INIT(76), \
            _PyBytes_CHAR_INIT(77), \
            _PyBytes_CHAR_INIT(78), \
            _PyBytes_CHAR_INIT(79), \
            _PyBytes_CHAR_INIT(80), \
            _PyBytes_CHAR_INIT(81), \
            _PyBytes_CHAR_INIT(82), \
            _PyBytes_CHAR_INIT(83), \
            _PyBytes_CHAR_INIT(84), \
            _PyBytes_CHAR_INIT(85), \
            _PyBytes_CHAR_INIT(86), \
            _PyBytes_CHAR_INIT(87), \
            _PyBytes_CHAR_INIT(88), \
            _PyBytes_CHAR_INIT(89), \
            _PyBytes_CHAR_INIT(90), \
            _PyBytes_CHAR_INIT(91), \
            _PyBytes_CHAR_INIT(92), \
            _PyBytes_CHAR_INIT(93), \
            _PyBytes_CHAR_INIT(94), \
            _PyBytes_CHAR_INIT(95), \
            _PyBytes_CHAR_INIT(96), \
            _PyBytes_CHAR_INIT(97), \
            _PyBytes_CHAR_INIT(98), \
            _PyBytes_CHAR_INIT(99), \
            _PyBytes_CHAR_INIT(100), \
            _PyBytes_CHAR_INIT(101), \
            _PyBytes_CHAR_INIT(102), \
            _PyBytes_CHAR_INIT(103), \
            _PyBytes_CHAR_INIT(104), \
            _PyBytes_CHAR_INIT(105), \
            _PyBytes_CHAR_INIT(106), \
            _PyBytes_CHAR_INIT(107), \
            _PyBytes_CHAR_INIT(108), \
            _PyBytes_CHAR_INIT(109), \
            _PyBytes_CHAR_INIT(110), \
            _PyBytes_CHAR_INIT(111), \
            _PyBytes_CHAR_INIT(112), \
            _PyBytes_CHAR_INIT(113), \
            _PyBytes_CHAR_INIT(114), \
            _PyBytes_CHAR_INIT(115), \
            _PyBytes_CHAR_INIT(116), \
            _PyBytes_CHAR_INIT(117), \
            _PyBytes_CHAR_INIT(118), \
            _PyBytes_CHAR_INIT(119), \
            _PyBytes_CHAR_INIT(120), \
            _PyBytes_CHAR_INIT(121), \
            _PyBytes_CHAR_INIT(122), \
            _PyBytes_CHAR_INIT(123), \
            _PyBytes_CHAR_INIT(124), \
            _PyBytes_CHAR_INIT(125), \
            _PyBytes_CHAR_INIT(126), \
            _PyBytes_CHAR_INIT(127), \
            _PyBytes_CHAR_INIT(128), \
            _PyBytes_CHAR_INIT(129), \
            _PyBytes_CHAR_INIT(130), \
            _PyBytes_CHAR_INIT(131), \
            _PyBytes_CHAR_INIT(132), \
            _PyBytes_CHAR_INIT(133), \
            _PyBytes_CHAR_INIT(134), \
            _PyBytes_CHAR_INIT(135), \
            _PyBytes_CHAR_INIT(136), \
            _PyBytes_CHAR_INIT(137), \
            _PyBytes_CHAR_INIT(138), \
            _PyBytes_CHAR_INIT(139), \
            _PyBytes_CHAR_INIT(140), \
            _PyBytes_CHAR_INIT(141), \
            _PyBytes_CHAR_INIT(142), \
            _PyBytes_CHAR_INIT(143), \
            _PyBytes_CHAR_INIT(144), \
            _PyBytes_CHAR_INIT(145), \
            _PyBytes_CHAR_INIT(146), \
            _PyBytes_CHAR_INIT(147), \
            _PyBytes_CHAR_INIT(148), \
            _PyBytes_CHAR_INIT(149), \
            _PyBytes_CHAR_INIT(150), \
            _PyBytes_CHAR_INIT(151), \
            _PyBytes_CHAR_INIT(152), \
            _PyBytes_CHAR_INIT(153), \
            _PyBytes_CHAR_INIT(154), \
            _PyBytes_CHAR_INIT(155), \
            _PyBytes_CHAR_INIT(156), \
            _PyBytes_CHAR_INIT(157), \
            _PyBytes_CHAR_INIT(158), \
            _PyBytes_CHAR_INIT(159), \
            _PyBytes_CHAR_INIT(160), \
            _PyBytes_CHAR_INIT(161), \
            _PyBytes_CHAR_INIT(162), \
            _PyBytes_CHAR_INIT(163), \
            _PyBytes_CHAR_INIT(164), \
            _PyBytes_CHAR_INIT(165), \
            _PyBytes_CHAR_INIT(166), \
            _PyBytes_CHAR_INIT(167), \
            _PyBytes_CHAR_INIT(168), \
            _PyBytes_CHAR_INIT(169), \
            _PyBytes_CHAR_INIT(170), \
            _PyBytes_CHAR_INIT(171), \
            _PyBytes_CHAR_INIT(172), \
            _PyBytes_CHAR_INIT(173), \
            _PyBytes_CHAR_INIT(174), \
            _PyBytes_CHAR_INIT(175), \
            _PyBytes_CHAR_INIT(176), \
            _PyBytes_CHAR_INIT(177), \
            _PyBytes_CHAR_INIT(178), \
            _PyBytes_CHAR_INIT(179), \
            _PyBytes_CHAR_INIT(180), \
            _PyBytes_CHAR_INIT(181), \
            _PyBytes_CHAR_INIT(182), \
            _PyBytes_CHAR_INIT(183), \
            _PyBytes_CHAR_INIT(184), \
            _PyBytes_CHAR_INIT(185), \
            _PyBytes_CHAR_INIT(186), \
            _PyBytes_CHAR_INIT(187), \
            _PyBytes_CHAR_INIT(188), \
            _PyBytes_CHAR_INIT(189), \
            _PyBytes_CHAR_INIT(190), \
            _PyBytes_CHAR_INIT(191), \
            _PyBytes_CHAR_INIT(192), \
            _PyBytes_CHAR_INIT(193), \
            _PyBytes_CHAR_INIT(194), \
            _PyBytes_CHAR_INIT(195), \
            _PyBytes_CHAR_INIT(196), \
            _PyBytes_CHAR_INIT(197), \
            _PyBytes_CHAR_INIT(198), \
            _PyBytes_CHAR_INIT(199), \
            _PyBytes_CHAR_INIT(200), \
            _PyBytes_CHAR_INIT(201), \
            _PyBytes_CHAR_INIT(202), \
            _PyBytes_CHAR_INIT(203), \
            _PyBytes_CHAR_INIT(204), \
            _PyBytes_CHAR_INIT(205), \
            _PyBytes_CHAR_INIT(206), \
            _PyBytes_CHAR_INIT(207), \
            _PyBytes_CHAR_INIT(208), \
            _PyBytes_CHAR_INIT(209), \
            _PyBytes_CHAR_INIT(210), \
            _PyBytes_CHAR_INIT(211), \
            _PyBytes_CHAR_INIT(212), \
            _PyBytes_CHAR_INIT(213), \
            _PyBytes_CHAR_INIT(214), \
            _PyBytes_CHAR_INIT(215), \
            _PyBytes_CHAR_INIT(216), \
            _PyBytes_CHAR_INIT(217), \
            _PyBytes_CHAR_INIT(218), \
            _PyBytes_CHAR_INIT(219), \
            _PyBytes_CHAR_INIT(220), \
            _PyBytes_CHAR_INIT(221), \
            _PyBytes_CHAR_INIT(222), \
            _PyBytes_CHAR_INIT(223), \
            _PyBytes_CHAR_INIT(224), \
            _PyBytes_CHAR_INIT(225), \
            _PyBytes_CHAR_INIT(226), \
            _PyBytes_CHAR_INIT(227), \
            _PyBytes_CHAR_INIT(228), \
            _PyBytes_CHAR_INIT(229), \
            _PyBytes_CHAR_INIT(230), \
            _PyBytes_CHAR_INIT(231), \
            _PyBytes_CHAR_INIT(232), \
            _PyBytes_CHAR_INIT(233), \
            _PyBytes_CHAR_INIT(234), \
            _PyBytes_CHAR_INIT(235), \
            _PyBytes_CHAR_INIT(236), \
            _PyBytes_CHAR_INIT(237), \
            _PyBytes_CHAR_INIT(238), \
            _PyBytes_CHAR_INIT(239), \
            _PyBytes_CHAR_INIT(240), \
            _PyBytes_CHAR_INIT(241), \
            _PyBytes_CHAR_INIT(242), \
            _PyBytes_CHAR_INIT(243), \
            _PyBytes_CHAR_INIT(244), \
            _PyBytes_CHAR_INIT(245), \
            _PyBytes_CHAR_INIT(246), \
            _PyBytes_CHAR_INIT(247), \
            _PyBytes_CHAR_INIT(248), \
            _PyBytes_CHAR_INIT(249), \
            _PyBytes_CHAR_INIT(250), \
            _PyBytes_CHAR_INIT(251), \
            _PyBytes_CHAR_INIT(252), \
            _PyBytes_CHAR_INIT(253), \
            _PyBytes_CHAR_INIT(254), \
            _PyBytes_CHAR_INIT(255), \
        }, \
        \
        .strings = { \
            .identifiers = { \
                INIT_ID(Py_Repr), \
                INIT_ID(TextIOWrapper), \
                INIT_ID(WarningMessage), \
                INIT_ID(_), \
                INIT_ID(__IOBase_closed), \
                INIT_ID(__abs__), \
                INIT_ID(__abstractmethods__), \
                INIT_ID(__add__), \
                INIT_ID(__aenter__), \
                INIT_ID(__aexit__), \
                INIT_ID(__aiter__), \
                INIT_ID(__all__), \
                INIT_ID(__and__), \
                INIT_ID(__anext__), \
                INIT_ID(__annotations__), \
                INIT_ID(__await__), \
                INIT_ID(__bases__), \
                INIT_ID(__bool__), \
                INIT_ID(__build_class__), \
                INIT_ID(__builtins__), \
                INIT_ID(__bytes__), \
                INIT_ID(__call__), \
                INIT_ID(__class__), \
                INIT_ID(__class_getitem__), \
                INIT_ID(__classcell__), \
                INIT_ID(__complex__), \
                INIT_ID(__contains__), \
                INIT_ID(__copy__), \
                INIT_ID(__del__), \
                INIT_ID(__delattr__), \
                INIT_ID(__delete__), \
                INIT_ID(__delitem__), \
                INIT_ID(__dict__), \
                INIT_ID(__dir__), \
                INIT_ID(__divmod__), \
                INIT_ID(__doc__), \
                INIT_ID(__enter__), \
                INIT_ID(__eq__), \
                INIT_ID(__exit__), \
                INIT_ID(__file__), \
                INIT_ID(__float__), \
                INIT_ID(__floordiv__), \
                INIT_ID(__format__), \
                INIT_ID(__fspath__), \
                INIT_ID(__ge__), \
                INIT_ID(__get__), \
                INIT_ID(__getattr__), \
                INIT_ID(__getattribute__), \
                INIT_ID(__getitem__), \
                INIT_ID(__getnewargs__), \
                INIT_ID(__getnewargs_ex__), \
                INIT_ID(__getstate__), \
                INIT_ID(__gt__), \
                INIT_ID(__hash__), \
                INIT_ID(__iadd__), \
                INIT_ID(__iand__), \
                INIT_ID(__ifloordiv__), \
                INIT_ID(__ilshift__), \
                INIT_ID(__imatmul__), \
                INIT_ID(__imod__), \
                INIT_ID(__import__), \
                INIT_ID(__imul__), \
                INIT_ID(__index__), \
                INIT_ID(__init__), \
                INIT_ID(__init_subclass__), \
                INIT_ID(__instancecheck__), \
                INIT_ID(__int__), \
                INIT_ID(__invert__), \
                INIT_ID(__ior__), \
                INIT_ID(__ipow__), \
                INIT_ID(__irshift__), \
                INIT_ID(__isabstractmethod__), \
                INIT_ID(__isub__), \
                INIT_ID(__iter__), \
                INIT_ID(__itruediv__), \
                INIT_ID(__ixor__), \
                INIT_ID(__le__), \
                INIT_ID(__len__), \
                INIT_ID(__length_hint__), \
                INIT_ID(__loader__), \
                INIT_ID(__lshift__), \
                INIT_ID(__lt__), \
                INIT_ID(__ltrace__), \
                INIT_ID(__main__), \
                INIT_ID(__matmul__), \
                INIT_ID(__missing__), \
                INIT_ID(__mod__), \
                INIT_ID(__module__), \
                INIT_ID(__mro_entries__), \
                INIT_ID(__mul__), \
                INIT_ID(__name__), \
                INIT_ID(__ne__), \
                INIT_ID(__neg__), \
                INIT_ID(__new__), \
                INIT_ID(__newobj__), \
                INIT_ID(__newobj_ex__), \
                INIT_ID(__next__), \
                INIT_ID(__or__), \
                INIT_ID(__package__), \
                INIT_ID(__path__), \
                INIT_ID(__pos__), \
                INIT_ID(__pow__), \
                INIT_ID(__prepare__), \
                INIT_ID(__qualname__), \
                INIT_ID(__radd__), \
                INIT_ID(__rand__), \
                INIT_ID(__rdivmod__), \
                INIT_ID(__reduce__), \
                INIT_ID(__repr__), \
                INIT_ID(__reversed__), \
                INIT_ID(__rfloordiv__), \
                INIT_ID(__rlshift__), \
                INIT_ID(__rmatmul__), \
                INIT_ID(__rmod__), \
                INIT_ID(__rmul__), \
                INIT_ID(__ror__), \
                INIT_ID(__round__), \
                INIT_ID(__rpow__), \
                INIT_ID(__rrshift__), \
                INIT_ID(__rshift__), \
                INIT_ID(__rsub__), \
                INIT_ID(__rtruediv__), \
                INIT_ID(__rxor__), \
                INIT_ID(__set__), \
                INIT_ID(__set_name__), \
                INIT_ID(__setattr__), \
                INIT_ID(__setitem__), \
                INIT_ID(__setstate__), \
                INIT_ID(__sizeof__), \
                INIT_ID(__slotnames__), \
                INIT_ID(__slots__), \
                INIT_ID(__spec__), \
                INIT_ID(__str__), \
                INIT_ID(__sub__), \
                INIT_ID(__subclasscheck__), \
                INIT_ID(__subclasshook__), \
                INIT_ID(__truediv__), \
                INIT_ID(__trunc__), \
                INIT_ID(__warningregistry__), \
                INIT_ID(__xor__), \
                INIT_ID(_abc_impl), \
                INIT_ID(_blksize), \
                INIT_ID(_bootstrap), \
                INIT_ID(_dealloc_warn), \
                INIT_ID(_finalizing), \
                INIT_ID(_find_and_load), \
                INIT_ID(_fix_up_module), \
                INIT_ID(_get_sourcefile), \
                INIT_ID(_handle_fromlist), \
                INIT_ID(_initializing), \
                INIT_ID(_is_text_encoding), \
                INIT_ID(_lock_unlock_module), \
                INIT_ID(_showwarnmsg), \
                INIT_ID(_shutdown), \
                INIT_ID(_slotnames), \
                INIT_ID(_strptime_time), \
                INIT_ID(_warn_unawaited_coroutine), \
                INIT_ID(_xoptions), \
                INIT_ID(big), \
                INIT_ID(buffer), \
                INIT_ID(builtins), \
                INIT_ID(c_call), \
                INIT_ID(c_exception), \
                INIT_ID(c_return), \
                INIT_ID(call), \
                INIT_ID(clear), \
                INIT_ID(close), \
                INIT_ID(closed), \
                INIT_ID(code), \
                INIT_ID(copy), \
                INIT_ID(copyreg), \
                INIT_ID(decode), \
                INIT_ID(defaultaction), \
                INIT_ID(difference_update), \
                INIT_ID(displayhook), \
                INIT_ID(enable), \
                INIT_ID(encode), \
                INIT_ID(encoding), \
                INIT_ID(errors), \
                INIT_ID(excepthook), \
                INIT_ID(exception), \
                INIT_ID(extend), \
                INIT_ID(filename), \
                INIT_ID(fileno), \
                INIT_ID(fillvalue), \
                INIT_ID(filters), \
                INIT_ID(flush), \
                INIT_ID(get), \
                INIT_ID(get_source), \
                INIT_ID(getattr), \
                INIT_ID(getpreferredencoding), \
                INIT_ID(getstate), \
                INIT_ID(imp), \
                INIT_ID(importlib), \
                INIT_ID(inf), \
                INIT_ID(intersection_update), \
                INIT_ID(isatty), \
                INIT_ID(items), \
                INIT_ID(iter), \
                INIT_ID(keys), \
                INIT_ID(last_traceback), \
                INIT_ID(last_type), \
                INIT_ID(last_value), \
                INIT_ID(line), \
                INIT_ID(lineno), \
                INIT_ID(little), \
                INIT_ID(locale), \
                INIT_ID(match), \
                INIT_ID(metaclass), \
                INIT_ID(mode), \
                INIT_ID(mro), \
                INIT_ID(msg), \
                INIT_ID(n_fields), \
                INIT_ID(n_sequence_fields), \
                INIT_ID(n_unnamed_fields), \
                INIT_ID(name), \
                INIT_ID(newlines), \
                INIT_ID(offset), \
                INIT_ID(onceregistry), \
                INIT_ID(opcode), \
                INIT_ID(open), \
                INIT_ID(parent), \
                INIT_ID(partial), \
                INIT_ID(path), \
                INIT_ID(peek), \
                INIT_ID(print_file_and_line), \
                INIT_ID(ps1), \
                INIT_ID(ps2), \
                INIT_ID(raw), \
                INIT_ID(read), \
                INIT_ID(read1), \
                INIT_ID(readable), \
                INIT_ID(readall), \
                INIT_ID(readinto), \
                INIT_ID(readinto1), \
                INIT_ID(readline), \
                INIT_ID(reload), \
                INIT_ID(replace), \
                INIT_ID(reset), \
                INIT_ID(return), \
                INIT_ID(reversed), \
                INIT_ID(seek), \
                INIT_ID(seekable), \
                INIT_ID(send), \
                INIT_ID(setstate), \
                INIT_ID(sort), \
                INIT_ID(st_mode), \
                INIT_ID(stderr), \
                INIT_ID(stdin), \
                INIT_ID(stdout), \
                INIT_ID(strict), \
                INIT_ID(struct_rusage), \
                INIT_ID(symmetric_difference_update), \
                INIT_ID(tell), \
                INIT_ID(text), \
                INIT_ID(threading), \
                INIT_ID(throw), \
                INIT_ID(truncate), \
                INIT_ID(unraisablehook), \
                INIT_ID(update), \
                INIT_ID(values), \
                INIT_ID(version), \
                INIT_ID(warnings), \
                INIT_ID(warnoptions), \
                INIT_ID(writable), \
                INIT_ID(write), \
                INIT_ID(zipimporter), \
            }, \
        }, \
    }, \
}
/* End auto-generated code */


#ifdef __cplusplus
}
#endif
#endif /* !Py_INTERNAL_RUNTIME_INIT_H */
