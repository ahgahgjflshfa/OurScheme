from src.lexer import Lexer, Token
from src.ast_nodes import *
from src.errors import NoClosingQuoteError, NotFinishError, EmptyInputError, UnexpectedTokenError


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
                sum(map(len, self.lexer.source_code.split("\n")[:token.line - 1]))  # Total number of characters in all lines before the current one
                + len(self.lexer.source_code.split("\n")[:token.line - 1])          # One '\n' for each previous line (newline compensation)
                + (token.end_pos - 1)                                               # End column of the token in its line (1-based → subtract 1)
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
        column = 1
        for c in self.lexer.source_code[s_exp_start:global_pos]:
            if c == '\n':
                column = 1
            else:
                column += 1

        line = self.lexer.line

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
                self._consume_token()   # consume right parenthesis
                return AtomNode("BOOLEAN", "nil")

            return self._parse_list()

        elif token.type == "DOT":
            value = token.value
            line, pos = self._relative_token_position(token)

            raise UnexpectedTokenError(line=line, column=pos, value=value)

        elif token.type == "RIGHT_PAREN":
            value = token.value
            line, pos = self._relative_token_position(token)

            raise UnexpectedTokenError(line=line, column=pos, value=value)

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

                    raise UnexpectedTokenError(line=line, column=pos, value=value)

                self._consume_token()  # skip `.`

                if Parser._is_token_type(self._current_token, "RIGHT_PAREN"):
                    # A Cons Node must have a cdr value
                    line, pos = self._relative_token_position(self._current_token)
                    value = self._current_token.value

                    raise UnexpectedTokenError(line=line, column=pos, value=value)

                elif Parser._is_token_type(self._current_token, "EOF"):
                    # Inform parser and repl to wait for remaining user input
                    raise NotFinishError("Unexpected EOF while parsing list.")  # Tell `repl()` to keep waiting for input

                cdr = self._parse_s_exp()   # Parse the cdr part

                token = self._consume_token()
                if Parser._is_token_type(token, "EOF"):
                    # Inform parser and repl to wait for remaining user input
                    raise NotFinishError("Unexpected EOF while parsing list.")  # Tell `repl()` to keep waiting for input

                elif not Parser._is_token_type(token, "RIGHT_PAREN"):
                    line, pos = self._relative_token_position(token)
                    value = token.value

                    raise UnexpectedTokenError(line=line, column=pos, value=value)

                return Parser._convert_to_cons(elements, cdr) # Convert to unified format

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
        return  self._last_token_end_pos

    def parse(self) -> ASTNode:
        """
        Entry point for parsing. Parses the next complete S-expression.

        Returns:
            ASTNode: The abstract syntax tree representing the parsed S-expression.
        """
        ast = self._parse_s_exp()

        self._current_s_exp_start_pos = self._last_token_end_pos + 1

        return ast
