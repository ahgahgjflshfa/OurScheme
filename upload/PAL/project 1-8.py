import numpy as np


# Custom Errors
class NotFinishError(Exception):
    """讓parser等待多行輸入"""

    def __init__(self, msg_: str = "S expression not complete"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class EmptyInputError(Exception):
    """遇到註解或是整行空白用的"""

    def __init__(self, msg_: str = "Empty Input"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class OurSchemeError(Exception):
    def __init__(self, err_type_: str):
        self.err_type = err_type_
        super().__init__(f"ERROR ({err_type_})")


class NoClosingQuoteError(OurSchemeError):
    def __init__(self, line_: int, column_: int):
        self.line = line_
        self.column = column_
        super().__init__("no closing quote")


class UnexpectedTokenError(OurSchemeError):
    def __init__(self, type_, line, column, value):
        self.type = type_
        self.line = line
        self.column = column
        self.value = value
        super().__init__("unexpected token")


# lexer.py
class Token:
    def __init__(self, type_, value_, line_=0, start_pos_=0, end_pos_=0):
        """
        Initialize a Token object.

        Args:
            type_ (str): Type of the token (e.g., STRING, INT, SYMBOL).
            value_ (Any): Actual value of the token (e.g., "hello", 42).
            line_ (int): Line number where the token appears (1-based).
            start_pos_ (int): Starting character index of the token (1-based).
            end_pos_ (int): Ending character index of the token (inclusive).
        """
        # Note: String tokens do not include the surrounding double quotes
        self.type = type_
        self.value = value_
        self.line = line_
        self.start_pos = start_pos_  # Start index in the source string
        self.end_pos = end_pos_  # End index in the source string (inclusive)

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value

        return False


class Lexer:
    def __init__(self):
        self.source_code = ""  # Store 1 line of user input in repl.
        self._position = 0  # Store current location.
        self._line_number = 1
        self._column_number = 1

    @property
    def position(self) -> int:
        return self._position

    @property
    def line(self) -> int:
        return self._line_number

    @property
    def column(self) -> int:
        return self._column_number

    def reset(self, new_source_code: str):
        """
        Reset the lexer with new source code.

        Args:
            new_source_code (str): The new code to be tokenized.
        """
        self.source_code = new_source_code  # + "\n"
        self._position = 0
        self._line_number = 1
        self._column_number = 1

    def has_more_token(self) -> bool:
        """
        Check if there are more tokens left in the source code.

        Returns:
            bool: True if more tokens are available, False otherwise.
        """
        return self._position < len(self.source_code)

    def peek(self) -> str:
        """
        Peek the next character without advancing the position.

        Returns:
            str: The next character, or an empty string if at the end.
        """
        return self.source_code[self._position + 1] if self._position + 1 < len(self.source_code) else ""

    def peek_token(self) -> Token:
        """
        Peek the next token without consuming it.

        Returns:
            Token: The next token.
        """
        current_position = self._position
        token = self.next_token()
        self._position = current_position
        return token

    def set_position(self, pos: int):
        """
        Set the current scanning position of the lexer.

        Args:
            pos (int): The new position to set as the current index.
        """
        self._position = pos

    def next_token(self) -> Token:
        """
        Extract the next token from the source code.

        Returns:
            Token: The next token object.
        """
        self._skip_whitespace_and_comments()

        if self._position >= len(self.source_code):
            return Token("EOF", None)

        char = self.source_code[self._position]

        if char in "()":
            return self._read_paren()

        elif char == "\'":
            return self._read_quote()

        elif char.isalpha() or char in "!#$%&*,/:<=>?@[\\]^_`{|}~":
            return self._read_symbol()

        elif char == "\"":
            return self._read_string()

        elif char == ".":
            peek = self.peek()
            if peek and (peek.isalnum() or peek in "!#$%&*+,-./:<=>?@[\\]^_`{|}~"):
                return self._read_number_or_symbol()
            else:
                return self._read_dot()

        elif (char.isdigit() or
              (char in "+-" and (self.peek().isdigit() or self.peek() == "."))
        ):
            return self._read_number_or_symbol()

        elif char in "!#$%&*+,-./:<=>?@[\\]^_`{|}~":
            return self._read_symbol()

        else:
            self._column_number += 1
            pos = self._column_number - 1
            raise SyntaxError(f"Unknown character: {char} at line {self._line_number} column {pos}")

    def _skip_whitespace_and_comments(self):
        """
        Skip over any whitespace or comment characters.
        """
        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char == "\n":
                self._line_number += 1
                self._column_number = 1
                self._position += 1

            elif char.isspace():  # whitespace
                self._column_number += 1
                self._position += 1

            elif char == ";":  # comments
                while self._position < len(self.source_code) and self.source_code[self._position] != "\n":
                    self._position += 1

            else:
                break

    def _read_string(self) -> Token:
        """
        Read a string token and handle escape characters.

        Returns:
            Token: A STRING token or ERROR token if the string is not closed.
        """
        # Record starting position of string (starting quote not included)
        start_pos = self._column_number
        self._position += 1  # skip "
        self._column_number += 1
        result = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if self.source_code[self.position] == "\"":
                end_pos = self._column_number  # includes "
                self._position += 1
                self._column_number += 1

                return Token("STRING", result, self._line_number, start_pos, end_pos)

            if char == "\\":
                self._position += 1
                self._column_number += 1

                if self.position >= len(self.source_code):  # no closing quote until end of line
                    return Token("ERROR", "Unclosed string", self._line_number, self._column_number)

                if self.source_code[self._position] == "n":
                    result += "\n"
                elif self.source_code[self._position] == "t":
                    result += "\t"
                elif self.source_code[self._position] == "\"":
                    result += "\""
                elif self.source_code[self._position] == "\\":
                    result += "\\"
                else:
                    result += f"\\{self.source_code[self._position]}"

                self._position += 1
                self._column_number += 1
                continue

            result += char
            self._position += 1
            self._column_number += 1

        # no closing quote until end of line
        return Token("ERROR", "Unclosed string", self._line_number, self._column_number)

    def _read_number_or_symbol(self) -> Token:
        """
        Read a number or symbol token depending on its content.

        Returns:
            Token: Either a FLOAT, INT, or SYMBOL token.
        """
        start_pos = self._column_number
        number_str = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isalnum() or char in "!#$%&*+,-./:<=>?@[\\]^_`{|}~":
                number_str += char
                self._position += 1
                self._column_number += 1

            else:
                break

        end_pos = self._column_number - 1

        if "_" in number_str:
            return Token("SYMBOL", number_str, self._line_number, start_pos, end_pos)

        try:
            val = np.float64(number_str)
            if '.' in number_str or 'e' in number_str.lower():
                return Token("FLOAT", float(val), self._line_number, start_pos, end_pos)
            elif np.isclose(val, int(val)):
                return Token("INT", int(val), self._line_number, start_pos, end_pos)
            else:
                return Token("FLOAT", float(val), self._line_number, start_pos, end_pos)

        except ValueError:
            return Token("SYMBOL", number_str, self._line_number, start_pos, end_pos)

    def _read_symbol(self) -> Token:
        """
        Read a symbol token (e.g., variable or function names).

        Returns:
            Token: A SYMBOL, T, or NIL token.
        """
        start_pos = self._column_number
        symbol = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isalnum() or char in "!#$%&*+,-./:<=>?@[\\]^_`{|}~":
                symbol += char
                self._position += 1
                self._column_number += 1

            elif char == "\n":
                break

            else:
                break

        end_pos = self._column_number - 1

        if symbol == "t":
            return Token("T", "#t", self._line_number, start_pos, end_pos)
        elif symbol == "nil":
            return Token("NIL", "nil", self._line_number, start_pos, end_pos)
        elif symbol == "#t":
            return Token("T", "#t", self._line_number, start_pos, end_pos)
        elif symbol == "#f":
            return Token("NIL", "nil", self._line_number, start_pos, end_pos)

        return Token("SYMBOL", symbol, self._line_number, start_pos, end_pos)

    def _read_dot(self) -> Token:
        """
        Read a dot (.) token.

        Returns:
            Token: A DOT token.
        """
        dot_pos = self._column_number
        self._position += 1
        self._column_number += 1

        return Token("DOT", ".", self._line_number, dot_pos, dot_pos)

    def _read_quote(self) -> Token:
        """
        Read a quote token (').

        Returns:
            Token: A QUOTE token.
        """
        quote_pos = self._column_number
        self._position += 1
        self._column_number += 1

        return Token("QUOTE", "quote", self._line_number, quote_pos, quote_pos)

    def _read_paren(self) -> Token:
        """
        Read a parenthesis token.

        Returns:
            Token: Either a LEFT_PAREN or RIGHT_PAREN token.
        """
        char = self.source_code[self._position]
        paren_pos = self._column_number
        self._position += 1
        self._column_number += 1

        if char == "(":
            return Token("LEFT_PAREN", "(", self._line_number, paren_pos, paren_pos)
        else:
            return Token("RIGHT_PAREN", ")", self._line_number, paren_pos, paren_pos)


# AST Nodes
class ASTNode:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and vars(self) == vars(other)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class AtomNode(ASTNode):
    def __init__(self, type_, value):
        self.type = type_   # "INT", "FLOAT", "SYMBOL", "BOOLEAN"
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type}, {repr(self.value)})"


