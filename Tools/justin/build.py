"""The Justin(time) template JIT for CPython 3.13, based on copy-and-patch."""

import asyncio
import dataclasses
import functools
import itertools
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import typing

TOOLS_JUSTIN = pathlib.Path(__file__).parent
TOOLS_JUSTIN_TEMPLATE = TOOLS_JUSTIN / "template.c"
TOOLS_JUSTIN_TRAMPOLINE = TOOLS_JUSTIN / "trampoline.c"
PYTHON_GENERATED_CASES_C_H = TOOLS_JUSTIN.parent.parent / "Python" / "generated_cases.c.h"

def batched(iterable, n):
    """Batch an iterable into lists of size n."""
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, n))
        if not batch:
            return
        yield batch

class _Value(typing.TypedDict):
    Value: str
    RawValue: int

class Flag(typing.TypedDict):
    Name: str
    Value: int

class Flags(typing.TypedDict):
    RawFlags: int
    Flags: list[Flag]

class SectionData(typing.TypedDict):
    Offset: int
    Bytes: list[int]

class _Name(typing.TypedDict):
    Value: str
    Offset: int
    Bytes: list[int]

class ELFRelocation(typing.TypedDict):
    Offset: int
    Type: _Value
    Symbol: _Value
    Addend: int

class COFFRelocation(typing.TypedDict):
    Offset: int
    Type: _Value
    Symbol: str
    SymbolIndex: int

class MachORelocation(typing.TypedDict):
    Offset: int
    PCRel: int
    Length: int
    Type: _Value
    Symbol: _Value  # XXX
    Section: _Value  # XXX

class COFFAuxSectionDef(typing.TypedDict):
    Length: int
    RelocationCount: int
    LineNumberCount: int
    Checksum: int
    Number: int
    Selection: int

class COFFSymbol(typing.TypedDict):
    Name: str
    Value: int
    Section: _Value
    BaseType: _Value
    ComplexType: _Value
    StorageClass: int
    AuxSymbolCount: int
    AuxSectionDef: COFFAuxSectionDef

class ELFSymbol(typing.TypedDict):
    Name: _Value
    Value: int
    Size: int
    Binding: _Value
    Type: _Value
    Other: int
    Section: _Value

class MachOSymbol(typing.TypedDict):
    Name: _Value
    Type: _Value
    Section: _Value
    RefType: _Value
    Flags: Flags
    Value: int

class ELFSection(typing.TypedDict):
    Index: int
    Name: _Value
    Type: _Value
    Flags: Flags
    Address: int
    Offset: int
    Size: int
    Link: int
    Info: int
    AddressAlignment: int
    EntrySize: int
    Relocations: list[dict[typing.Literal["Relocation"], ELFRelocation]]
    Symbols: list[dict[typing.Literal["Symbol"], ELFSymbol]]
    SectionData: SectionData

class COFFSection(typing.TypedDict):
    Number: int
    Name: _Name
    VirtualSize: int
    VirtualAddress: int
    RawDataSize: int
    PointerToRawData: int
    PointerToRelocations: int
    PointerToLineNumbers: int
    RelocationCount: int
    LineNumberCount: int
    Characteristics: Flags
    Relocations: list[dict[typing.Literal["Relocation"], COFFRelocation]]
    Symbols: list[dict[typing.Literal["Symbol"], COFFSymbol]]
    SectionData: SectionData  # XXX

class MachOSection(typing.TypedDict):
    Index: int
    Name: _Name
    Segment: _Name
    Address: int
    Size: int
    Offset: int
    Alignment: int
    RelocationOffset: int
    RelocationCount: int
    Type: _Value
    Attributes: Flags
    Reserved1: int
    Reserved2: int
    Reserved3: int
    Relocations: list[dict[typing.Literal["Relocation"], MachORelocation]]  # XXX
    Symbols: list[dict[typing.Literal["Symbol"], MachOSymbol]]  # XXX
    SectionData: SectionData  # XXX

S = typing.TypeVar("S", bound=str)
T = typing.TypeVar("T")


def unwrap(source: list[dict[S, T]], wrapper: S) -> list[T]:
    return [child[wrapper] for child in source]

def get_llvm_tool_version(name: str) -> int | None:
    try:
        args = [name, "--version"]
        process = subprocess.run(args, check=True, stdout=subprocess.PIPE)
    except FileNotFoundError:
        return None
    match = re.search(br"version\s+(\d+)\.\d+\.\d+\s+", process.stdout)
    return match and int(match.group(1))

