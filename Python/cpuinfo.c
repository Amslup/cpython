#include "Python.h"
#include "pycore_cpuinfo.h"

#include <stdint.h>     // UINT32_C()

/* CPUID input and output registers are 32-bit unsigned integers */
#define CPUID_REG                   uint32_t
/* Check one or more CPUID register bits. */
#define CPUID_CHECK_REG(REG, MASK)  ((((REG) & (MASK)) == (MASK)) ? 0 : 1)

// For now, we only try to enable SIMD instructions for x86-64 Intel CPUs.
// In the future, we should carefully enable support for ARM NEON and POWER
// as well as AMD.
#if defined(__x86_64__) && defined(__GNUC__)
#  include <cpuid.h>      // __cpuid_count()
#  define HAS_CPUID_SUPPORT
#  define HAS_XGETBV_SUPPORT
#elif defined(_M_X64)
#  include <immintrin.h>  // _xgetbv()
#  define HAS_XGETBV_SUPPORT
#  include <intrin.h>     // __cpuidex()
#  define HAS_CPUID_SUPPORT
#else
#  undef HAS_CPUID_SUPPORT
#  undef HAS_XGETBV_SUPPORT
#endif

// Below, we declare macros for guarding the detection of SSE, AVX/AVX2
// and AVX-512 instructions. If the compiler does not even recognize the
// corresponding flags or if we are not on an 64-bit platform we do not
// even try to inspect the output of CPUID for those specific features.
#ifdef HAS_CPUID_SUPPORT
#if defined(Py_CAN_COMPILE_SIMD_SSE_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_SSE2_INSTRUCTIONS)          \
    || defined(Py_CAN_COMPILE_SIMD_SSE3_INSTRUCTIONS)          \
    || defined(Py_CAN_COMPILE_SIMD_SSSE3_INSTRUCTIONS)         \
    || defined(Py_CAN_COMPILE_SIMD_SSE4_1_INSTRUCTIONS)        \
    || defined(Py_CAN_COMPILE_SIMD_SSE4_2_INSTRUCTIONS)        \
    // macros above should be sorted in alphabetical order
#  define SIMD_SSE_INSTRUCTIONS_DETECTION_GUARD
#endif

#if defined(Py_CAN_COMPILE_SIMD_AVX_INSTRUCTIONS)               \
    || defined(Py_CAN_COMPILE_SIMD_AVX_IFMA_INSTRUCTIONS)       \
    || defined(Py_CAN_COMPILE_SIMD_AVX_NE_CONVERT_INSTRUCTIONS) \
    || defined(Py_CAN_COMPILE_SIMD_AVX_VNNI_INSTRUCTIONS)       \
    || defined(Py_CAN_COMPILE_SIMD_AVX_VNNI_INT8_INSTRUCTIONS)  \
    || defined(Py_CAN_COMPILE_SIMD_AVX_VNNI_INT16_INSTRUCTIONS) \
    // macros above should be sorted in alphabetical order
#  define SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD
#endif

#if defined(Py_CAN_COMPILE_SIMD_AVX2_INSTRUCTIONS)              \
    // macros above should be sorted in alphabetical order
#  define SIMD_AVX2_INSTRUCTIONS_DETECTION_GUARD
#endif

#if defined(Py_CAN_COMPILE_SIMD_AVX512_BITALG_INSTRUCTIONS)             \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_BW_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_CD_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_DQ_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_ER_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_F_INSTRUCTIONS)               \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_IFMA_INSTRUCTIONS)            \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_PF_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_VBMI_INSTRUCTIONS)            \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_VBMI2_INSTRUCTIONS)           \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_VL_INSTRUCTIONS)              \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_VNNI_INSTRUCTIONS)            \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_VP2INTERSECT_INSTRUCTIONS)    \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_VPOPCNTDQ_INSTRUCTIONS)       \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_4FMAPS_INSTRUCTIONS)          \
    || defined(Py_CAN_COMPILE_SIMD_AVX512_4VNNIW_INSTRUCTIONS)          \
    // macros above should be sorted in alphabetical order