class ListNode(ASTNode):
    def __init__(self, elements=None):
        self.elements = elements if elements is not None else []

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.elements)})"


class ConsNode(ASTNode):
    def __init__(self, car: ASTNode, cdr: ASTNode = None):
        self.car = car
        self.cdr = cdr  # cdr 可以是 ASTNode 或 None

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.car)}, {repr(self.cdr)})"


class QuoteNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


# Parser.py
class Parser:
    def __init__(self, lexer: Lexer):
        """
        Initialize the Parser with a given lexer. This also performs an initial token fetch.

        Args:
            lexer (Lexer): The lexer instance used to tokenize the input source code.

        Raises:
            EmptyInputError: If the input is immediately EOF.
        """
        self.lexer = lexer

        # Records the starting column index of the current S-expression
        # (based on the list index of the source characters)
        self._current_s_exp_start_pos = 0

        # Records the end position (index) of the most recently consumed token
        # in the source code. Still based on list index of source characters.
        # So: source_code[last_token_end_pos] is still part of the previous token,
        # and the next character after that is the beginning of the new token.
        self._last_token_end_pos = 0

        self._current_token = self.lexer.next_token()

        if self._current_token.type == "EOF":
            raise EmptyInputError(f"EOF encountered")

    @staticmethod
    def _is_token_type(token: Token, *types: str) -> bool:
        """
        Check whether the token's type matches any of the specified types.

        Args:
            token (Token): The token to check.
            *types (str): A variable number of string type names to compare against.

        Returns:
            bool: True if token.type matches any of the provided types, False otherwise.
        """
        return token.type in types

    @staticmethod
    def _convert_to_cons(elements: list, cdr: ASTNode) -> ASTNode:
        """
        Convert a Python list of ASTNodes to nested ConsNode representation.

        Args:
            elements (list): A list of ASTNode instances to be converted into a nested ConsNode structure.
            cdr (ASTNode): The final cdr node to terminate the Cons chain.

        Returns:
            ASTNode: A nested ConsNode representing the list.
        """
        if not elements:
            return AtomNode("BOOLEAN", "nil")

        result = cdr if cdr else AtomNode("BOOLEAN", "nil")

        for elem in reversed(elements):
            result = ConsNode(elem, result)

        return result

    def _consume_token(self) -> Token:
        """Consume the current token and advance to the next one."""
        if Parser._is_token_type(self._current_token, "ERROR"):
            self._handle_lexer_error()

        token = self._current_token

        self._last_token_end_pos = (
                sum(map(len, self.lexer.source_code.split("\n")[
                             :token.line - 1]))  # Total number of characters in all lines before the current one
                + len(self.lexer.source_code.split("\n")[
                      :token.line - 1])  # One '\n' for each previous line (newline compensation)
                + (token.end_pos - 1)  # End column of the token in its line (1-based → subtract 1)
        )

        self._current_token = self.lexer.next_token()

        return token

    def _handle_lexer_error(self):
        """
        Handle lexer-related errors such as an unclosed quote.
        Calculates the error's line and column number relative to the current S-expression
        and raises a NoClosingQuoteError accordingly.

        Raises:
            NoClosingQuoteError: If a string is not properly closed before EOF or EOL.
        """
        global_pos = self.lexer.position
        s_exp_start = self._current_s_exp_start_pos  # 包含
        line = 1
        column = 1
        for c in self.lexer.source_code[s_exp_start:global_pos]:
            if c == '\n':
                line += 1
                column = 1
            else:
                column += 1

        raise NoClosingQuoteError(line, column)

    def _relative_token_position(self, token: Token):
        """
        Calculate the line and column number (1-based) of the given token
        relative to the start of the current S-expression.

        Args:
            token (Token): The token whose relative position is to be calculated.

        Returns:
            Tuple[int, int]: A tuple (line, column) representing the relative line and column number,
                             both starting from 1.
        """
        # Calculate the token's absolute position (as character offset from the start of the entire source code)
        global_char_pos = sum(
            len(line) + 1 for line in self.lexer.source_code.split("\n")[:token.line - 1]) + token.start_pos - 1

        # Slice the source code from the current S-expression start up to the token's absolute position
        relative_text = self.lexer.source_code[self._current_s_exp_start_pos:global_char_pos]

        # Split the sliced string to determine how many lines and the final column
        lines = relative_text.split("\n")
        line = len(lines)
        column = len(lines[-1]) + 1  # human-style column
        return line, column

    def _parse_s_exp(self) -> ASTNode | None:
        """
        Parse a single S-expression from the current token stream.

        This function determines the type of the current token and delegates
        parsing to the appropriate handler (e.g., atom, quote, list).

        Returns:
            ASTNode | None: An abstract syntax tree node representing the parsed
                            S-expression, or None in case of invalid structure
                            that raises an exception instead.

        Raises:
            UnexpectedTokenError: If a token is found where a valid S-expression is not possible.
        """
        token = self._consume_token()

        if token.type in ("SYMBOL", "INT", "FLOAT", "STRING", "NIL", "T", "UNKNOWN"):
            return self._parse_atom(token)

        elif token.type == "QUOTE":
            return self._parse_quote()

        elif token.type == "LEFT_PAREN":
            if self._current_token.type == "RIGHT_PAREN":
                self._consume_token()  # consume right parenthesis
                return AtomNode("BOOLEAN", "nil")

            return self._parse_list()

        elif token.type == "DOT":
            value = token.value
            line, pos = self._relative_token_position(token)

            raise UnexpectedTokenError(type_=1, line=line, column=pos, value=value)

        elif token.type == "RIGHT_PAREN":
            value = token.value
            line, pos = self._relative_token_position(token)

            raise UnexpectedTokenError(type_=1, line=line, column=pos, value=value)

    def _parse_list(self) -> ASTNode:
        """
        Parse a single S-expression from the current token stream.

        This function determines the type of the current token and delegates
        parsing to the appropriate handler (e.g., atom, quote, list).

        Returns:
            ASTNode | None: An abstract syntax tree node representing the parsed
            S-expression, or None in case of invalid structure that raises an exception instead.

        Raises:
            UnexpectedTokenError: If a token is found where a valid S-expression is not possible.
            NotFinishError: If the parser encounters EOF in a situation where the input is incomplete,
            such as during a list or quoted expression.
        """
        elements = []

        while not Parser._is_token_type(self._current_token, "RIGHT_PAREN", "EOF"):
            if Parser._is_token_type(self._current_token, "DOT"):
                # If a dot `.` is encountered, convert to a unified cons node structure
                # e.g., (1 2 . 3) => (1 . (2 . 3))
                if not elements:
                    line, pos = self._relative_token_position(self._current_token)
                    value = self._current_token.value

                    raise UnexpectedTokenError(type_=1, line=line, column=pos, value=value)

                self._consume_token()  # skip `.`

                if Parser._is_token_type(self._current_token, "RIGHT_PAREN"):
                    # A Cons Node must have a cdr value
                    line, pos = self._relative_token_position(self._current_token)
                    value = self._current_token.value

                    raise UnexpectedTokenError(type_=1, line=line, column=pos, value=value)

                elif Parser._is_token_type(self._current_token, "EOF"):
                    # Inform parser and repl to wait for remaining user input
                    raise NotFinishError(
                        "Unexpected EOF while parsing list.")  # Tell `repl()` to keep waiting for input

                cdr = self._parse_s_exp()  # Parse the cdr part

                token = self._consume_token()
                if Parser._is_token_type(token, "EOF"):
                    # Inform parser and repl to wait for remaining user input
                    raise NotFinishError(
                        "Unexpected EOF while parsing list.")  # Tell `repl()` to keep waiting for input

                elif not Parser._is_token_type(token, "RIGHT_PAREN"):
                    line, pos = self._relative_token_position(token)
                    value = token.value

                    raise UnexpectedTokenError(type_=2, line=line, column=pos, value=value)

                return Parser._convert_to_cons(elements, cdr)  # Convert to unified format

            elements.append(self._parse_s_exp())

        if Parser._is_token_type(self._current_token, "EOF"):
            raise NotFinishError("Unexpected EOF while parsing list.")  # Tell `repl()` to keep waiting for input

        self._consume_token()  # consume `)`

        # Always convert to ConsNode format: (1 2 3) => (1 . (2 . (3 . nil)))
        return Parser._convert_to_cons(elements, AtomNode("BOOLEAN", "nil"))

    def _parse_quote(self) -> ASTNode:
        """
        Parse a quoted expression, wrapping the result in a QuoteNode.

        This function consumes the next token from `self._current_token` and treats
        the following S-expression as quoted.

        Returns:
            ASTNode: A QuoteNode containing the quoted expression.
        """
        if Parser._is_token_type(self._current_token, "EOF"):
            raise NotFinishError("Unexpected EOF while parsing list.")

        return QuoteNode(self._parse_s_exp())  # Consume and parse quoted expression

    def _parse_atom(self, token: Token) -> ASTNode:
        """
        Parse an atomic token and convert it to the corresponding AtomNode.

        Args:
            token (Token): The atomic token to convert. Expected types include INT, FLOAT,
                           SYMBOL, STRING, T, NIL, or UNKNOWN.

        Returns:
            ASTNode: The corresponding AtomNode with preserved type and value.

        Raises:
            SyntaxError: If the token type is not recognized as a valid atomic type.
        """
        if Parser._is_token_type(token, "INT", "FLOAT", "SYMBOL", "STRING", "UNKNOWN"):
            return AtomNode(token.type, token.value)

        elif Parser._is_token_type(token, "T"):  # #t
            return AtomNode("BOOLEAN", "#t")

        elif Parser._is_token_type(token, "NIL"):  # #f
            return AtomNode("BOOLEAN", "nil")

        raise SyntaxError(f"Unexpected atom type: {token.type}")

    @property
    def current(self):
        """Return the current token being pointed to by the parser."""
        return self._current_token

    @property
    def last_s_exp_pos(self):
        """
        Returns the end index of the last consumed token. If called
        immediately after parsing a complete S-expression, this corresponds
        to the end position of that S-expression.

        Returns:
            int: Character index of the last token in source string.
        """
        return self._last_token_end_pos

    def parse(self) -> ASTNode:
        """
        Entry point for parsing. Parses the next complete S-expression.

        Returns:
            ASTNode: The abstract syntax tree representing the parsed S-expression.
        """
        ast = self._parse_s_exp()

        self._current_s_exp_start_pos = self._last_token_end_pos + 1

        return ast


