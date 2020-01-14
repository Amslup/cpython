"""A generic class to build line-oriented command interpreters.

Interpreters constructed with this class obey the following conventions:

1. End of file on input is processed as the command 'EOF'.
2. A command is parsed out of each line by collecting the prefix composed
   of characters in the identchars member.
3. A command `foo' is dispatched to a method 'do_foo()'; the do_ method
   is passed a single argument consisting of the remainder of the line.
4. Typing an empty line repeats the last command.  (Actually, it calls the
   method `emptyline', which may be overridden in a subclass.)
5. There is a predefined `help' method.  Given an argument `topic', it
   calls the command `help_topic'.  With no arguments, it lists all topics
   with defined help_ functions, broken into up to three topics; documented
   commands, miscellaneous help topics, and undocumented commands.
6. The command '?' is a synonym for `help'.  The command '!' is a synonym
   for `shell', if a do_shell method exists.
7. If completion is enabled, completing commands will be done automatically,
   and completing of commands args is done by calling complete_foo() with
   arguments text, line, begidx, endidx.  text is string we are matching
   against, all returned matches must begin with it.  line is the current
   input line (lstripped), begidx and endidx are the beginning and end
   indexes of the text being matched, which could be used to provide
   different completion depending upon which position the argument is in.

The `default' method may be overridden to intercept commands for which there
is no do_ method.

The `completedefault' method may be overridden to intercept completions for
commands that have no complete_ method.

The data member `self.ruler' sets the character used to draw separator lines
in the help messages.  If empty, no ruler line is drawn.  It defaults to "=".

If the value of `self.intro' is nonempty when the cmdloop method is called,
it is printed out on interpreter startup.  This value may be overridden
via an optional argument to the cmdloop() method.

The data members `self.doc_header', `self.misc_header', and
`self.undoc_header' set the headers used for the help function's
listings of documented functions, miscellaneous topics, and undocumented
functions respectively.
"""

import string, sys

__all__ = ["Cmd"]

PROMPT = '(Cmd) '
IDENTCHARS = string.ascii_letters + string.digits + '_'

