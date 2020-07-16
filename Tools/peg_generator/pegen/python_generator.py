import token
from typing import Any, Dict, Optional, IO, Text, Tuple

from pegen.grammar import (
    Cut,
    GrammarVisitor,
    NameLeaf,
    StringLeaf,
    Rhs,
    NamedItem,
    Lookahead,
    PositiveLookahead,
    NegativeLookahead,
    Opt,
    Repeat0,
    Repeat1,
    Gather,
    Group,
    Rule,
    Alt,
)
from pegen import grammar
from pegen.parser_generator import ParserGenerator

MODULE_PREFIX = """\
#!/usr/bin/env python3.8
# @generated by pegen from {filename}

import ast
import sys
import tokenize

from typing import Any, Optional

from pegen.parser import memoize, memoize_left_rec, logger, Parser

"""
MODULE_SUFFIX = """

if __name__ == '__main__':
    from pegen.parser import simple_parser_main
    simple_parser_main(GeneratedParser)
"""


class PythonCallMakerVisitor(GrammarVisitor):
    def __init__(self, parser_generator: ParserGenerator):
        self.gen = parser_generator
        self.cache: Dict[Any, Any] = {}

    def visit_NameLeaf(self, node: NameLeaf) -> Tuple[Optional[str], str]:
        name = node.value
        if name in ("NAME", "NUMBER", "STRING", "OP"):
            name = name.lower()
            return name, f"self.{name}()"
        if name in ("NEWLINE", "DEDENT", "INDENT", "ENDMARKER", "ASYNC", "AWAIT"):
            return name.lower(), f"self.expect({name!r})"
        return name, f"self.{name}()"

    def visit_StringLeaf(self, node: StringLeaf) -> Tuple[str, str]:
        return "literal", f"self.expect({node.value})"

    def visit_Rhs(self, node: Rhs) -> Tuple[Optional[str], str]:
        if node in self.cache:
            return self.cache[node]
        if len(node.alts) == 1 and len(node.alts[0].items) == 1:
            self.cache[node] = self.visit(node.alts[0].items[0])
        else:
            name = self.gen.name_node(node)
            self.cache[node] = name, f"self.{name}()"
        return self.cache[node]

    def visit_NamedItem(self, node: NamedItem) -> Tuple[Optional[str], str]:
        name, call = self.visit(node.item)
        if node.name:
            name = node.name
        return name, call

    def lookahead_call_helper(self, node: Lookahead) -> Tuple[str, str]:
        name, call = self.visit(node.node)
        head, tail = call.split("(", 1)
        assert tail[-1] == ")"
        tail = tail[:-1]
        return head, tail

    def visit_PositiveLookahead(self, node: PositiveLookahead) -> Tuple[None, str]:
        head, tail = self.lookahead_call_helper(node)
        return None, f"self.positive_lookahead({head}, {tail})"

    def visit_NegativeLookahead(self, node: NegativeLookahead) -> Tuple[None, str]:
        head, tail = self.lookahead_call_helper(node)
        return None, f"self.negative_lookahead({head}, {tail})"

    def visit_Opt(self, node: Opt) -> Tuple[str, str]:
        name, call = self.visit(node.node)
        # Note trailing comma (the call may already have one comma
        # at the end, for example when rules have both repeat0 and optional
        # markers, e.g: [rule*])
        if call.endswith(","):
            return "opt", call
        else:
            return "opt", f"{call},"

    def visit_Repeat0(self, node: Repeat0) -> Tuple[str, str]:
        if node in self.cache:
            return self.cache[node]
        name = self.gen.name_loop(node.node, False)
        self.cache[node] = name, f"self.{name}(),"  # Also a trailing comma!
        return self.cache[node]

    def visit_Repeat1(self, node: Repeat1) -> Tuple[str, str]:
        if node in self.cache:
            return self.cache[node]
        name = self.gen.name_loop(node.node, True)
        self.cache[node] = name, f"self.{name}()"  # But no trailing comma here!
        return self.cache[node]

    def visit_Gather(self, node: Gather) -> Tuple[str, str]:
        if node in self.cache:
            return self.cache[node]
        name = self.gen.name_gather(node)
        self.cache[node] = name, f"self.{name}()"  # No trailing comma here either!
        return self.cache[node]

    def visit_Group(self, node: Group) -> Tuple[Optional[str], str]:
        return self.visit(node.rhs)

    def visit_Cut(self, node: Cut) -> Tuple[str, str]:
        return "cut", "True"