# Pretty Printer
def pretty_print(node, indent: int = 0):
    """
    Pretty-print the Scheme AST with strict indentation formatting.

    Args:
        node (ASTNode): The root node of the AST to be printed.
        indent (int): Current indentation level.

    Returns:
        str: A formatted string representation of the AST node.
    """
    indent_str = "  " * indent
    next_indent_str = "  " * (indent + 1)

    if isinstance(node, AtomNode):
        # Handle basic types: number, boolean, symbol, string
        if node.type == "STRING":
            return f'"{node.value}"'
        elif node.type == "FLOAT":
            return f"{node.value:.3f}"
        else:
            return f"{node.value}"

    elif isinstance(node, ConsNode):
        elements = []
        current = node

        # Unroll nested cons cells into a list
        while isinstance(current, ConsNode):
            elements.append(current.car)
            current = current.cdr

        # Handle proper list: (a b c)
        if isinstance(current,
                      AtomNode) and current.type == "BOOLEAN" and current.value == "nil":  # ( ssp . nil ) === ( sp1 sp2 sp3 ... spn )
            result = f"( {pretty_print(elements[0], indent + 1)}"

            for elem in elements[1:]:
                result += f"\n{next_indent_str}{pretty_print(elem, indent + 1)}"

            result += f"\n{indent_str})"
            return result

        # Handle improper list: (a b . c)
        result = f"( {pretty_print(elements[0], indent + 1)}"
        for element in elements[1:]:
            result += f"\n{next_indent_str}{pretty_print(element, indent + 1)}"

        result += f"\n{next_indent_str}."
        result += f"\n{next_indent_str}{pretty_print(current, indent + 1)}"
        result += f"\n{indent_str})"
        return result

    elif isinstance(node, QuoteNode):
        # Handle quoted expressions: (quote ...)
        result = f"( quote"

        result += f"\n{next_indent_str}{pretty_print(node.value, indent + 1)}"

        result += f"\n{indent_str})"
        return result

    return f"{node}"


