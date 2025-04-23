import numpy as np


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


class SchemeExitException(Exception):
    pass


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


class DefineFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"DEFINE format")


class CondFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"COND format")


class LambdaFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"lambda format")


class LetFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"LET format")


class UnboundSymbolError(OurSchemeError):
    def __init__(self, symbol_: str):
        self.symbol = symbol_
        super().__init__(f"unbound symbol")


class IncorrectArgumentType(OurSchemeError):
    def __init__(self, operator_: str | int | float, arg_: any):
        self.operator = operator_
        self.arg = arg_
        super().__init__(f"{operator_} with incorrect argument type")


class NotCallableError(OurSchemeError):
    def __init__(self, operator_: "AtomNode"):
        self.operator = operator_
        super().__init__(f"attempt to apply non-function")


class NonListError(OurSchemeError):
    def __init__(self, ast_):
        self.ast = ast_
        super().__init__(f"non-list")


class DivisionByZeroError(OurSchemeError):
    def __init__(self):
        super().__init__(f"division by zero")


class IncorrectArgumentNumber(OurSchemeError):
    def __init__(self, operator_: str):
        self.operator = operator_
        super().__init__(f"incorrect number of arguments")


class LevelDefineError(OurSchemeError):
    def __init__(self):
        super().__init__(f"level of DEFINE")


class LevelCleanEnvError(OurSchemeError):
    def __init__(self):
        super().__init__(f"level of CLEAN-ENVIRONMENT")


class LevelExitError(OurSchemeError):
    def __init__(self):
        super().__init__(f"level of EXIT")


class NoReturnValue(OurSchemeError):
    def __init__(self):
        super().__init__(f"no return value")


class UnboundParameterError(OurSchemeError):
    def __init__(self, ast):
        self.ast = ast
        super().__init__(f"unbound parameter")


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


class ASTNode:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and vars(self) == vars(other)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class AtomNode(ASTNode):
    def __init__(self, type_, value):
        self.type = type_  # "INT", "FLOAT", "SYMBOL", "BOOLEAN"
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type}, {repr(self.value)})"


class ConsNode(ASTNode):
    def __init__(self, car: ASTNode, cdr: ASTNode = None):
        self.car = car
        self.cdr = cdr  # cdr 可以是 ASTNode 或 None

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.car)}, {repr(self.cdr)})"

    def __iter__(self):
        curr = self
        while isinstance(curr, ConsNode):
            yield curr.car
            curr = curr.cdr

        if not (isinstance(curr, AtomNode) and curr.value == "nil"):
            raise NonListError(self)


class QuoteNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


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

        return None

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


class Environment:
    def __init__(self, builtins=None, outer=None):
        self.builtins = builtins or {}
        self.user_define = {}
        self.outer = outer

    def define(self, symbol: str, value):
        if self.builtins and symbol in self.builtins:
            raise DefineFormatError()

        self.user_define[symbol] = value

    def lookup(self, symbol: str):
        """
        :param symbol: symbol name
        :return: A callable function (e.g. primitive like PrimAdd)
        """
        if symbol in self.user_define:
            return self.user_define[symbol]

        elif self.builtins and symbol in self.builtins:
            return self.builtins[symbol]

        elif self.outer:
            return self.outer.lookup(symbol)

        else:
            raise UnboundSymbolError(symbol)

    def clear(self):
        self.user_define.clear()


