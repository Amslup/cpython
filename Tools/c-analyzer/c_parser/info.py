from collections import namedtuple

from c_analyzer_common import info, util
from c_analyzer_common.util import classonly, _NTBase


def normalize_vartype(vartype):
    """Return the canonical form for a variable type (or func signature)."""
    # We allow empty strring through for semantic reasons.
    if vartype is None:
        return None

    # XXX finish!
    # XXX Return (modifiers, type, pointer)?
    return str(vartype)


class Variable(_NTBase,
               namedtuple('Variable', 'id vartype')):
    """Information about a single variable declaration."""

    __slots__ = ()
    _isstatic = util.Slot()

    @classonly
    def from_parts(cls, filename, funcname, name, vartype, isstatic=False):
        id = info.ID(filename, funcname, name)
        self = cls(id, vartype)
        if isstatic:
            self._isstatic = True
        return self

    def __new__(cls, id, vartype):
        self = super().__new__(
                cls,
                id=info.ID.from_raw(id),
                vartype=normalize_vartype(vartype) if vartype else None,
                )
        return self

    def __hash__(self):
        return hash(self.id)

    def __getattr__(self, name):
        return getattr(self.id, name)

    def _validate_id(self):
        if not self.id:
            raise TypeError('missing id')

        if not self.filename or self.filename == info.UNKNOWN:
            raise TypeError(f'id missing filename ({self.id})')

        if self.funcname and self.funcname == info.UNKNOWN:
            raise TypeError(f'id missing funcname ({self.id})')

        self.id.validate()

    def validate(self):
        """Fail if the object is invalid (i.e. init with bad data)."""
        if self.name == 'id':  # XXX drop this case
            return

        self._validate_id()

        if self.vartype is None or self.vartype == info.UNKNOWN:
            raise TypeError('missing vartype')

    @property
    def isstatic(self):
        try:
            return self._isstatic
        except AttributeError:
            self._isstatic = ('static' in self.vartype.split())
            return self._isstatic

    @property
    def isconst(self):
        return 'const' in self.vartype.split()