class Cmd:
    """A simple framework for writing line-oriented command interpreters.

    These are often useful for test harnesses, administrative tools, and
    prototypes that will later be wrapped in a more sophisticated interface.

    A Cmd instance or subclass instance is a line-oriented interpreter
    framework.  There is no good reason to instantiate Cmd itself; rather,
    it's useful as a superclass of an interpreter class you define yourself
    in order to inherit Cmd's methods and encapsulate action methods.

    """
    prompt = PROMPT
    identchars = IDENTCHARS
    ruler = '='
    lastcmd = ''
    intro = None
    doc_leader = ""
    doc_header = "Documented commands (type help <topic>):"
    misc_header = "Miscellaneous help topics:"
    undoc_header = "Undocumented commands:"
    nohelp = "*** No help on %s"
    use_rawinput = 1

    def __init__(self, completekey='tab', stdin=None, stdout=None):
        """Instantiate a line-oriented interpreter framework.

        The optional argument 'completekey' is the readline name of a
        completion key; it defaults to the Tab key. If completekey is
        not None and the readline module is available, command completion
        is done automatically. The optional arguments stdin and stdout
        specify alternate input and output file objects; if not specified,
        sys.stdin and sys.stdout are used.

        """
        self.stdin = stdin if stdin is not None else sys.stdin
        self.stdout = stdout if stdout is not None else sys.stdout
        self.cmdqueue = []
        self.completekey = completekey

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        self.try_setting_readline_as_completer()
        self.set_intro_and_print_it(intro)
        self.loop()
        self.postloop()
        self.restore_readline_completer()


    def try_setting_readline_as_completer(self):
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass

    def set_intro_and_print_it(self, intro):
        self.intro = intro
        if self.intro is not None:
            self.stdout.write(str(self.intro)+"\n")

    def loop(self):
        stop = False
        while not stop:
            line = self.get_line()
            try:
                line = self.precmd(line)
            except:
                pass
            stop = self.onecmd(line)
            try:
                stop = self.postcmd(stop, line)
            except:
                pass

    def get_line(self):
        if len(self.cmdqueue) > 0:
            return self.cmdqueue.pop(0)

        if self.use_rawinput:
            try:
                return input(self.prompt)
            except EOFError:
                return 'EOF'

        self.stdout.write(self.prompt)
        self.stdout.flush()
        line = self.stdin.readline()
        if not len(line):
            return 'EOF'
        return line.rstrip('\r\n')

    def restore_readline_completer(self):
        if self.use_rawinput and self.completekey:
            try:
                import readline
                readline.set_completer(self.old_completer)
            except ImportError:
                pass


    def precmd(self, line):
        """Hook method executed just before the command line is
        interpreted, but after the input prompt is generated and issued.

        """
        return line

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        return stop

    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        pass

    def postloop(self):
        """Hook method executed once when the cmdloop() method is about to
        return.

        """
        pass

    def parseline(self, line):
        """Parse the line into a command name and a string containing
        the arguments.  Returns a tuple containing (command, args, line).
        'command' and 'args' may be None if the line couldn't be parsed.
        """
        line = line.strip()

        if len(line) == 0 or self.is_shell_alias_without_shell(line):
            return None, None, line

        line = self.expand_alias(line, '?', 'help')
        line = self.expand_alias(line, '!', 'shell')

        cmd, arg = self.split_cmd_from_args(line)
        return cmd, arg, line

    def is_shell_alias_without_shell(self, line):
        return line[0] == '!' and not hasattr(self, 'do_shell')

    def expand_alias(self, line, alias, command):
        if line[0] == alias:
            return command + ' ' + line[1:]
        return line

    def split_cmd_from_args(self, line):
        for i in range(len(line)):
            if line[i] not in self.identchars:
                return line[:i], line[i:].strip()
        return line, ''

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if len(line) == 0:
            return self.emptyline()

        if self.tried_invoking_shell_without_implementation(cmd):
            return self.default(line)

        self.save_lastcmd(line)

        if cmd == '':
            return self.default(line)

        return self.try_invoking_command(cmd, arg, line)

    def emptyline(self):
        """Called when an empty line is entered in response to the prompt.

        If this method is not overridden, it repeats the last nonempty
        command entered.

        """
        if len(self.lastcmd) > 0:
            return self.onecmd(self.lastcmd)

    def default(self, line):
        """Called on an input line when the command prefix is not recognized.

        If this method is not overridden, it prints an error message and
        returns.

        """
        self.stdout.write('*** Unknown syntax: %s\n' % line)

    def tried_invoking_shell_without_implementation(self, cmd):
        return cmd is None

    def try_invoking_command(self, cmd, arg, line):
        try:
            func = getattr(self, 'do_' + cmd)
        except AttributeError:
            return self.default(line)
        return func(arg)

    def save_lastcmd(self, line):
        self.lastcmd = line if line != 'EOF' else ''

    def completedefault(self, *ignored):
        """Method called to complete an input line when no command-specific
        complete_*() method is available.

        By default, it returns an empty list.

        """
        return []

    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        return [a[3:] for a in self.get_names() if a.startswith(dotext)]

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        If a command has not been entered, then complete against command list.
        Otherwise try to call complete_<command> to get list of completions.
        """
        if state == 0:
            import readline
            origline = readline.get_line_buffer()
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = readline.get_begidx() - stripped
            endidx = readline.get_endidx() - stripped
            if begidx>0:
                cmd, args, foo = self.parseline(line)
                if cmd == '':
                    compfunc = self.completedefault
                else:
                    try:
                        compfunc = getattr(self, 'complete_' + cmd)
                    except AttributeError:
                        compfunc = self.completedefault
            else:
                compfunc = self.completenames
            self.completion_matches = compfunc(text, line, begidx, endidx)
        try:
            return self.completion_matches[state]
        except IndexError:
            return None

    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)

    def complete_help(self, *args):
        text = args[0]
        commands = set(self.completenames(text))
        topics = set(name[len('help_'):] for name in self.get_names()
                     if name.startswith('help_' + args[0]))
        return list(commands | topics)

    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd".'
        if len(arg) > 0:
            self.print_cmd_help(arg)
        else:
            self.print_general_help()

    def print_cmd_help(self, cmd):
        try:
            self.invoke_cmd_help_method(cmd)
        except AttributeError:
            try:
                self.print_cmd_function_docstring(cmd)
            except AttributeError:
                self.print_default_cmd_help(cmd)

    def invoke_cmd_help_method(self, cmd):
        func = getattr(self, 'help_' + cmd)
        func()

    def print_cmd_function_docstring(self, cmd):
        doc = getattr(self, 'do_' + cmd).__doc__
        if doc:
            self.stdout.write("%s\n"%str(doc))

    def print_default_cmd_help(self, cmd):
        self.stdout.write("%s\n"%str(self.nohelp % (cmd,)))

    def print_general_help(self):
        misc_topics, documented_commands, undocumented_commands = \
            self.split_by_documentation_type()
        self.stdout.write("%s\n"%str(self.doc_leader))
        self.print_topics(self.doc_header, documented_commands)
        self.print_topics(self.misc_header, misc_topics)
        self.print_topics(self.undoc_header, undocumented_commands)

    def split_by_documentation_type(self):
        misc_topics = self.get_misc_topics()
        documented_commands, undocumented_commands = \
            self.split_commands_by_documentation()
        return misc_topics, documented_commands, undocumented_commands

    def get_misc_topics(self):
        do_functions = set(self.get_do_functions())
        help_functions = set(self.get_do_functions())
        return help_functions - do_functions

    def split_commands_by_documentation(self):
        documented_commands = []
        undocumented_commands = []
        for function in self.get_do_functions():
            if self.has_documentation(function):
                documented_commands.append(function)
            else:
                undocumented_commands.append(function)
        return documented_commands, undocumented_commands

    def has_documentation(self, function):
        docstring = getattr(self, 'do_' + function).__doc__
        return function in self.get_help_functions() or docstring is not None

    def get_do_functions(self):
        return self.get_functions_with_prefix('do_')

    def has_help_function(self, function):
        return function in self.get_help_functions()

    def get_help_functions(self):
        return self.get_functions_with_prefix('help_')

    def get_functions_with_prefix(self, prefix):
        functions_with_prefix = []
        for name in set(self.get_names()):
            if name.startswith(prefix):
                name_without_prefix = name[len(prefix):]
                functions_with_prefix.append(name_without_prefix)
        functions_with_prefix.sort()
        return functions_with_prefix

    def print_topics(self, header, cmds, cmdlen=15, maxcol=80):
        if cmds:
            self.stdout.write("%s\n"%str(header))
            if self.ruler:
                self.stdout.write("%s\n"%str(self.ruler * len(header)))
            self.columnize(cmds, maxcol-1)
            self.stdout.write("\n")

    def columnize(self, list, displaywidth=80):
        """Display a list of strings as a compact set of columns.

        Each column is only as wide as necessary.
        Columns are separated by two spaces (one was not legible enough).
        """
        if not list:
            self.stdout.write("<empty>\n")
            return

        self.raise_if_list_contains_non_strings(list)

        row_num, col_num, col_widths = \
            self.calculate_min_row_and_col_num_and_col_widths(list, \
            displaywidth)
        self.print_rows(list, row_num, col_num, col_widths)

    def raise_if_list_contains_non_strings(self, list):
        non_strings = [index for index in range(len(list)) if not \
            isinstance(list[index], str)]
        if len(non_strings) > 0:
            raise TypeError("list[i] not a string for i in %s"
                            % ", ".join(map(str, non_strings)))

    def calculate_min_row_and_col_num_and_col_widths(self, list, displaywidth=80):
        for row_num in range(1, len(list)):
            col_num = self.get_col_num(len(list), row_num)
            col_widths = self.get_col_widths(list, row_num, col_num)
            if self.get_total_width(col_widths) <= displaywidth:
                return row_num, col_num, col_widths
        return len(list), 1, [0]

    def get_col_num(self, item_num, row_num):
        return (item_num + row_num - 1) // row_num

    def get_col_widths(self, list, row_num, col_num):
        col_widths = []
        for col in range(col_num):
            col_widths.append(self.min_col_width_for_all_rows(list, col, row_num))
        return col_widths

    def get_total_width(self, col_widths):
        content_width = sum(col_widths)
        separator_width = (len(col_widths) - 1) * len(self.column_seperatpr())
        return content_width + separator_width

    def min_col_width_for_all_rows(self, list, col, row_num):
        min_col_width = 0
        for row in range(row_num):
            item_index = self.get_item_index(row_num, row, col)
            if item_index >= len(list):
                break
            item = list[item_index]
            min_col_width = max(min_col_width, len(item))
        return min_col_width

    def print_rows(self, list, row_num, col_num, col_widths):
        for row_index in range(row_num):
            row = self.get_row(list, row_num, row_index, col_num)
            self.justify_row(row, col_widths)
            self.stdout.write("%s\n" % self.column_seperatpr().join(row))

    def get_row(self, list, row_num, row_index, col_num):
        row = []
        for col in range(col_num):
            item_index = self.get_item_index(row_num, row_index, col)
            if item_index >= len(list):
                return row
            row.append(list[item_index])
        return row

    def justify_row(self, row, col_widths):
        for col in range(len(row)):
            row[col] = row[col].ljust(col_widths[col])

    def get_item_index(self, row_num, row, col):
        return row + row_num * col

    def column_seperatpr(self):
        return '  '