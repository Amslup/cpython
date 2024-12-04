import re
from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import make_id

def make_snippet(directive, options, content):
    group_name = options['group']

    # Docutils elements have a `rawsource` attribute that is supposed to be
    # set to the original ReST source.
    # Sphinx does the following with it:
    # - if it's empty, set it to `self.astext()`
    # - if it matches `self.astext()` when generating the output,
    #   apply syntax highlighting (which is based on the plain-text content
    #   and thus discards internal formatting, like references).
    # To get around this, we set it to this non-empty string:
    rawsource = 'You should not see this.'

    literal = nodes.literal_block(
        rawsource,
        '',
        # TODO: Use a dedicated CSS class here and for strings.
        # and add it to the theme too
        classes=['highlight'],
    )

    grammar_re = re.compile(
        """
            (?P<rule_name>^[a-zA-Z0-9_]+)     # identifier at start of line
            (?=:)                             # ... followed by a colon
        |
            [`](?P<rule_ref>[a-zA-Z0-9_]+)[`] # identifier in backquotes
        |
            (?P<single_quoted>'[^']*')        # string in 'quotes'
        |
            (?P<double_quoted>"[^"]*")        # string in "quotes"
        """,
        re.VERBOSE,
    )

    for line in content:
        last_pos = 0
        for match in grammar_re.finditer(line):
            # Handle text between matches
            if match.start() > last_pos:
                literal += nodes.Text(line[last_pos:match.start()])
            last_pos = match.end()

            # Handle matches
            groupdict = {
                name: content
                for name, content in match.groupdict().items()
                if content is not None
            }
            match groupdict:
                case {'rule_name': name}:
                    name_node = addnodes.literal_strong()

                    # Cargo-culted magic to make `name_node` a link target
                    # similar to Sphinx `production`.
                    # This needs to be the same as what Sphinx does
                    # to avoid breaking existing links.
                    domain = directive.env.domains['std']
                    obj_name = f"{group_name}:{name}"
                    prefix = f'grammar-token-{group_name}'
                    node_id = make_id(directive.env, directive.state.document, prefix, name)
                    name_node['ids'].append(node_id)
                    directive.state.document.note_implicit_target(name_node, name_node)
                    domain.note_object('token', obj_name, node_id, location=name_node)

                    text_node = nodes.Text(name)
                    name_node += text_node
                    literal += name_node
                case {'rule_ref': name}:
                    ref_node = addnodes.pending_xref(
                        name,
                        reftype="token",
                        refdomain="std",
                        reftarget=f"{group_name}:{name}",
                    )
                    ref_node += nodes.Text(name)
                    literal += ref_node
                case {'single_quoted': name} | {'double_quoted': name}:
                    string_node = nodes.inline(classes=['nb'])
                    string_node += nodes.Text(name)
                    literal += string_node
                case _:
                    raise ValueError('unhandled match')
        literal += nodes.Text(line[last_pos:] + '\n')

    node = nodes.paragraph(
        '', '',
        literal,
    )

    return [node]


class GrammarSnippetDirective(SphinxDirective):
    """Transform a grammar-snippet directive to a Sphinx productionlist

    That is, turn something like:

        .. grammar-snippet:: file
           :group: python-grammar

           file: (NEWLINE | statement)*

    into something similar to Sphinx productionlist, but better suited
    for our needs:
    - Instead of `::=`, use a colon, as in `Grammar/python.gram`
    - Show the listing almost as is, with no auto-aligment.
      The only special character is the backtick, which marks tokens.

    Unlike Sphinx's productionlist, this directive supports options.
    The "group" must be given as an option.
    """
    has_content = True
    option_spec = {
        'group': directives.unchanged,
    }

    # We currently ignore arguments.
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        return make_snippet(self, self.options, self.content)


class CompatProductionList(SphinxDirective):
    has_content = True
    option_spec = {}

    # We currently ignore arguments.
    required_arguments = 1

    def run(self):
        options = {'group': self.arguments[0]}
        content = self.content
        return make_snippet(self, options, content)


def setup(app):
    app.add_directive('grammar-snippet', GrammarSnippetDirective)
    app.add_directive('productionlist', CompatProductionList, override=True)
    return {'version': '1.0', 'parallel_read_safe': True}