def find_llvm_tool(tool: str) -> tuple[str, int]:
    versions = {14, 15, 16}
    forced_version = os.getenv("PYTHON_LLVM_VERSION")
    if forced_version:
        versions &= {int(forced_version)}
    # Unversioned executables:
    path = tool
    version = get_llvm_tool_version(tool)
    if version in versions:
        return tool, version
    for version in sorted(versions, reverse=True):
        # Versioned executables:
        path = f"{tool}-{version}"
        if get_llvm_tool_version(path) == version:
            return path, version
        # My homebrew homies:
        try:
            args = ["brew", "--prefix", f"llvm@{version}"]
            process = subprocess.run(args, check=True, stdout=subprocess.PIPE)
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        else:
            prefix = process.stdout.decode().removesuffix("\n")
            path = f"{prefix}/bin/{tool}"
            if get_llvm_tool_version(path) == version:
                return path, version
    raise RuntimeError(f"Can't find {tool}!")

# TODO: Divide into read-only data and writable/executable text.

class ObjectParser:

    _ARGS = [
        # "--demangle",
        "--elf-output-style=JSON",
        "--expand-relocs",
        "--pretty-print",
        "--section-data",
        "--section-relocations",
        "--section-symbols",
        "--sections",
    ]

    def __init__(self, path: pathlib.Path, reader: str, symbol_prefix: str = "") -> None:
        self.path = path
        self.body = bytearray()
        self.body_symbols = {}
        self.body_offsets = {}
        self.relocations = {}
        self.dupes = set()
        self.got_entries = []
        self.relocations_todo = []
        self.symbol_prefix = symbol_prefix
        self.reader = reader

    async def parse(self):
        # subprocess.run([find_llvm_tool("llvm-objdump")[0], self.path, "-dr"], check=True)  # XXX
        process = await asyncio.create_subprocess_exec(self.reader, *self._ARGS, self.path, stdout=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        assert stderr is None, stderr
        if process.returncode:
            raise RuntimeError(f"{self.reader} exited with {process.returncode}")
        output = stdout
        output = output.replace(b"PrivateExtern\n", b"\n")  # XXX: MachO
        output = output.replace(b"Extern\n", b"\n")  # XXX: MachO
        start = output.index(b"[", 1)  # XXX: MachO, COFF
        end = output.rindex(b"]", 0, -1) + 1  # XXXL MachO, COFF
        self._data = json.loads(output[start:end])
        for section in unwrap(self._data, "Section"):
            self._handle_section(section)
        # if "_justin_entry" in self.body_symbols:
        #     entry = self.body_symbols["_justin_entry"]
        # else:
        #     entry = self.body_symbols["_justin_trampoline"]
        entry = 0  # XXX
        holes = []
        for newhole in handle_relocations(self.got_entries, self.body, self.relocations_todo):
            assert newhole.symbol not in self.dupes
            if newhole.symbol in self.body_symbols:
                addend = newhole.addend + self.body_symbols[newhole.symbol] - entry
                newhole = Hole(newhole.kind, "_justin_base", newhole.offset, addend)
            holes.append(newhole)
        got = len(self.body)
        for i, got_symbol in enumerate(self.got_entries):
            if got_symbol in self.body_symbols:
                holes.append(Hole("PATCH_ABS_64", "_justin_base", got + 8 * i, self.body_symbols[got_symbol]))
                continue
            # XXX: PATCH_ABS_32 on 32-bit platforms?
            holes.append(Hole("PATCH_ABS_64", got_symbol, got + 8 * i, 0))
        self.body.extend([0] * 8 * len(self.got_entries))
        holes.sort(key=lambda hole: hole.offset)
        return Stencil(bytes(self.body)[entry:], tuple(holes))  # XXX

@dataclasses.dataclass(frozen=True)
class Hole:
    kind: str  # XXX: Enum
    symbol: str
    offset: int
    addend: int

@dataclasses.dataclass(frozen=True)
class Stencil:
    body: bytes
    holes: tuple[Hole, ...]
    # entry: int

def sign_extend_64(value: int, bits: int) -> int:
    """Sign-extend a value to 64 bits."""
    assert 0 <= value < (1 << bits) < (1 << 64)
    return value - ((value & (1 << (bits - 1))) << 1)

def handle_relocations(
    got_entries: list[str],
    body: bytearray,
    relocations: typing.Sequence[tuple[int, typing.Mapping[str, typing.Any]]],
) -> typing.Generator[Hole, None, None]:
    for i, (base, relocation) in enumerate(relocations):
        match relocation:
    ##############################################################################
            case {
                "Length": 2 as length,
                "Offset": int(offset),
                "PCRel": 1 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_BRANCH26"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                # XXX: This nonsense...
                assert what & 0xFC000000 == 0x14000000 or what & 0xFC000000 == 0x94000000, what
                addend = (what & 0x03FFFFFF) << 2
                addend = sign_extend_64(addend, 28)
                assert symbol.startswith("_"), symbol
                symbol = symbol.removeprefix("_")
                yield Hole("PATCH_REL_26", symbol, offset, addend)
            case {
                "Length": 2 as length,
                "Offset": int(offset),
                "PCRel": 1 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_GOT_LOAD_PAGE21"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                # XXX: This nonsense...
                assert what & 0x9F000000 == 0x90000000, what
                addend = ((what & 0x60000000) >> 29) | ((what & 0x01FFFFE0) >> 3) << 12
                addend = sign_extend_64(addend, 33)
                # assert symbol.startswith("_"), symbol
                symbol = symbol.removeprefix("_")
                if symbol not in got_entries:
                    got_entries.append(symbol)
                addend += len(body) + got_entries.index(symbol) * 8
                yield Hole("PATCH_REL_21", "_justin_base", offset, addend)
            case {
                "Length": 2 as length,
                "Offset": int(offset),
                "PCRel": 0 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_GOT_LOAD_PAGEOFF12"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                # XXX: This nonsense...
                assert what & 0x3B000000 == 0x39000000, what
                addend = (what & 0x003FFC00) >> 10
                implicit_shift = 0
                if what & 0x3B000000 == 0x39000000:
                    implicit_shift = (what >> 30) & 0x3
                    if implicit_shift == 0:
                        if what & 0x04800000 == 0x04800000:
                            implicit_shift = 4
                addend <<= implicit_shift
                # assert symbol.startswith("_"), symbol
                symbol = symbol.removeprefix("_")
                if symbol not in got_entries:
                    got_entries.append(symbol)
                addend += len(body) + got_entries.index(symbol) * 8
                yield Hole("PATCH_ABS_12", "_justin_base", offset, addend)
            case {
                "Length": 2 as length,
                "Offset": int(offset),
                "PCRel": 1 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_PAGE21"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                # XXX: This nonsense...
                assert what & 0x9F000000 == 0x90000000, what
                addend = ((what & 0x60000000) >> 29) | ((what & 0x01FFFFE0) >> 3) << 12
                addend = sign_extend_64(addend, 33)
                # assert symbol.startswith("_"), symbol
                symbol = symbol.removeprefix("_")
                yield Hole("PATCH_REL_21", symbol, offset, addend)
            case {
                "Length": 2 as length,
                "Offset": int(offset),
                "PCRel": 0 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_PAGEOFF12"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                # XXX: This nonsense...
                assert what & 0x3B000000 == 0x39000000 or what & 0x11C00000 == 0x11000000, what
                addend = (what & 0x003FFC00) >> 10
                implicit_shift = 0
                if what & 0x3B000000 == 0x39000000:
                    implicit_shift = (what >> 30) & 0x3
                    if implicit_shift == 0:
                        if what & 0x04800000 == 0x04800000:
                            implicit_shift = 4
                addend <<= implicit_shift
                # assert symbol.startswith("_"), symbol
                symbol = symbol.removeprefix("_")
                yield Hole("PATCH_ABS_12", symbol, offset, addend)
            case {
                "Length": 3 as length,
                "Offset": int(offset),
                "PCRel": 0 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_SUBTRACTOR"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=True)
                addend = what
                print(f"ARM64_RELOC_SUBTRACTOR: {offset:#x} {what:#x} {addend:#x} {symbol}")
                # XXX: Need to pair with UNSIGNED...
            case {
                "Length": 3 as length,
                "Offset": int(offset),
                "PCRel": 0 as pcrel,
                "Section": {"Value": str(section)},
                "Type": {"Value": "ARM64_RELOC_UNSIGNED"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                addend = what
                assert section.startswith("_"), section
                section = section.removeprefix("_")
                yield Hole("PATCH_ABS_64", section, offset, addend)
            case {
                "Length": 3 as length,
                "Offset": int(offset),
                "PCRel": 0 as pcrel,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "ARM64_RELOC_UNSIGNED"},
            }:
                offset += base
                where = slice(offset, offset + (1 << length))
                what = int.from_bytes(body[where], "little", signed=False)
                addend = what
                assert symbol.startswith("_"), symbol
                symbol = symbol.removeprefix("_")
                yield Hole("PATCH_ABS_64", symbol, offset, addend)
    ##############################################################################
            case {
                "Offset": int(offset),
                "Symbol": str(symbol),
                "Type": {"Value": "IMAGE_REL_AMD64_ADDR64"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                # assert not what, what
                addend = what
                body[where] = [0] * 8
                yield Hole("PATCH_ABS_64", symbol, offset, addend)
            case {
                "Offset": int(offset),
                "Symbol": str(symbol),
                "Type": {"Value": "IMAGE_REL_I386_DIR32"},
            }:
                offset += base
                where = slice(offset, offset + 4)
                what = int.from_bytes(body[where], sys.byteorder)
                # assert not what, what
                addend = what
                body[where] = [0] * 4
                # assert symbol.startswith("_")
                symbol = symbol.removeprefix("_")
                yield Hole("PATCH_ABS_32", symbol, offset, addend)
            case {
                "Addend": int(addend),
                "Offset": int(offset),
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "R_X86_64_64"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                assert not what, what
                yield Hole("PATCH_ABS_64", symbol, offset, addend)
            case {
                "Addend": int(addend),
                "Offset": int(offset),
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "R_X86_64_GOT64"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                assert not what, what
                if symbol not in got_entries:
                    got_entries.append(symbol)
                addend += got_entries.index(symbol) * 8
                body[where] = addend.to_bytes(8, sys.byteorder)
            case {
                "Addend": int(addend),
                "Offset": int(offset),
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "R_X86_64_GOTOFF64"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                assert not what, what
                addend += offset - len(body)
                yield Hole("PATCH_REL_64", symbol, offset, addend)
            case {
                "Addend": int(addend),
                "Offset": int(offset),
                "Symbol": {"Value": "_GLOBAL_OFFSET_TABLE_"},
                "Type": {"Value": "R_X86_64_GOTPC64"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                assert not what, what
                addend += len(body) - offset
                body[where] = addend.to_bytes(8, sys.byteorder)
            case {
                "Addend": int(addend),
                "Offset": int(offset),
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "R_X86_64_PC32"},
            }:
                offset += base
                where = slice(offset, offset + 4)
                what = int.from_bytes(body[where], sys.byteorder)
                assert not what, what
                yield Hole("PATCH_REL_32", symbol, offset, addend)
            case {
                "Length": 3,
                "Offset": int(offset),
                "PCRel": 0,
                "Section": {"Value": str(section)},
                "Type": {"Value": "X86_64_RELOC_UNSIGNED"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                # assert not what, what
                addend = what
                body[where] = [0] * 8
                assert section.startswith("_")
                section = section.removeprefix("_")
                yield Hole("PATCH_ABS_64", section, offset, addend)
            case {
                "Length": 3,
                "Offset": int(offset),
                "PCRel": 0,
                "Symbol": {"Value": str(symbol)},
                "Type": {"Value": "X86_64_RELOC_UNSIGNED"},
            }:
                offset += base
                where = slice(offset, offset + 8)
                what = int.from_bytes(body[where], sys.byteorder)
                # assert not what, what
                addend = what
                body[where] = [0] * 8
                assert symbol.startswith("_")
                symbol = symbol.removeprefix("_")
                yield Hole("PATCH_ABS_64", symbol, offset, addend)
            case _:
                raise NotImplementedError(relocation)


class ObjectParserCOFF(ObjectParser):

    def _handle_section(self, section: COFFSection) -> None:
        flags = {flag["Name"] for flag in section["Characteristics"]["Flags"]}
        if "SectionData" not in section:
            return
        if flags & {"IMAGE_SCN_LINK_COMDAT", "IMAGE_SCN_MEM_EXECUTE", "IMAGE_SCN_MEM_READ", "IMAGE_SCN_MEM_WRITE"} == {"IMAGE_SCN_LINK_COMDAT", "IMAGE_SCN_MEM_READ"}:
            # XXX: Merge these
            before = self.body_offsets[section["Number"]] = len(self.body)
            section_data = section["SectionData"]
            self.body.extend(section_data["Bytes"])
        elif flags & {"IMAGE_SCN_MEM_READ"} == {"IMAGE_SCN_MEM_READ"}:
            before = self.body_offsets[section["Number"]] = len(self.body)
            section_data = section["SectionData"]
            self.body.extend(section_data["Bytes"])
        else:
            return
        for symbol in unwrap(section["Symbols"], "Symbol"):
            offset = before + symbol["Value"]
            name = symbol["Name"]
            # assert name.startswith("_")  # XXX
            name = name.removeprefix(self.symbol_prefix)  # XXX
            if name in self.body_symbols:
                self.dupes.add(name)
            self.body_symbols[name] = offset
        for relocation in unwrap(section["Relocations"], "Relocation"):
            self.relocations_todo.append((before, relocation))

class ObjectParserMachO(ObjectParser):

    def _handle_section(self, section: MachOSection) -> None:
        assert section["Address"] >= len(self.body)
        self.body.extend([0] * (section["Address"] - len(self.body)))
        before = self.body_offsets[section["Index"]] = section["Address"]
        section_data = section["SectionData"]
        self.body.extend(section_data["Bytes"])
        name = section["Name"]["Value"]
        # assert name.startswith("_")  # XXX
        name = name.removeprefix(self.symbol_prefix)  # XXX
        if name in self.body_symbols:
            self.dupes.add(name)
        self.body_symbols[name] = 0  # before
        for symbol in unwrap(section["Symbols"], "Symbol"):
            offset = symbol["Value"]
            name = symbol["Name"]["Value"]
            # assert name.startswith("_")  # XXX
            name = name.removeprefix(self.symbol_prefix)  # XXX
            if name in self.body_symbols:
                self.dupes.add(name)
            self.body_symbols[name] = offset
        for relocation in unwrap(section["Relocations"], "Relocation"):
            self.relocations_todo.append((before, relocation))


class ObjectParserELF(ObjectParser):

    def _handle_section(self, section: ELFSection) -> None:
        type = section["Type"]["Value"]
        flags = {flag["Name"] for flag in section["Flags"]["Flags"]}
        if type == "SHT_RELA":
            assert "SHF_INFO_LINK" in flags, flags
            before = self.body_offsets[section["Info"]]
            assert not section["Symbols"]
            for relocation in unwrap(section["Relocations"], "Relocation"):
                self.relocations_todo.append((before, relocation))
        elif type == "SHT_PROGBITS":
            before = self.body_offsets[section["Index"]] = len(self.body)
            if "SHF_ALLOC" not in flags:
                return
            elif flags & {"SHF_EXECINSTR", "SHF_MERGE", "SHF_WRITE"} == {"SHF_MERGE"}:
                # XXX: Merge these
                section_data = section["SectionData"]
                self.body.extend(section_data["Bytes"])
            else:
                section_data = section["SectionData"]
                self.body.extend(section_data["Bytes"])
            assert not section["Relocations"]
            for symbol in unwrap(section["Symbols"], "Symbol"):
                offset = before + symbol["Value"]
                name = symbol["Name"]["Value"]
                # assert name.startswith("_")  # XXX
                name = name.removeprefix(self.symbol_prefix)  # XXX
                assert name not in self.body_symbols
                self.body_symbols[name] = offset
        else:
            assert type in {"SHT_LLVM_ADDRSIG", "SHT_NULL", "SHT_STRTAB", "SHT_SYMTAB"}, type


CFLAGS = [
    # "-DNDEBUG",  # XXX
    "-DPy_BUILD_CORE",
    "-D_PyJIT_ACTIVE",
    "-I.",
    "-I./Include",
    "-I./Include/internal",
    "-I./PC",
    "-O3",
    "-Wno-unreachable-code",
    "-Wno-unused-but-set-variable",
    "-Wno-unused-command-line-argument",
    "-Wno-unused-label",
    "-Wno-unused-variable",
    # We don't need this (and it causes weird relocations):
    "-fno-asynchronous-unwind-tables",  # XXX
    # # Don't need the overhead of position-independent code, if posssible:
    # "-fno-pic",
    # Disable stack-smashing canaries, which use magic symbols:
    "-fno-stack-protector",  # XXX
    # The GHC calling convention uses %rbp as an argument-passing register:
    "-fomit-frame-pointer",  # XXX
    # Disable debug info:
    "-g0",  # XXX
    # Need this to leave room for patching our 64-bit pointers:
    "-mcmodel=large",  # XXX
]

if sys.platform == "darwin":
    ObjectParserDefault = functools.partial(ObjectParserMachO, symbol_prefix="_")  # XXX
elif sys.platform == "linux":
    ObjectParserDefault = ObjectParserELF
elif sys.platform == "win32":
    assert sys.argv[1] == "--windows", sys.argv[1]
    if sys.argv[2] == "Debug|Win32":
        ObjectParserDefault = functools.partial(ObjectParserCOFF, symbol_prefix="_")  # XXX
        CFLAGS += ["-D_DEBUG", "-m32"]
    elif sys.argv[2] == "Debug|x64":
        ObjectParserDefault = ObjectParserCOFF
        CFLAGS += ["-D_DEBUG"]
    elif sys.argv[2] in {"PGInstrument|Win32", "PGUpdate|Win32", "Release|Win32"}:
        ObjectParserDefault = functools.partial(ObjectParserCOFF, symbol_prefix="_")  # XXX
        # CFLAGS += ["-DNDEBUG", "-m32"]  # XXX
        CFLAGS += ["-m32"]
    elif sys.argv[2] in {"PGInstrument|x64", "PGUpdate|x64", "Release|x64"}:
        ObjectParserDefault = ObjectParserCOFF
        # CFLAGS += ["-DNDEBUG"]  # XXX
        pass
    else:
        assert False, sys.argv[2]
    sys.argv[1:] = sys.argv[3:]
else:
    raise NotImplementedError(sys.platform)

class Compiler:
    _SKIP = frozenset(
        {
            "CALL_BOUND_METHOD_EXACT_ARGS",
            "CALL_FUNCTION_EX",
            "CHECK_EG_MATCH",
            "CHECK_EXC_MATCH",
            "CLEANUP_THROW",
            "DELETE_DEREF",
            "DELETE_FAST",
            "DELETE_GLOBAL",
            "DELETE_NAME",
            "DICT_MERGE",
            "END_ASYNC_FOR",
            "EXTENDED_ARG",  # XXX: Only because we don't handle extended args correctly...
            "FOR_ITER",
            "FORMAT_VALUE",
            "GET_AWAITABLE",
            "IMPORT_FROM",
            "IMPORT_NAME",
            "INSTRUMENTED_CALL", # XXX
            "INSTRUMENTED_CALL_FUNCTION_EX", # XXX
            "INSTRUMENTED_END_FOR", # XXX
            "INSTRUMENTED_END_SEND", # XXX
            "INSTRUMENTED_FOR_ITER", # XXX
            "INSTRUMENTED_INSTRUCTION", # XXX
            "INSTRUMENTED_JUMP_BACKWARD", # XXX
            "INSTRUMENTED_JUMP_FORWARD", # XXX
            "INSTRUMENTED_LINE", # XXX
            "INSTRUMENTED_LOAD_SUPER_ATTR", # XXX
            "INSTRUMENTED_POP_JUMP_IF_FALSE", # XXX
            "INSTRUMENTED_POP_JUMP_IF_NONE", # XXX
            "INSTRUMENTED_POP_JUMP_IF_NOT_NONE", # XXX
            "INSTRUMENTED_POP_JUMP_IF_TRUE", # XXX
            "INSTRUMENTED_RESUME", # XXX
            "INSTRUMENTED_RETURN_CONST", # XXX
            "INSTRUMENTED_RETURN_VALUE", # XXX
            "INSTRUMENTED_YIELD_VALUE", # XXX
            "INTERPRETER_EXIT", # XXX
            "JUMP_BACKWARD",  # XXX: Is this a problem?
            "JUMP_BACKWARD_INTO_TRACE",
            "JUMP_BACKWARD_NO_INTERRUPT",
            "KW_NAMES",  # XXX: Only because we don't handle kwnames correctly...
            "LOAD_CLASSDEREF",
            "LOAD_CLOSURE",
            "LOAD_DEREF",
            "LOAD_FAST_CHECK",
            "LOAD_FROM_DICT_OR_DEREF",
            "LOAD_FROM_DICT_OR_GLOBALS",
            "LOAD_GLOBAL",
            "LOAD_NAME",
            "MAKE_CELL",
            "MATCH_CLASS",
            "MATCH_KEYS",
            "RAISE_VARARGS",
            "RERAISE",
            "SEND",
            "STORE_ATTR_WITH_HINT",
            "UNPACK_EX",
            "UNPACK_SEQUENCE",
            "CALL_NO_KW_METHOD_DESCRIPTOR_NOARGS",  # XXX: M2 Mac...
            "CALL_NO_KW_METHOD_DESCRIPTOR_O",  # XXX: M2 Mac...
            "CALL_PY_EXACT_ARGS",  # XXX: M2 Mac...
            "BINARY_SUBSCR_GETITEM",  # XXX: M2 Mac...
            "CALL_NO_KW_BUILTIN_O",  # XXX: M2 Mac...
            "CALL_PY_WITH_DEFAULTS",  # XXX: M2 Mac...
            "LOAD_ATTR_PROPERTY",  # XXX: M2 Mac...
            "GET_ANEXT",  # XXX: M2 Mac...
            "IS_OP",  # XXX: M2 Mac...
            "LOAD_ATTR",  # XXX: M2 Mac...
            "LOAD_ATTR_WITH_HINT",  # XXX: M2 Mac...
            "BINARY_OP_SUBTRACT_FLOAT",  # XXX: M2 Mac...
            "BINARY_OP_MULTIPLY_FLOAT",  # XXX: M2 Mac...
            "BINARY_OP_ADD_FLOAT",  # XXX: M2 Mac...
        }
    )

    def __init__(self, *, verbose: bool = False) -> None:
        self._stencils_built = {}
        self._verbose = verbose
        self._clang, clang_version = find_llvm_tool("clang")
        self._readobj, readobj_version = find_llvm_tool("llvm-readobj")
        self._stderr(f"Using {self._clang} ({clang_version}) and {self._readobj} ({readobj_version}).")

    def _stderr(self, *args, **kwargs) -> None:
        if self._verbose:
            print(*args, **kwargs, file=sys.stderr)

    @staticmethod
    def _use_ghccc(ll: pathlib.Path, enable: bool = False) -> None:
        if enable:
            ir = ll.read_text()
            ir = ir.replace("i32 @_justin_continue", "ghccc i32 @_justin_continue")
            ir = ir.replace("i32 @_justin_entry", "ghccc i32 @_justin_entry")
            ll.write_text(ir)

    @staticmethod
    def _use_tos_caching(c: pathlib.Path, enable: int = 0) -> None:
        sc = c.read_text()
        for i in range(1, enable + 1):
            sc = sc.replace(f" = stack_pointer[-{i}];", f" = _tos{i};")
        for i in range(enable + 1, 5):
            sc = "".join(
                line for line in sc.splitlines(True) if f"_tos{i}" not in line
            )
        c.write_text(sc)

    async def _compile(self, opname, body) -> None:
        defines = [f"-D_JUSTIN_OPCODE={opname}"]
        with tempfile.TemporaryDirectory() as tempdir:
            c = pathlib.Path(tempdir, f"{opname}.c")
            ll = pathlib.Path(tempdir, f"{opname}.ll")
            o = pathlib.Path(tempdir, f"{opname}.o")
            c.write_text(body)
            self._use_tos_caching(c, 0)
            self._stderr(f"Compiling {opname}...")
            process = await asyncio.create_subprocess_exec(self._clang, *CFLAGS, "-emit-llvm", "-S", *defines, "-o", ll, c)
            stdout, stderr = await process.communicate()
            assert stdout is None, stdout
            assert stderr is None, stderr
            if process.returncode:
                raise RuntimeError(f"{self._clang} exited with {process.returncode}")
            # self._use_ghccc(ll, True)  # XXX: M2 Mac... (LLVM 14)
            self._stderr(f"Recompiling {opname}...")
            process = await asyncio.create_subprocess_exec(self._clang, *CFLAGS, "-c", "-o", o, ll)
            stdout, stderr = await process.communicate()
            assert stdout is None, stdout
            assert stderr is None, stderr
            if process.returncode:
                raise RuntimeError(f"{self._clang} exited with {process.returncode}")
            self._stderr(f"Parsing {opname}...")
            self._stencils_built[opname] = await ObjectParserDefault(o, self._readobj).parse()
        self._stderr(f"Built {opname}!")

    async def build(self) -> None:
        generated_cases = PYTHON_GENERATED_CASES_C_H.read_text()
        pattern = r"(?s:\n( {8}TARGET\((\w+)\) \{\n.*?\n {8}\})\n)"
        self._cases = {}
        for body, opname in re.findall(pattern, generated_cases):
            self._cases[opname] = body.replace(" " * 8, " " * 4)
        template = TOOLS_JUSTIN_TEMPLATE.read_text()
        tasks = []
        for opname in sorted(self._cases.keys() - self._SKIP):
            body = template % self._cases[opname]
            tasks.append(self._compile(opname, body))
        opname = "trampoline"
        body = TOOLS_JUSTIN_TRAMPOLINE.read_text()
        tasks.append(self._compile(opname, body))
        await asyncio.gather(*tasks)

    def dump(self) -> str:
        lines = []
        # XXX: Rework these to use Enums:
        kinds = {
            "PATCH_ABS_12",
            "PATCH_ABS_32",
            "PATCH_ABS_64",
            "PATCH_REL_21",
            "PATCH_REL_26",
            "PATCH_REL_32",
            "PATCH_REL_64",
        }
        values = {
            "HOLE_base",
            "HOLE_continue",
            "HOLE_next_instr",
            "HOLE_next_trace",
            "HOLE_oparg_plus_one",
        }
        opnames = []
        for opname, stencil in sorted(self._stencils_built.items()):
            opnames.append(opname)
            lines.append(f"// {opname}")
            assert stencil.body
            lines.append(f"static unsigned char {opname}_stencil_bytes[] = {{")
            for chunk in batched(stencil.body, 8):
                lines.append(f"    {', '.join(f'0x{byte:02X}' for byte in chunk)},")
            lines.append(f"}};")
            holes = []
            loads = []
            for hole in stencil.holes:
                assert hole.kind in kinds, hole.kind
                if hole.symbol.startswith("_justin_"):
                    value = f"HOLE_{hole.symbol.removeprefix('_justin_')}"
                    assert value in values, value
                    holes.append(f"    {{.kind = {hole.kind}, .offset = {hole.offset:4}, .addend = {hole.addend % (1 << 64):4}, .value = {value}}},")
                else:
                    loads.append(f"    {{.kind = {hole.kind}, .offset = {hole.offset:4}, .addend = {hole.addend % (1 << 64):4}, .symbol = \"{hole.symbol}\"}},")
            assert holes, stencil.holes
            lines.append(f"static const Hole {opname}_stencil_holes[] = {{")
            for hole in holes:
                lines.append(hole)
            lines.append(f"}};")
            lines.append(f"static const SymbolLoad {opname}_stencil_loads[] = {{")
            for  load in loads:
                lines.append(load)
            lines.append(f"    {{.kind =            0, .offset =    0, .addend =    0, .symbol = NULL}},")
            lines.append(f"}};")
            lines.append(f"")
        lines.append(f"#define INIT_STENCIL(OP) {{                             \\")
        lines.append(f"    .nbytes = Py_ARRAY_LENGTH(OP##_stencil_bytes),     \\")
        lines.append(f"    .bytes = OP##_stencil_bytes,                       \\")
        lines.append(f"    .nholes = Py_ARRAY_LENGTH(OP##_stencil_holes),     \\")
        lines.append(f"    .holes = OP##_stencil_holes,                       \\")
        lines.append(f"    .nloads = Py_ARRAY_LENGTH(OP##_stencil_loads) - 1, \\")
        lines.append(f"    .loads = OP##_stencil_loads,                       \\")
        lines.append(f"}}")
        lines.append(f"")
        lines.append(f"static const Stencil trampoline_stencil = INIT_STENCIL(trampoline);")
        lines.append(f"")
        lines.append(f"static const Stencil stencils[256] = {{")
        assert opnames[-1] == "trampoline"
        for opname in opnames[:-1]:
            lines.append(f"    [{opname}] = INIT_STENCIL({opname}),")
        lines.append(f"}};")
        lines.append(f"")
        lines.append(f"#define INIT_HOLE(NAME) [HOLE_##NAME] = (uintptr_t)0xBAD0BAD0BAD0BAD0")
        lines.append(f"")
        lines.append(f"#define GET_PATCHES() {{ \\")
        for value in sorted(values):
            if value.startswith("HOLE_"):
                name = value.removeprefix("HOLE_")
                lines.append(f"    INIT_HOLE({name}), \\")
        lines.append(f"}}")
        header = []
        header.append(f"// Don't be scared... this entire file is generated by Justin!")
        header.append(f"")
        header.append(f"typedef enum {{")
        for kind in sorted(kinds):
            header.append(f"    {kind},")
        header.append(f"}} HoleKind;")
        header.append(f"")
        header.append(f"typedef enum {{")
        for value in sorted(values):
            header.append(f"    {value},")
        header.append(f"}} HoleValue;")
        header.append(f"")
        header.append(f"typedef struct {{")
        header.append(f"    const HoleKind kind;")
        header.append(f"    const uintptr_t offset;")
        header.append(f"    const uintptr_t addend;")
        header.append(f"    const HoleValue value;")
        header.append(f"}} Hole;")
        header.append(f"")
        header.append(f"typedef struct {{")
        header.append(f"    const HoleKind kind;")
        header.append(f"    const uintptr_t offset;")
        header.append(f"    const uintptr_t addend;")
        header.append(f"    const char * const symbol;")
        header.append(f"}} SymbolLoad;")
        header.append(f"")
        header.append(f"typedef struct {{")
        header.append(f"    const size_t nbytes;")
        header.append(f"    unsigned char * const bytes;")
        header.append(f"    const size_t nholes;")
        header.append(f"    const Hole * const holes;")
        header.append(f"    size_t nloads;")
        header.append(f"    const SymbolLoad * const loads;")
        header.append(f"}} Stencil;")
        header.append(f"")
        lines[:0] = header
        lines.append("")
        return "\n".join(lines)

if __name__ == "__main__":
    # First, create our JIT engine:
    engine = Compiler(verbose=True)
    # This performs all of the steps that normally happen at build time:
    # TODO: Actual arg parser...
    asyncio.run(engine.build())
    with open(sys.argv[2], "w") as file:
        file.write(engine.dump())