#  define SIMD_AVX512_INSTRUCTIONS_DETECTION_GUARD
#endif
#endif // HAS_CPUID_SUPPORT

// On macOS, checking the XCR0 register is NOT a guaranteed way
// to ensure the usability of AVX-512. As such, we disable the
// entire set of AVX-512 instructions.
//
// See https://stackoverflow.com/a/72523150/9579194.
#if defined(__APPLE__)
#  undef SIMD_AVX512_INSTRUCTIONS_DETECTION_GUARD
   // Additionally, AVX2 cannot be compiled on macOS ARM64 (yet it can be
   // compiled on x86_64). However, since autoconf incorrectly assumes so
   // when compiling a universal2 binary, we disable SIMD on such builds.
#  if defined(__aarch64__) || defined(__arm64__)
#    undef SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD
#    undef SIMD_AVX2_INSTRUCTIONS_DETECTION_GUARD
#  endif
#endif

// Below, we declare macros indicating how CPUID can be called at runtime,
// so that we only call CPUID with specific inputs when needed.

#if defined(SIMD_SSE_INSTRUCTIONS_DETECTION_GUARD)      \
    || defined(SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD)
/* Indicate that cpuid should be called once with EAX=1 and ECX=0. */
#  define SHOULD_PARSE_CPUID_L1
#endif

#if defined(SIMD_AVX2_INSTRUCTIONS_DETECTION_GUARD)         \
    || defined(SIMD_AVX512_INSTRUCTIONS_DETECTION_GUARD)
/* Indicate that cpuid should be called once with EAX=7 and ECX=0. */
#  define SHOULD_PARSE_CPUID_L7
#  define SHOULD_PARSE_CPUID_L7S0
#endif

#if defined(SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD)
/* Indicate that cpuid should be called once with EAX=7 and ECX=1. */
#  define SHOULD_PARSE_CPUID_L7
#  define SHOULD_PARSE_CPUID_L7S1
#endif

/*
 * The macros below describe masks to apply on CPUID output registers.
 *
 * Each macro is of the form <REGISTER>_L<LEAF>[S<SUBLEAF>]_<FEATURE>,
 * where <> (resp. []) denotes a required (resp. optional) group and:
 *
 * - REGISTER is EAX, EBX, ECX or EDX,
 * - LEAF is the initial value of the EAX register (1 or 7),
 * - SUBLEAF is the initial value of the ECX register (omitted if 0), and
 * - FEATURE is a SIMD feature (with one or more specialized instructions).
 *
 * For maintainability, the flags are ordered by registers, leafs, subleafs,
 * and bits. See https://en.wikipedia.org/wiki/CPUID for the values.
 *
 * Note 1: The LEAF is also called the 'page' or the 'level'.
 * Note 2: The SUBLEAF is also referred to as the 'count'.
 */

