
from lexer import Token
from typing import TextIO

class CWriter:
    'A writer that understands tokens and how to format C code'

    def __init__(self, out: TextIO, indent: int = 0):
        self.out = out
        self.initial_indent = self.indent = indent
        self.line = -1
        self.column = 0

    def set_position(self, tkn: Token):
        if self.line < tkn.line:
            self.column = 0
            self.out.write("\n")
        if self.column == 0:
            self.out.write("    " * self.indent)
        else:
            #Token colums are 1 based
            column = tkn.column - 1
            if self.column < column:
                self.out.write(" " * (column-self.column))
        self.line = tkn.end_line
        self.column = tkn.end_column - 1

    def maybe_dedent(self, txt: str):
        parens = txt.count("(") - txt.count(")")
        if parens < 0:
            self.indent += parens
        elif "}" in txt or txt.endswith(":"):
            self.indent -= 1

    def maybe_indent(self, txt: str):
        parens = txt.count("(") - txt.count(")")
        if parens > 0:
            self.indent += parens
        elif "{" in txt or txt.endswith(":"):
            self.indent += 1

    def emit_token(self, tkn: Token):
        self.maybe_dedent(tkn.text)
        self.set_position(tkn)
        self.emit_text(tkn.text)
        self.maybe_indent(tkn.text)

    def emit_text(self, txt: str):
        if self.column == 0:
            self.out.write("    " * self.indent)
            self.column = self.initial_indent * 4
        self.out.write(txt)

    def emit_str(self, txt: str):
        self.maybe_dedent(txt)
        self.emit_text(txt)
        if txt.endswith("\n"):
            self.column = 0
            self.line += 1
        elif txt.endswith("{") or txt.startswith("}"):
            if self.column:
                self.out.write("\n")
                self.column = 0
                self.line += 1
        else:
            self.column += len(txt)
        self.maybe_indent(txt)

    def emit(self, txt: str | Token):
        if isinstance(txt, Token):
            self.emit_token(txt)
        elif isinstance(txt, str):
            self.emit_str(txt)
        else:
            assert False

    def start_line(self):
        if self.column:
            self.out.write("\n")
            self.column = 0