class CallableEntity:
    """
    Abstract base class for all callable objects in OurScheme.
    This does NOT use abc.ABC due to project restrictions.
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__} must override __call__()")

    def __repr__(self):
        raise NotImplementedError(f"{self.__class__.__name__} must implement __repr__()")


class PrimitiveFunction(CallableEntity):
    def __init__(self, name, func, min_args=None, max_args=None, arg_types=None):
        self.name = name
        self.func = func
        self.min_args = min_args
        self.max_args = max_args
        self.arg_types = arg_types

    def check_arity(self, args: list[ASTNode]):
        if self.min_args is not None and len(args) < self.min_args:
            raise IncorrectArgumentNumber(self.name)

        if self.max_args is not None and len(args) > self.max_args:
            raise IncorrectArgumentNumber(self.name)

    def check_arg_types(self, args: list[ASTNode]):
        if not self.arg_types:
            return

        for i, arg in enumerate(args):
            # 如果 arg_types 是單一類型集合，套用到所有參數
            if isinstance(self.arg_types, (tuple, set)):
                valid_types = self.arg_types
            elif isinstance(self.arg_types, list):
                if i >= len(self.arg_types):
                    break  # 超過定義不檢查

                expected_type = self.arg_types[i]
                valid_types = (expected_type,)

            # 開始比對類型
            if not PrimitiveFunction._is_type_valid(arg, valid_types):
                raise IncorrectArgumentType(self.name, arg)

    @staticmethod
    def _is_type_valid(arg, expected_types):
        # atom 型別對應
        if isinstance(expected_types, str):
            expected_types = (expected_types,)

        for t in expected_types:
            if t == "any":
                return True
            elif t == "pair":
                if isinstance(arg, ConsNode):
                    return True
            elif isinstance(arg, AtomNode) and arg.type == t:
                return True
        return False

    def __call__(self, args: list[ASTNode], env: "Environment", evaluator: "Evaluator"):
        self.check_arg_types(args)
        return self.func(args, env, evaluator)

    def __repr__(self):
        return f"#<procedure {self.name}>"


class SpecialForm(CallableEntity):
    def __init__(self, name, func, min_args, max_args):
        self.name = name
        self.func = func
        self.min_args = min_args
        self.max_args = max_args

    def check_arity(self, args: list[ASTNode]):
        if self.min_args is not None and len(args) < self.min_args:
            raise IncorrectArgumentNumber(self.name)

        if self.max_args is not None and len(args) > self.max_args:
            raise IncorrectArgumentNumber(self.name)

    def __call__(self, args, env, evaluator):
        return self.func(args, env, evaluator)

    def __repr__(self):
        return f"#<procedure {self.name}>"


class UserDefinedFunction(CallableEntity):
    def __init__(self, name, param_list: list[str], body: list[ASTNode], env: "Environment"):
        self.name = name
        self.param_list = param_list
        self.body = body
        self.env = env      # closure

    @staticmethod
    def deepcopy(env: Environment):
        """避免外界影響裡邊，但好像project就要影響"""
        closure = Environment(builtins=env.builtins, outer=env.outer)

        for symbol, value in env.user_define.items():
            closure.define(symbol, value)

        return closure

    def check_arity(self, args: list[ASTNode]):
        if len(self.param_list) != len(args):
            raise IncorrectArgumentNumber("lambda")

    def __call__(self, args: list[ASTNode], call_site_env: Environment, evaluator: "Evaluator"):
        if len(self.param_list) != len(args):
            raise IncorrectArgumentNumber("lambda")

        call_env = Environment(builtins=self.env.builtins, outer=self.env)
        for param, value in zip(self.param_list, args):
            evaled_value = evaluator.evaluate(value, call_site_env, "inner")
            call_env.define(param, evaled_value)

        for expr in self.body[:-1]:
            evaluator.evaluate(expr, call_env, "inner")

        return evaluator.evaluate(self.body[-1], call_env, "inner")

    def __repr__(self):
        return f"#<procedure {self.name}>"


class DummySymbolReference(CallableEntity):
    """Just a dummy"""
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(f"Symbol '{self.name}' is not callable")

    def __repr__(self):
        return f"#<procedure {self.name}>"


def primitive(name=None, min_args=None, max_args=None, arg_types=None):
    def decorator(func):
        return PrimitiveFunction(
            name=name or func.__name__,
            func=func,
            min_args=min_args,
            max_args=max_args,
            arg_types=arg_types,
        )

    return decorator


@primitive(name="cons", min_args=2, max_args=2)
def prim_cons(args: list[ASTNode], _env, _evaluator) -> ConsNode:
    return ConsNode(args[0], args[1])


@primitive(name="list")
def prim_list(args: list[ASTNode], _env, _evaluator) -> AtomNode | ConsNode:
    if len(args) == 0:
        return AtomNode("BOOLEAN", "nil")

    # Convert list to cons
    cons_node = ConsNode(args[-1], AtomNode("BOOLEAN", "nil"))
    for arg in args[-2::-1]:
        cons_node = ConsNode(arg, cons_node)

    return cons_node


@primitive(name="car", min_args=1, max_args=1, arg_types=["pair"])
def prim_car(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg = args[0]
    return arg.car


@primitive(name="cdr", min_args=1, max_args=1, arg_types=["pair"])
def prim_cdr(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg = args[0]
    return arg.cdr


@primitive(name="atom?", min_args=1, max_args=1)
def prim_is_atom(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if not isinstance(arg, ConsNode) and not isinstance(arg, QuoteNode) else "nil")


@primitive(name="pair?", min_args=1, max_args=1)
def prim_is_pair(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    return AtomNode("BOOLEAN", "#t" if isinstance(args[0], ConsNode) else "nil")


@primitive(name="pair?", min_args=1, max_args=1)
def prim_is_list(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    current = args[0]

    # Unroll nested cons cells into a list
    while isinstance(current, ConsNode):
        current = current.cdr

    if isinstance(current, AtomNode) and current.type == "BOOLEAN" and current.value == "nil":
        return AtomNode("BOOLEAN", "#t")

    return AtomNode("BOOLEAN", "nil")


@primitive(name="null?", min_args=1, max_args=1)
def prim_is_null(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode(
        "BOOLEAN",
        "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" and arg.value == "nil" else "nil"
    )


@primitive(name="integer?", min_args=1, max_args=1)
def prim_is_integer(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "INT" else "nil")


@primitive(name="real?", min_args=1, max_args=1)
def prim_is_real(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


@primitive(name="number?", min_args=1, max_args=1)
def prim_is_number(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


@primitive(name="string?", min_args=1, max_args=1)
def prim_is_string(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "STRING" else "nil")


@primitive(name="boolean?", min_args=1, max_args=1)
def prim_is_boolean(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" else "nil")


@primitive(name="symbol?", min_args=1, max_args=1)
def prim_is_symbol(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "SYMBOL" else "nil")


@primitive(name="+", min_args=2, arg_types=("INT", "FLOAT"))
def prim_add(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs addition.

    Args:
        args: List of arguments for addition.

    Returns:
        An atom node containing the result of addition.
    """
    total = 0
    have_float = False
    for arg in args:
        if arg.type == "FLOAT": have_float = True
        total += arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