/* CPUID (LEAF=1, SUBLEAF=0) [ECX] */
#define ECX_L1_SSE3                 (UINT32_C(1) << 0)  // 0x00000001
#define ECX_L1_PCLMULQDQ            (UINT32_C(1) << 1)  // 0x00000002
#define ECX_L1_SSSE3                (UINT32_C(1) << 9)  // 0x00000200
#define ECX_L1_FMA                  (UINT32_C(1) << 12) // 0x00001000
#define ECX_L1_SSE4_1               (UINT32_C(1) << 19) // 0x00080000
#define ECX_L1_SSE4_2               (UINT32_C(1) << 20) // 0x00100000
#define ECX_L1_POPCNT               (UINT32_C(1) << 23) // 0x00800000
#define ECX_L1_XSAVE                (UINT32_C(1) << 26) // 0x04000000
#define ECX_L1_OSXSAVE              (UINT32_C(1) << 27) // 0x08000000
#define ECX_L1_AVX                  (UINT32_C(1) << 28) // 0x10000000
/* CPUID (LEAF=1, SUBLEAF=0) [EDX] */
#define EDX_L1_CMOV                 (UINT32_C(1) << 15) // 0x00008000
#define EDX_L1_SSE                  (UINT32_C(1) << 25) // 0x02000000
#define EDX_L1_SSE2                 (UINT32_C(1) << 26) // 0x04000000
/* CPUID (LEAF=7, SUBLEAF=0) [EBX] */
#define EBX_L7_AVX2                 (UINT32_C(1) << 5)  // 0x00000020
#define EBX_L7_AVX512_F             (UINT32_C(1) << 16) // 0x00010000
#define EBX_L7_AVX512_DQ            (UINT32_C(1) << 17) // 0x00020000
#define EBX_L7_AVX512_IFMA          (UINT32_C(1) << 21) // 0x00200000
#define EBX_L7_AVX512_PF            (UINT32_C(1) << 26) // 0x04000000
#define EBX_L7_AVX512_ER            (UINT32_C(1) << 27) // 0x08000000
#define EBX_L7_AVX512_CD            (UINT32_C(1) << 28) // 0x10000000
#define EBX_L7_AVX512_BW            (UINT32_C(1) << 30) // 0x40000000
#define EBX_L7_AVX512_VL            (UINT32_C(1) << 31) // 0x80000000
/* CPUID (LEAF=7, SUBLEAF=0) [ECX] */
#define ECX_L7_AVX512_VBMI          (UINT32_C(1) << 1)  // 0x00000002
#define ECX_L7_AVX512_VBMI2         (UINT32_C(1) << 6)  // 0x00000040
#define ECX_L7_AVX512_VNNI          (UINT32_C(1) << 11) // 0x00000800
#define ECX_L7_AVX512_BITALG        (UINT32_C(1) << 12) // 0x00001000
#define ECX_L7_AVX512_VPOPCNTDQ     (UINT32_C(1) << 14) // 0x00004000
/* CPUID (LEAF=7, SUBLEAF=0) [EDX] */
#define EDX_L7_AVX512_4VNNIW        (UINT32_C(1) << 2)  // 0x00000004
#define EDX_L7_AVX512_4FMAPS        (UINT32_C(1) << 3)  // 0x00000008
#define EDX_L7_AVX512_VP2INTERSECT  (UINT32_C(1) << 8)  // 0x00000100
/* CPUID (LEAF=7, SUBLEAF=1) [EAX] */
#define EAX_L7S1_AVX_VNNI           (UINT32_C(1) << 4)  // 0x00000010
#define EAX_L7S1_AVX_IFMA           (UINT32_C(1) << 23) // 0x00800000
/* CPUID (LEAF=7, SUBLEAF=1) [EDX] */
#define EDX_L7S1_AVX_VNNI_INT8      (UINT32_C(1) << 4)  // 0x00000010
#define EDX_L7S1_AVX_NE_CONVERT     (UINT32_C(1) << 5)  // 0x00000020
#define EDX_L7S1_AVX_VNNI_INT16     (UINT32_C(1) << 10) // 0x00000400

/*
 * Call __cpuid_count() or equivalent and get
 * its EAX, EBX, ECX and EDX output registers.
 *
 * If CPUID is not supported, registers are set to 0.
 */
static inline void
get_cpuid_info(uint32_t level /* input eax */,
               uint32_t count /* input ecx */,
               CPUID_REG *eax, CPUID_REG *ebx, CPUID_REG *ecx, CPUID_REG *edx)
{
    *eax = *ebx = *ecx = *edx = 0; // ensure the output to be initialized
#if defined(HAS_CPUID_SUPPORT) && defined(__x86_64__) && defined(__GNUC__)
    __cpuid_count(level, count, *eax, *ebx, *ecx, *edx);
#elif defined(HAS_CPUID_SUPPORT) && defined(_M_X64)
    uint32_t info[4] = {0};
    __cpuidex(info, level, count);
    *eax = info[0], *ebx = info[1], *ecx = info[2], *edx = info[3];
#endif
}

/* XSAVE state components (XCR0 control register) */
#define XCR0_SSE                    (UINT32_C(1) << 1)  // 0x00000002
#define XCR0_AVX                    (UINT32_C(1) << 2)  // 0x00000004
#define XCR0_AVX512_OPMASK          (UINT32_C(1) << 5)  // 0x00000020
#define XCR0_AVX512_ZMM_HI256       (UINT32_C(1) << 6)  // 0x00000040
#define XCR0_AVX512_HI16_ZMM        (UINT32_C(1) << 7)  // 0x00000080