class PythonParserGenerator(ParserGenerator, GrammarVisitor):
    def __init__(
        self,
        grammar: grammar.Grammar,
        file: Optional[IO[Text]],
        tokens: Dict[int, str] = token.tok_name,
    ):
        super().__init__(grammar, tokens, file)
        self.callmakervisitor = PythonCallMakerVisitor(self)

    def generate(self, filename: str) -> None:
        header = self.grammar.metas.get("header", MODULE_PREFIX)
        if header is not None:
            self.print(header.rstrip("\n").format(filename=filename))
        subheader = self.grammar.metas.get("subheader", "")
        if subheader:
            self.print(subheader.format(filename=filename))
        self.print("class GeneratedParser(Parser):")
        while self.todo:
            for rulename, rule in list(self.todo.items()):
                del self.todo[rulename]
                self.print()
                with self.indent():
                    self.visit(rule)
        trailer = self.grammar.metas.get("trailer", MODULE_SUFFIX)
        if trailer is not None:
            self.print(trailer.rstrip("\n"))

    def visit_Rule(self, node: Rule) -> None:
        is_loop = node.is_loop()
        is_gather = node.is_gather()
        rhs = node.flatten()
        if node.left_recursive:
            if node.leader:
                self.print("@memoize_left_rec")
            else:
                # Non-leader rules in a cycle are not memoized,
                # but they must still be logged.
                self.print("@logger")
        else:
            self.print("@memoize")
        node_type = node.type or "Any"
        self.print(f"def {node.name}(self) -> Optional[{node_type}]:")
        with self.indent():
            self.print(f"# {node.name}: {rhs}")
            if node.nullable:
                self.print(f"# nullable={node.nullable}")
            self.print("mark = self.mark()")
            if is_loop:
                self.print("children = []")
            self.visit(rhs, is_loop=is_loop, is_gather=is_gather)
            if is_loop:
                self.print("return children")
            else:
                self.print("return None")

    def visit_NamedItem(self, node: NamedItem) -> None:
        name, call = self.callmakervisitor.visit(node.item)
        if node.name:
            name = node.name
        if not name:
            self.print(call)
        else:
            if name != "cut":
                name = self.dedupe(name)
            self.print(f"({name} := {call})")

    def visit_Rhs(self, node: Rhs, is_loop: bool = False, is_gather: bool = False) -> None:
        if is_loop:
            assert len(node.alts) == 1
        for alt in node.alts:
            self.visit(alt, is_loop=is_loop, is_gather=is_gather)

    def visit_Alt(self, node: Alt, is_loop: bool, is_gather: bool) -> None:
        with self.local_variable_context():
            self.print("cut = False")  # TODO: Only if needed.
            if is_loop:
                self.print("while (")
            else:
                self.print("if (")
            with self.indent():
                first = True
                for item in node.items:
                    if first:
                        first = False
                    else:
                        self.print("and")
                    self.visit(item)
            self.print("):")
            with self.indent():
                action = node.action
                if not action:
                    if is_gather:
                        assert len(self.local_variable_names) == 2
                        action = (
                            f"[{self.local_variable_names[0]}] + {self.local_variable_names[1]}"
                        )
                    else:
                        action = f"[{', '.join(self.local_variable_names)}]"
                if is_loop:
                    self.print(f"children.append({action})")
                    self.print(f"mark = self.mark()")
                else:
                    self.print(f"return {action}")
            self.print("self.reset(mark)")
            # Skip remaining alternatives if a cut was reached.
            self.print("if cut: return None")  # TODO: Only if needed.