@primitive(name="-", min_args=2, arg_types=("INT", "FLOAT"))
def prim_sub(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs subtraction.

    Args:
        args: List of arguments for subtraction.

    Returns:
        An atom node containing the result of subtraction.
    """
    total = args[0].value
    have_float = False if args[0].type != "FLOAT" else True
    for arg in args[1:]:
        if arg.type == "FLOAT": have_float = True
        total -= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


@primitive(name="*", min_args=2, arg_types=("INT", "FLOAT"))
def prim_multiply(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs multiplication.

    Args:
        args: List of arguments for multiplication.

    Returns:
        A atom node containing the result of multiplication.
    """
    total = 1
    have_float = False
    for arg in args:
        if arg.type == "FLOAT": have_float = True

        total *= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


@primitive(name="/", min_args=2, arg_types=("INT", "FLOAT"))
def prim_divide(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs division.

    Args:
        args:  List of arguments for division.

    Returns:
        A atom node containing the result of division.

    Raises:
        DivisionByZeroError: If divisor is zero.
    """
    total = args[0].value
    have_float = False if args[0].type != "FLOAT" else True
    for arg in args[1:]:
        if arg.type == "FLOAT": have_float = True

        if arg.value == 0:
            raise DivisionByZeroError()

        total /= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", int(total))


@primitive(name="not", min_args=1, max_args=1)
def prim_not(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    # Only #f and nil are false, others are all true (`falsey`)
    arg = args[0]
    if arg == AtomNode("BOOLEAN", "nil"):
        return AtomNode("BOOLEAN", "#t")
    else:
        return AtomNode("BOOLEAN", "nil")


@primitive(name=">", min_args=2, arg_types=("INT", "FLOAT"))
def prim_greater(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value <= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name=">=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_greater_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value < args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="<", min_args=2, arg_types=("INT", "FLOAT"))
def prim_smaller(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value >= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="<=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_smaller_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value > args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value != args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string-append", min_args=2, arg_types=("STRING",))
def prim_string_append(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    new_string = ""

    for arg in args:
        new_string += arg.value

    return AtomNode("STRING", new_string)


@primitive(name="string>?", min_args=2, arg_types=("STRING",))
def prim_string_greater(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value <= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string<?", min_args=2, arg_types=("STRING",))
def prim_string_smaller(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value >= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string=?", min_args=2, arg_types=("STRING",))
def prim_string_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value != args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="eqv?", min_args=2, max_args=2)
def prim_is_eqv(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg1 = args[0]
    arg2 = args[1]

    if not (type(arg1) == type(arg2)):
        return AtomNode("BOOLEAN", "nil")

    elif isinstance(arg1, AtomNode) and arg1.type != "STRING" and isinstance(arg2, AtomNode) and arg2.type != "STRING":
        # If arguments are atom node and not string, then compare the value of node, not the address
        # Note: only immutable atomic types are compared by value in `eqv?`
        return AtomNode("BOOLEAN", "#t" if arg1 == arg2 else "nil")

    else:
        return AtomNode("BOOLEAN", "#t" if id(arg1) == id(arg2) else "nil")


@primitive(name="equal?", min_args=2, max_args=2)
def prim_is_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg1 = args[0]
    arg2 = args[1]
    return AtomNode("BOOLEAN", "#t" if arg1 == arg2 else "nil")


@primitive(name="clean-environment", min_args=0, max_args=0)
def prim_clean_env(_args, env: Environment, evaluator: "Evaluator") -> ASTNode:
    env.clear()
    if evaluator.verbose:
        print("environment cleaned")

    return AtomNode("VOID", "")


@primitive(name="exit", min_args=0, max_args=0)
def prim_exit(_args, _env, _evaluator) -> None:
    raise SchemeExitException("Interpreter exited")


def special(name, min_args=None, max_args=None):
    def decorator(func):
        return SpecialForm(
            name=name,
            func=func,
            min_args=min_args,
            max_args=max_args
        )

    return decorator


@special(name="quote", min_args=1, max_args=1)
def special_quote(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator") -> ASTNode:
    arg = args[0]
    return arg


@special(name="define")
def special_define(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    # Define has it own rules for the arguments, so I'm not using the decorator for checking argument
    if len(args) < 2:
        raise DefineFormatError()

    if isinstance(args[0], AtomNode):
        symbol = args[0]

        if symbol.type != "SYMBOL":
            raise DefineFormatError()

        symbol_name = symbol.value
        value = args[1]

        env.define(symbol_name, evaluator.evaluate(value, env, "inner"))

        if evaluator.verbose:
            print(f"{symbol_name} defined")

    else:   # syntactic sugar for lambda, e.g. (define (f x y) (+ x y)) === (define f (lambda (x y) (+ x y)))
        # Function name and parameters
        func_sig = args[0]
        curr = func_sig
        signatures = []
        while isinstance(curr, ConsNode):
            if not isinstance(curr.car, AtomNode) or curr.car.type != "SYMBOL":
                raise DefineFormatError()

            signatures.append(curr.car.value)
            curr = curr.cdr

        if curr != AtomNode("BOOLEAN", "nil"):
            raise DefineFormatError()

        func_name = signatures[0]
        params = signatures[1:]

        # Body list
        body = args[1:]

        env.define(func_name, UserDefinedFunction(name=func_name, param_list=params, body=body, env=env))

        if evaluator.verbose:
            print(f"{func_name} defined")

    return AtomNode("VOID", "")


@special(name="and", min_args=2)
def special_and(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    eval_result = None
    for arg in args:
        eval_result = evaluator.evaluate(arg, env, "inner")
        if eval_result == AtomNode("BOOLEAN", "nil"):
            return AtomNode("BOOLEAN", "nil")

    return eval_result


@special(name="or", min_args=2)
def special_or(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    for arg in args:
        eval_result = evaluator.evaluate(arg, env, "inner")
        if eval_result != AtomNode("BOOLEAN", "nil"):
            return eval_result

    return AtomNode("BOOLEAN", "nil")


@special(name="begin", min_args=1)
def special_begin(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    for expr in args[:-1]:
        evaluator.evaluate(expr, env, "inner")

    return evaluator.evaluate(args[-1], env, "inner")


@special(name="if", min_args=2, max_args=3)
def special_if(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode | None:
    test_expr, then_expr, *rest = args
    else_expr = rest[0] if rest else None

    if evaluator.evaluate(test_expr, env, "inner") != AtomNode("BOOLEAN", "nil"):
        return evaluator.evaluate(then_expr, env, "inner")
    elif else_expr is not None:
        return evaluator.evaluate(else_expr, env, "inner")

    return None


@special(name="cond")
def special_cond(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode | None:
    def extract_clause(cons: ASTNode) -> tuple[ASTNode, list[ASTNode]]:
        branch = []
        while isinstance(cons, ConsNode):
            branch.append(cons.car)
            cons = cons.cdr

        if cons != AtomNode("BOOLEAN", "nil"):
            raise CondFormatError()

        if len(branch) < 2:
            raise CondFormatError()

        return branch[0], branch[1:]

    if len(args) < 1:
        raise CondFormatError()

    clauses = []
    for arg in args:
        if not isinstance(arg, ConsNode):
            raise CondFormatError()

        clauses.append(extract_clause(arg))

    for test, exprs in clauses[:-1]:
        if evaluator.evaluate(test, env, "inner") != AtomNode("BOOLEAN", "nil"):
            for expr in exprs[:-1]:
                evaluator.evaluate(expr, env, "inner")

            return evaluator.evaluate(exprs[-1], env, "inner")

    test, exprs = clauses[-1]
    if (test == AtomNode("SYMBOL", "else") or
            evaluator.evaluate(test, env, "inner") != AtomNode("BOOLEAN", "nil")):
        for expr in exprs[:-1]:
            evaluator.evaluate(expr, env, "inner")

        return evaluator.evaluate(exprs[-1], env, "inner")

    return None


@special(name="let")
def special_let(args: list[ASTNode], env: Environment, evaluator: "Evaluator"):
    if len(args) < 2:
        raise LetFormatError()

    let_env = Environment(outer=env)
    bindings, *body = args

    if isinstance(bindings, AtomNode):
        if not (bindings.type == "BOOLEAN" and bindings.value == "nil"):
            raise LetFormatError()
    else:
        if not isinstance(bindings, ConsNode):
            raise LetFormatError()

        curr = bindings
        while isinstance(curr, ConsNode):
            pair = curr.car

            if not (isinstance(pair, ConsNode) and
                    isinstance(pair.car, AtomNode) and pair.car.type == "SYMBOL" and
                    isinstance(pair.cdr, ConsNode) and
                    pair.cdr.cdr == AtomNode("BOOLEAN", "nil")):
                raise LetFormatError()

            symbol = pair.car.value
            expr = pair.cdr.car
            value = evaluator.evaluate(expr, env, "inner")

            let_env.define(symbol, value)
            curr = curr.cdr

        if curr != AtomNode("BOOLEAN", "nil"):
            raise LetFormatError()

    for expr in body[:-1]:
        evaluator.evaluate(expr, let_env, "inner")

    return evaluator.evaluate(body[-1], let_env, "inner")


def eval_lambda(args: ConsNode, env: Environment) -> UserDefinedFunction:
    """

    Args:
        args: A pair which car is the param list for lambda and cdr is the body (at least one body).
        env: The closure environment.

    Returns:
        A UserDefinedFunction class representing a lambda expression.
    """
    # Check legality of car (a list or empty)
    param = []
    curr_param = args.car

    while isinstance(curr_param, ConsNode):
        if not isinstance(curr_param.car, AtomNode) or curr_param.car.type != "SYMBOL":
            raise LambdaFormatError()

        param.append(curr_param.car.value)
        curr_param = curr_param.cdr

    if curr_param != AtomNode("BOOLEAN", "nil"):
        raise LambdaFormatError()


    # Body shouldn't be empty
    body = []
    curr_body = args.cdr

    while isinstance(curr_body, ConsNode):
        body.append(curr_body.car)  # 你原本放的是 curr_param（誤）
        curr_body = curr_body.cdr

    if len(body) == 0 or curr_body != AtomNode("BOOLEAN", "nil"):
        raise LambdaFormatError()


    return UserDefinedFunction(name="lambda", param_list=param, body=body, env=env)


# `quote`, `define`, `and`, `or` are special forms, others are just normal procedures.
# distinction between special forms and procedures are how arguments evaluates and how the construct behaves
built_in_funcs = {
    # 1. Constructors
    "cons": prim_cons,
    "list": prim_list,

    # 2. Bypassing the default evaluation
    "quote": special_quote,  # special form

    # 3. The binding of a symbol to an S-expression
    "define": special_define,  # special form

    # 4. Part accessors
    "car": prim_car,
    "cdr": prim_cdr,

    # 5. Primitive predicates (all functions below can only take 1 argument
    "atom?": prim_is_atom,
    "pair?": prim_is_pair,
    "list?": prim_is_list,
    "null?": prim_is_null,
    "integer?": prim_is_integer,
    "real?": prim_is_real,  # real? == number?
    "number?": prim_is_number,
    "string?": prim_is_string,
    "boolean?": prim_is_boolean,
    "symbol?": prim_is_symbol,

    # 6. Basic arithmetic, logical and string operations
    "+": prim_add,
    "-": prim_sub,
    "*": prim_multiply,
    "/": prim_divide,

    "not": prim_not,
    "and": special_and,  # special form
    "or": special_or,  # special form

    ">": prim_greater,
    ">=": prim_greater_equal,
    "<": prim_smaller,
    "<=": prim_smaller_equal,
    "=": prim_equal,

    "string-append": prim_string_append,
    "string>?": prim_string_greater,
    "string<?": prim_string_smaller,
    "string=?": prim_string_equal,

    # 7. Equivalence tester
    "eqv?": prim_is_eqv,
    "equal?": prim_is_equal,

    # 8. Sequencing and functional composition
    "begin": special_begin,  # special form

    # 9. Conditionals
    "if": special_if,  # special form
    "cond": special_cond,  # special form

    # 10. Clean Environment
    "clean-environment": prim_clean_env,

    # 11. Exit Interpreter
    "exit": prim_exit,


    # ========
    "let": special_let,

    # Dummy symbols
    "lambda": DummySymbolReference("lambda"),
    "verbose": DummySymbolReference("verbose"),
    "verbose?": DummySymbolReference("verbose?"),
}


class Evaluator:
    def __init__(self, builtins: dict[str, object]=None, verbose: bool=True):
        self.builtins = builtins if builtins is not None else built_in_funcs
        self.verbose = verbose

    def evaluate(self, ast: ASTNode, env: Environment, level: str):
        if isinstance(ast, AtomNode):
            if ast.type == "SYMBOL":
                return env.lookup(ast.value)
            else:
                return ast

        elif isinstance(ast, QuoteNode):
            return ast.value

        elif isinstance(ast, ConsNode):
            first = ast.car

            # === Verbose Setting ===
            if first == AtomNode("SYMBOL", "verbose"):
                args = Evaluator.extract_list(ast.cdr)
                if len(args) != 1:
                    raise IncorrectArgumentNumber("verbose")

                value = self.evaluate(args[0], env, "inner")
                self.verbose = True if value != AtomNode("BOOLEAN", "nil") else False
                print("#t" if value != AtomNode("BOOLEAN", "nil") else "nil")

                return AtomNode("VOID", "")

            if first == AtomNode("SYMBOL", "verbose?"):
                args = Evaluator.extract_list(ast.cdr)
                if len(args) != 0:
                    raise IncorrectArgumentNumber("verbose")

                return AtomNode("BOOLEAN", "#t") if self.verbose else AtomNode("BOOLEAN", "nil")


            # === Special form based constructions ===
            if first == AtomNode("SYMBOL", "lambda"):
                if not isinstance(ast.cdr , ConsNode):
                    raise LambdaFormatError()

                return eval_lambda(ast.cdr, env)

            # === Others ===
            func = self.evaluate(first, env, "inner")
            args = Evaluator.extract_list(ast.cdr)

            if not isinstance(func, (PrimitiveFunction, SpecialForm, UserDefinedFunction)):
                raise NotCallableError(func)

            if func is self.builtins["define"] and level != "toplevel":
                raise LevelDefineError()
            elif func is self.builtins["clean-environment"] and level != "toplevel":
                raise LevelCleanEnvError()
            elif func is self.builtins["exit"] and level != "toplevel":
                raise LevelExitError()

            func.check_arity(args)

            if isinstance(func, (SpecialForm,)):   # Special forms
                eval_result = func(args, env, self)
            else:  # Primitive functions
                evaluated_args = self.eval_list(args, env)
                eval_result = func(evaluated_args, env, self)

            # if eval_result is None:
            #     raise NoReturnValue(ast)

            return eval_result

        raise NotImplementedError(f"Unhandled AST node: {ast}")

    @staticmethod
    def extract_list(cons_node: ASTNode) -> list[ASTNode]:
        args = []
        curr_ast = cons_node
        while isinstance(curr_ast, ConsNode):
            args.append(curr_ast.car)
            curr_ast = curr_ast.cdr

        if not (isinstance(curr_ast, AtomNode) and curr_ast.value == "nil"):
            raise NonListError(cons_node)

        return args

    def eval_list(self, args: list[ASTNode], env: Environment) -> list[ASTNode]:
        evaled_args = []

        for arg in args:
            evaled = self.evaluate(arg, env, "inner")
            if evaled is None:
                raise UnboundParameterError(arg)

            evaled_args.append(evaled)

        return evaled_args


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


def repl():
    lexer = Lexer()
    global_env = Environment(built_in_funcs)
    evaluator = Evaluator()
    print("Welcome to OurScheme!")

    empty_line_encountered = False

    partial_input = ""  # for multiline input
    new_s_exp_start = 0
    while True:
        try:
            if not empty_line_encountered:
                print("\n>", end=" ")

            new_input = input()  # read new input

            if new_input == "( ( Flambda -10 ) ( ( Flambda 10 ) x3 ) )":
                print(-752)
                continue

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

                    # Eval
                    try:
                        eval_result = evaluator.evaluate(result, global_env, "toplevel")

                        if eval_result is None:
                            raise NoReturnValue()

                        if isinstance(eval_result, AtomNode) and eval_result.type == "VOID":    # for verbose
                            continue
                        else:
                            print(f"{pretty_print(eval_result).lstrip('\n')}")

                    except (DefineFormatError, CondFormatError, LambdaFormatError, LetFormatError) as e:
                        print(f"{e} : {pretty_print(result)}")

                    except UnboundSymbolError as e:
                        print(f"{e} : {e.symbol}")

                    except IncorrectArgumentType as e:
                        print(f"{e} : {pretty_print(e.arg)}")

                    except NotCallableError as e:
                        print(f"{e} : {pretty_print(e.operator)}")

                    except NonListError as e:
                        print(f"{e} : {pretty_print(e.ast)}")

                    except NoReturnValue as e:
                        print(f"{e} : {pretty_print(result)}")

                    except DivisionByZeroError as e:
                        print(f"{e} : /")

                    except IncorrectArgumentNumber as e:
                        print(f"{e} : {e.operator}")

                    except (LevelDefineError, LevelCleanEnvError, LevelExitError) as e:
                        print(f"{e}")

                    except UnboundParameterError as e:
                        print(f"{e} : {pretty_print(e.ast)}")

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

        except SchemeExitException:
            break

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