static inline uint64_t
get_xgetbv(uint32_t index)
{
    assert(index == 0); // only XCR0 is supported for now
#if defined(HAS_CPUID_SUPPORT) && defined(__x86_64__) && defined(__GNUC__)
    uint32_t eax = 0, edx = 0;
    __asm__ __volatile__("xgetbv" : "=a" (eax), "=d" (edx) : "c" (index));
    return ((uint64_t)edx << 32) | eax;
#elif defined(HAS_CPUID_SUPPORT) && defined(_M_X64)
    return (uint64_t)_xgetbv(index);
#else
    (void)index;
    return 0;
#endif
}

/* Highest Function Parameter and Manufacturer ID (LEAF=0, SUBLEAF=0). */
static inline uint32_t
detect_cpuid_maxleaf(void)
{
    CPUID_REG maxlevel = 0, ebx = 0, ecx = 0, edx = 0;
    get_cpuid_info(0, 0, &maxlevel, &ebx, &ecx, &edx);
    return maxlevel;
}

/* Processor Info and Feature Bits (LEAF=1, SUBLEAF=0). */
static inline void
detect_cpuid_features(py_cpuid_features *flags, CPUID_REG ecx, CPUID_REG edx)
{
    // Keep the ordering and newlines as they are declared in the structure.
#ifdef SIMD_SSE_INSTRUCTIONS_DETECTION_GUARD
#ifdef Py_CAN_COMPILE_SIMD_SSE_INSTRUCTIONS
    flags->sse = CPUID_CHECK_REG(edx, EDX_L1_SSE);
#endif
#ifdef Py_CAN_COMPILE_SIMD_SSE2_INSTRUCTIONS
    flags->sse2 = CPUID_CHECK_REG(edx, EDX_L1_SSE2);
#endif
#ifdef Py_CAN_COMPILE_SIMD_SSE3_INSTRUCTIONS
    flags->sse3 = CPUID_CHECK_REG(ecx, ECX_L1_SSE3);
#endif
#ifdef Py_CAN_COMPILE_SIMD_SSSE3_INSTRUCTIONS
    flags->ssse3 = CPUID_CHECK_REG(ecx, ECX_L1_SSSE3);
#endif
#ifdef Py_CAN_COMPILE_SIMD_SSE4_1_INSTRUCTIONS
    flags->sse41 = CPUID_CHECK_REG(ecx, ECX_L1_SSE4_1);
#endif
#ifdef Py_CAN_COMPILE_SIMD_SSE4_2_INSTRUCTIONS
    flags->sse42 = CPUID_CHECK_REG(ecx, ECX_L1_SSE4_2);
#endif
#endif // SIMD_SSE_INSTRUCTIONS_DETECTION_GUARD

#ifdef SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD
#ifdef Py_CAN_COMPILE_SIMD_AVX_INSTRUCTIONS
    flags->avx = CPUID_CHECK_REG(ecx, ECX_L1_AVX);
#endif
#endif // SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD

#ifdef HAS_CPUID_SUPPORT
    flags->cmov = CPUID_CHECK_REG(edx, EDX_L1_CMOV);
    flags->fma = CPUID_CHECK_REG(ecx, ECX_L1_FMA);
    flags->popcnt = CPUID_CHECK_REG(ecx, ECX_L1_POPCNT);
    flags->pclmulqdq = CPUID_CHECK_REG(ecx, ECX_L1_PCLMULQDQ);

    flags->xsave = CPUID_CHECK_REG(ecx, ECX_L1_XSAVE);
    flags->os_xsave = CPUID_CHECK_REG(ecx, ECX_L1_OSXSAVE);
#endif
}