# Repl
def repl():
    lexer = Lexer()
    print("Welcome to OurScheme!")

    empty_line_encountered = False

    partial_input = ""  # for multiline input
    new_s_exp_start = 0
    while True:
        try:
            if not empty_line_encountered:
                print("\n>", end=" ")

            new_input = input()  # read new input

            partial_input += new_input + "\n"  # add new line input

            lexer.reset(partial_input.rstrip("\n"))

            lexer.set_position(new_s_exp_start)

            parser = Parser(lexer)

            # Parsing
            first = True
            try:
                while parser.current.type != "EOF":  # Parse until lexer reached the end
                    if not first:
                        print("\n>", end=" ")

                    result = parser.parse()

                    first = False

                    new_s_exp_start = parser.last_s_exp_pos + 1

                    print(f"{pretty_print(result).lstrip('\n')}")

                partial_input = ""  # after parsing, clear input
                new_s_exp_start = 0

            except NotFinishError:
                empty_line_encountered = True  # wait for user input, so do nothing
                continue

            except NoClosingQuoteError as e:
                print(f"{e} : END-OF-LINE encountered at Line {e.line} Column {e.column}")
                partial_input = ""
                new_s_exp_start = 0

            except UnexpectedTokenError as e:
                if e.type == 1:
                    print(f"{e} : atom or '(' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")
                else:
                    print(f"{e} : ')' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")

                partial_input = ""
                new_s_exp_start = 0

        except EmptyInputError:
            empty_line_encountered = True
            continue

        except EOFError:
            print("ERROR (no more input) : END-OF-FILE encountered", end="")
            break

        empty_line_encountered = False

    print("\nThanks for using OurScheme!", end="")


if __name__ == "__main__":
    n = input()
    repl()
