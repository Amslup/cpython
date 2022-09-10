"""Python implementations of some algorithms for use by longobject.c.
The goal is to provide asymptotically faster algorithms that can be
used for operations on integers with many digits.  In those cases, the
performance overhead of the Python implementation is not significant
since the asymptotic behavior is what dominates runtime. Functions
provided by this module should be considered private and not part of any
public API.

Note: for ease of maintainability, please prefer clear code and avoid
"micro-optimizations".  This module will only be imported and used for
integers with a huge number of digits.  Saving a few microseconds with
tricky or non-obvious code is not worth it.  For people looking for
maximum performance, they should use something like gmpy2."""

import sys
import io
import re
import decimal
import functools

_DEBUG = False


def int_to_decimal(n):
    """Asymptotically fast conversion of an 'int' to Decimal."""

    # Function due to Tim Peters.  See GH issue #90716 for details.
    # https://github.com/python/cpython/issues/90716
    #
    # The implementation in longobject.c of base conversion algorithms
    # between power-of-2 and non-power-of-2 bases are quadratic time.
    # This function implements a divide-and-conquer algorithm that is
    # faster for large numbers.  Builds an equal decimal.Decimal in a
    # "clever" recursive way.  If we want a string representation, we
    # apply str to _that_.

    if _DEBUG:
        print('int_to_decimal', n.bit_length(), file=sys.stderr)

    D = decimal.Decimal
    D2 = D(2)

    BITLIM = 128

    mem = {}

    def w2pow(w):
        """Return D(2)**w and store the result. Also possibly save some
        intermediate results. In context, these are likely to be reused
        across various levels of the conversion to Decimal."""
        if (result := mem.get(w)) is None:
            if w <= BITLIM:
                result = D2**w
            elif w - 1 in mem:
                result = (t := mem[w - 1]) + t
            else:
                w2 = w >> 1
                # If w happens to be odd, w-w2 is one larger then w2
                # now. Recurse on the smaller first (w2), so that it's
                # in the cache and the larger (w-w2) can be handled by
                # the cheaper `w-1 in mem` branch instead.
                result = w2pow(w2) * w2pow(w - w2)
            mem[w] = result
        return result

    def inner(n, w):
        if w <= BITLIM:
            return D(n)
        w2 = w >> 1
        hi = n >> w2
        lo = n - (hi << w2)
        return inner(lo, w2) + inner(hi, w - w2) * w2pow(w2)

    with decimal.localcontext() as ctx:
        ctx.prec = decimal.MAX_PREC
        ctx.Emax = decimal.MAX_EMAX
        ctx.Emin = decimal.MIN_EMIN
        ctx.traps[decimal.Inexact] = 1

        if n < 0:
            negate = True
            n = -n
        else:
            negate = False
        result = inner(n, n.bit_length())
        if negate:
            result = -result
    return result


def int_to_decimal_string(n):
    """Asymptotically fast conversion of an 'int' to a decimal string."""
    return str(int_to_decimal(n))


# Fast integer division, based on code from mdickinson, fast_div.py GH #47701

_DIV_LIMIT = 1000


def _div2n1n(a, b, n):
    """Divide a 2n-bit nonnegative integer a by an n-bit positive integer
    b, using a recursive divide-and-conquer algorithm.

    Inputs:
      n is a positive integer
      b is a positive integer with exactly n bits
      a is a nonnegative integer such that a < 2**n * b

    Output:
      (q, r) such that a = b*q+r and 0 <= r < b.

    """
    if n <= _DIV_LIMIT:
        return divmod(a, b)
    pad = n & 1
    if pad:
        a <<= 1
        b <<= 1
        n += 1
    half_n = n >> 1
    mask = (1 << half_n) - 1
    b1, b2 = b >> half_n, b & mask
    q1, r = _div3n2n(a >> n, (a >> half_n) & mask, b, b1, b2, half_n)
    q2, r = _div3n2n(r, a & mask, b, b1, b2, half_n)
    if pad:
        r >>= 1
    return q1 << half_n | q2, r


def _div3n2n(a12, a3, b, b1, b2, n):
    """Helper function for _div2n1n; not intended to be called directly."""
    if a12 >> n == b1:
        q, r = (1 << n) - 1, a12 - (b1 << n) + b1
    else:
        q, r = _div2n1n(a12, b1, n)
    r = (r << n | a3) - q * b2
    while r < 0:
        q -= 1
        r += b
    return q, r


def _divmod_pos(a, b):
    """Divide a positive integer a by a positive integer b, giving
    quotient and remainder."""
    # Use grade-school algorithm in base 2**n, n = nbits(b)
    n = len(bin(b)) - 2
    mask = (1 << n) - 1
    a_digits = []
    while a:
        a_digits.append(a & mask)
        a >>= n
    r = 0 if a_digits[-1] >= b else a_digits.pop()
    q = 0
    while a_digits:
        q_digit, r = _div2n1n((r << n) + a_digits.pop(), b, n)
        q = (q << n) + q_digit
    return q, r


def int_divmod(a, b):
    """Asymptotically fast replacement for divmod, for 'int'."""
    if _DEBUG:
        print('int_divmod', b.bit_length(), file=sys.stderr)
    if b == 0:
        raise ZeroDivisionError
    elif b < 0:
        q, r = int_divmod(-a, -b)
        return q, -r
    elif a < 0:
        q, r = int_divmod(~a, b)
        return ~q, b + ~r
    elif a == 0:
        return 0, 0
    else:
        return _divmod_pos(a, b)


# Based on code from bjorn-martinsson GH-90716, str-to-int conversion


def _str_to_int_inner(s):
    @functools.cache
    def pow5(n):
        if n <= 5:
            return 5 ** (1 << n)
        else:
            p = pow5(n - 1)
            return p * p

    def inner(a, b):
        if b - a <= 3000:
            return int(s[a:b])
        lg_split = (b - a - 1).bit_length() - 1
        split = 1 << lg_split
        x = (inner(a, b - split) * pow5(lg_split)) << split
        y = inner(b - split, b)
        return x + y

    return inner(0, len(s))


def int_from_string(s):
    """Asymptotically fast version of PyLong_FromString(), conversion
    of a string of decimal digits into an 'int'."""
    if _DEBUG:
        print('int_from_string', len(s), file=sys.stderr)
    # PyLong_FromString() has already removed leading +/-, checked for invalid
    # use of underscore characters and stripped leading whitespace.  The input
    # can still contain underscores and have trailing whitespace.  If not
    # valid, return the index of the first invalid character.
    m = re.match(r'[0-9_]+\s*', s)
    if not m:
        return None, 0
    if m.end() != len(s):
        # Invalid characters at end.
        return None, m.end()
    s = s.rstrip().replace('_', '')
    return _str_to_int_inner(s), None


def str_to_int(s):
    """Asymptotically fast version of decimal string to 'int' conversion."""
    # FIXME: this doesn't support the full syntax that int() supports.
    v, error_index = int_from_string(s)
    if v is not None:
        return v
    raise ValueError('invalid literal for int() with base 10')