/* Extended Feature Bits (LEAF=7, SUBLEAF=0). */
static inline void
detect_cpuid_extended_features_L7S0(py_cpuid_features *flags,
                                    CPUID_REG ebx, CPUID_REG ecx, CPUID_REG edx)
{
    (void)ebx, (void)ecx, (void)edx; // to suppress unused warnings
    // Keep the ordering and newlines as they are declared in the structure.
#ifdef SIMD_AVX2_INSTRUCTIONS_DETECTION_GUARD
#ifdef Py_CAN_COMPILE_SIMD_AVX2_INSTRUCTIONS
    flags->avx2 = CPUID_CHECK_REG(ebx, EBX_L7_AVX2);
#endif
#endif // SIMD_AVX2_INSTRUCTIONS_DETECTION_GUARD

#ifdef SIMD_AVX512_INSTRUCTIONS_DETECTION_GUARD
#ifdef Py_CAN_COMPILE_SIMD_AVX512_F_INSTRUCTIONS
    flags->avx512_f = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_F);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_CD_INSTRUCTIONS
    flags->avx512_cd = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_CD);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_ER_INSTRUCTIONS
    flags->avx512_er = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_ER);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_PF_INSTRUCTIONS
    flags->avx512_pf = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_PF);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_4FMAPS_INSTRUCTIONS
    flags->avx512_4fmaps = CPUID_CHECK_REG(edx, EDX_L7_AVX512_4FMAPS);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_4VNNIW_INSTRUCTIONS
    flags->avx512_4vnniw = CPUID_CHECK_REG(edx, EDX_L7_AVX512_4VNNIW);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_VPOPCNTDQ_INSTRUCTIONS
    flags->avx512_vpopcntdq = CPUID_CHECK_REG(ecx, ECX_L7_AVX512_VPOPCNTDQ);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_VL_INSTRUCTIONS
    flags->avx512_vl = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_VL);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_DQ_INSTRUCTIONS
    flags->avx512_dq = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_DQ);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_BW_INSTRUCTIONS
    flags->avx512_bw = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_BW);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_IFMA_INSTRUCTIONS
    flags->avx512_ifma = CPUID_CHECK_REG(ebx, EBX_L7_AVX512_IFMA);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_VBMI_INSTRUCTIONS
    flags->avx512_vbmi = CPUID_CHECK_REG(ecx, ECX_L7_AVX512_VBMI);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_VNNI_INSTRUCTIONS
    flags->avx512_vnni = CPUID_CHECK_REG(ecx, ECX_L7_AVX512_VNNI);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_VBMI2_INSTRUCTIONS
    flags->avx512_vbmi2 = CPUID_CHECK_REG(ecx, ECX_L7_AVX512_VBMI2);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX512_BITALG_INSTRUCTIONS
    flags->avx512_bitalg = CPUID_CHECK_REG(ecx, ECX_L7_AVX512_BITALG);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX512_VP2INTERSECT_INSTRUCTIONS
    flags->avx512_vp2intersect = CPUID_CHECK_REG(edx, EDX_L7_AVX512_VP2INTERSECT);
#endif
#endif // SIMD_AVX512_INSTRUCTIONS_DETECTION_GUARD
}

/* Extended Feature Bits (LEAF=7, SUBLEAF=1). */
static inline void
detect_cpuid_extended_features_L7S1(py_cpuid_features *flags,
                                    CPUID_REG eax,
                                    CPUID_REG ebx,
                                    CPUID_REG ecx,
                                    CPUID_REG edx)
{
    (void)eax, (void)ebx, (void)ecx, (void)edx; // to suppress unused warnings
    // Keep the ordering and newlines as they are declared in the structure.
#ifdef SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD
#ifdef Py_CAN_COMPILE_SIMD_AVX_NE_CONVERT_INSTRUCTIONS
    flags->avx_ne_convert = CPUID_CHECK_REG(edx, EDX_L7S1_AVX_NE_CONVERT);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX_IFMA_INSTRUCTIONS
    flags->avx_ifma = CPUID_CHECK_REG(eax, EAX_L7S1_AVX_IFMA);
#endif

#ifdef Py_CAN_COMPILE_SIMD_AVX_VNNI_INSTRUCTIONS
    flags->avx_vnni = CPUID_CHECK_REG(eax, EAX_L7S1_AVX_VNNI);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX_VNNI_INT8_INSTRUCTIONS
    flags->avx_vnni_int8 = CPUID_CHECK_REG(edx, EDX_L7S1_AVX_VNNI_INT8);
#endif
#ifdef Py_CAN_COMPILE_SIMD_AVX_VNNI_INT16_INSTRUCTIONS
    flags->avx_vnni_int16 = CPUID_CHECK_REG(edx, EDX_L7S1_AVX_VNNI_INT16);
#endif
#endif // SIMD_AVX_INSTRUCTIONS_DETECTION_GUARD
}

