"""
Protocols for supporting classes in pathlib.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class Parser(Protocol):
    """Protocol for path parsers, which do low-level path manipulation.

    Path parsers provide a subset of the os.path API, specifically those
    functions needed to provide PurePathBase functionality. Each PurePathBase
    subclass references its path parser via a 'parser' class attribute.
    """

    sep: str
    def join(self, path: str, *paths: str) -> str: ...
    def split(self, path: str) -> tuple[str, str]: ...
    def splitdrive(self, path: str) -> tuple[str, str]: ...
    def splitext(self, path: str) -> tuple[str, str]: ...
    def normcase(self, path: str) -> str: ...
    def isabs(self, path: str) -> bool: ...


@runtime_checkable
class DirEntry(Protocol):
    """Protocol for directory entries, which store information about directory
    children.

    Directory entries provide a subset of the os.DirEntry API, specifically
    those methods and attributes needed to provide PathBase functionality
    like glob() and walk(). Directory entry objects are generated by
    PathBase.scandir().

    Methods may return cached information for performance reasons, though this
    is not required.

    Path and PathBase implement this protocol, but their is_*() methods always
    fetch up-to-date information.
    """

    name: str
    def is_file(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_dir(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_symlink(self) -> bool: ...


@runtime_checkable
class StatResult(Protocol):
    """Protocol for stat results, which store low-level information about
    files.

    Stat results provide a subset of the os.stat_result API, specifically
    attributes for the file type, permissions and offset.
    """

    st_mode: int
    st_ino: int
    st_dev: int
