import numpy as np


class Token:
    def __init__(self, type_, value_, line_= 0, start_pos_ = 0, end_pos_ = 0):
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
        self.start_pos = start_pos_ # Start index in the source string
        self.end_pos = end_pos_     # End index in the source string (inclusive)

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value

        return False


class Lexer:
    def __init__(self):
        self.source_code = ""   # Store 1 line of user input in repl.
        self._position = 0      # Store current location.
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
        self.source_code = new_source_code # + "\n"
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

            elif char == ";":   # comments
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
        self._position += 1  # 跳過開頭 " 符號
        self._column_number += 1
        result = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if self.source_code[self.position] == "\"":
                end_pos = self._column_number   # 包含 "
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

            if char.isalnum() or char in "!#$%&*+,-./:<=>?@[\\]^_`{|}~":   # TODO: check legal characters
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