static inline void
detect_cpuid_xsave_state(py_cpuid_features *flags)
{
    // Keep the ordering and newlines as they are declared in the structure.
#ifdef HAS_XGETBV_SUPPORT
    uint64_t xcr0 = flags->os_xsave ? get_xgetbv(0) : 0;
    flags->xcr0_sse = CPUID_CHECK_REG(xcr0, XCR0_SSE);
    flags->xcr0_avx = CPUID_CHECK_REG(xcr0, XCR0_AVX);
    flags->xcr0_avx512_opmask = CPUID_CHECK_REG(xcr0, XCR0_AVX512_OPMASK);
    flags->xcr0_avx512_zmm_hi256 = CPUID_CHECK_REG(xcr0, XCR0_AVX512_ZMM_HI256);
    flags->xcr0_avx512_hi16_zmm = CPUID_CHECK_REG(xcr0, XCR0_AVX512_HI16_ZMM);
#endif
}

static inline void
cpuid_features_finalize(py_cpuid_features *flags)
{
    assert(flags->ready == 0);

    // Here, any flag that may depend on others should be correctly set
    // at runtime to avoid illegal instruction errors.

    flags->ready = 1;
}

static inline int
cpuid_features_validate(const py_cpuid_features *flags)
{
    if (flags->ready != 1) {
        return -1;
    }

    // AVX-512/F is required to support any other AVX-512 instruction set
    uint8_t avx512_require_f = (
        // newlines are placed according to processor generations
        flags->avx512_cd ||
        flags->avx512_er || flags->avx512_pf ||
        flags->avx512_4fmaps || flags->avx512_4vnniw ||
        flags->avx512_vpopcntdq ||
        flags->avx512_vl || flags->avx512_dq || flags->avx512_bw ||
        flags->avx512_ifma || flags->avx512_vbmi ||
        flags->avx512_vnni ||
        flags->avx512_vbmi2 || flags->avx512_bitalg ||
        flags->avx512_vp2intersect
    );

    if (!flags->avx512_f && !avx512_require_f) {
        return -1;
    }

    return 0;
}

int
_Py_cpuid_check_features(const py_cpuid_features *flags)
{
    return cpuid_features_validate(flags) < 0 ? 0 : 1;
}

/*
 * Apply a 1-parameter macro MACRO(FLAG) on all members
 * of a 'py_cpuid_features' object ('ready' is omitted).
 */
#define CPUID_APPLY_MACRO(MACRO)        \
    do {                                \
        MACRO(sse);                     \
        MACRO(sse2);                    \
        MACRO(sse3);                    \
        MACRO(ssse3);                   \
        MACRO(sse41);                   \
        MACRO(sse42);                   \
                                        \
        MACRO(avx);                     \
        MACRO(avx_ifma);                \
        MACRO(avx_ne_convert);          \
                                        \
        MACRO(avx_vnni);                \
        MACRO(avx_vnni_int8);           \
        MACRO(avx_vnni_int16);          \
                                        \
        MACRO(avx2);                    \
                                        \
        MACRO(avx512_f);                \
        MACRO(avx512_cd);               \
                                        \
        MACRO(avx512_er);               \
        MACRO(avx512_pf);               \
                                        \
        MACRO(avx512_4fmaps);           \
        MACRO(avx512_4vnniw);           \
                                        \
        MACRO(avx512_vpopcntdq);        \
                                        \
        MACRO(avx512_vl);               \
        MACRO(avx512_dq);               \
        MACRO(avx512_bw);               \
                                        \
        MACRO(avx512_ifma);             \
        MACRO(avx512_vbmi);             \
                                        \
        MACRO(avx512_vnni);             \
                                        \
        MACRO(avx512_vbmi2);            \
        MACRO(avx512_bitalg);           \
                                        \
        MACRO(avx512_vp2intersect);     \
                                        \
        MACRO(cmov);                    \
        MACRO(fma);                     \
        MACRO(popcnt);                  \
        MACRO(pclmulqdq);               \
                                        \
        MACRO(xsave);                   \
        MACRO(os_xsave);                \
                                        \
        MACRO(xcr0_sse);                \
        MACRO(xcr0_avx);                \
        MACRO(xcr0_avx512_opmask);      \
        MACRO(xcr0_avx512_zmm_hi256);   \
        MACRO(xcr0_avx512_hi16_zmm);    \
    } while (0)

void
_Py_cpuid_disable_features(py_cpuid_features *flags)
{
#define CPUID_DISABLE(FLAG)    flags->FLAG = 0
    CPUID_APPLY_MACRO(CPUID_DISABLE);
#undef CPUID_DISABLE
}

int
_Py_cpuid_has_features(const py_cpuid_features *actual,
                       const py_cpuid_features *expect)
{
    if (!actual->ready || !expect->ready) {
        return 0;
    }
#define CPUID_CHECK_FEATURE(FLAG)               \
    do {                                        \
        if (expect->FLAG && !actual->FLAG) {    \
            return 0;                           \
        }                                       \
    } while (0)
    CPUID_APPLY_MACRO(CPUID_CHECK_FEATURE);
#undef CPUID_CHECK_FEATURE
    return 1;
}

int
_Py_cpuid_match_features(const py_cpuid_features *actual,
                         const py_cpuid_features *expect)
{
    if (!actual->ready || !expect->ready) {
        return 0;
    }
#define CPUID_MATCH_FEATURE(FLAG)           \
    do {                                    \
        if (expect->FLAG != actual->FLAG) { \
            return 0;                       \
        }                                   \
    } while (0)
    CPUID_APPLY_MACRO(CPUID_MATCH_FEATURE);
#undef CPUID_MATCH_FEATURE
    return 1;
}

#undef CPUID_APPLY_MACRO

void
_Py_cpuid_detect_features(py_cpuid_features *flags)
{
    if (flags->ready) {
        return;
    }
    _Py_cpuid_disable_features(flags);
#ifdef HAS_CPUID_SUPPORT
    uint32_t maxleaf = detect_cpuid_maxleaf();
    (void)maxleaf;                              // to suppress unused warnings
    CPUID_REG eax = 0, ebx = 0, ecx = 0, edx = 0;
    (void)eax, (void)ebx, (void)ecx, (void)edx; // to suppress unused warnings

#ifdef SHOULD_PARSE_CPUID_L1
    if (maxleaf >= 1) {
        eax = 0, ebx = 0, ecx = 0, edx = 0;
        get_cpuid_info(1, 0, &eax, &ebx, &ecx, &edx);
        detect_cpuid_features(flags, ecx, edx);
        if (flags->os_xsave) {
            detect_cpuid_xsave_state(flags);
        }
    }
#endif // SHOULD_PARSE_CPUID_L1

#ifdef SHOULD_PARSE_CPUID_L7
    if (maxleaf >= 7) {
#ifdef SHOULD_PARSE_CPUID_L7S0
        eax = 0, ebx = 0, ecx = 0, edx = 0;
        get_cpuid_info(7, 0, &eax, &ebx, &ecx, &edx);
        detect_cpuid_extended_features_L7S0(flags, ebx, ecx, edx);
#endif
#ifdef SHOULD_PARSE_CPUID_L7S1
        eax = 0, ebx = 0, ecx = 0, edx = 0;
        get_cpuid_info(7, 1, &eax, &ebx, &ecx, &edx);
        detect_cpuid_extended_features_L7S1(flags, eax, ebx, ecx, edx);
#endif
    }
#endif // SHOULD_PARSE_CPUID_L7
    cpuid_features_finalize(flags);
    if (cpuid_features_validate(flags) < 0) {
        _Py_cpuid_disable_features(flags);
    }
#else
    flags->ready = 1;
#endif // HAS_CPUID_SUPPORT
}
