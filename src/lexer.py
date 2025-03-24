import numpy as np
from .errors import *

class Token:
    def __init__(self, type_, value_, line_= 0, start_pos_ = 0, end_pos_ = 0):
        """

        :param type_:
        :param value_:
        :param line_:
        :param start_pos_: Token starting position
            (input[token_start_pos-1] 才是這個 token 的第一個字元，這是用來讓parser知道這個token在輸出中是第幾個字元，從1開始，不是0)
        :param end_pos_: End position is the token's last character position
            (input[token_end_pos-1] 才是這個 token 的最後一個字元，下一個不是)
        """
        # Note: String Token won't include `"` !
        self.type = type_
        self.value = value_
        self.line = line_
        self.start_pos = start_pos_ # Token starting position
                                    # (input[token_start_pos] 是這個 token 的第一個字元，上一個不是)
        self.end_pos = end_pos_     # End position is the token's last character position
                                    # (input[token_end_pos] 還是這個 token 的最後一個字元，下一個不是)

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
    def position(self):
        return self._position

    @property
    def line(self):
        return self._line_number

    @property
    def column(self):
        return self._column_number

    def reset(self, new_source_code):
        """Reset lexer status, let it tokenize new source code"""
        self.source_code = new_source_code # + "\n"
        self._position = 0
        self._line_number = 1
        self._column_number = 1

    def has_more_token(self) -> bool:
        """Check if lexer have more token

        :return: True if more token exist, else False.
        """
        return self._position < len(self.source_code)

    def peek(self):
        """Peek next character"""
        return self.source_code[self._position + 1] if self._position + 1 < len(self.source_code) else ""

    def peek_token(self):
        current_position = self._position
        token = self.next_token()
        self._position = current_position
        return token

    def set_position(self, pos: int):
        """
        將 Lexer 的掃描位置設為 pos，並將 pos 當作新的「Line 1 Column 1」起點。
        """
        self._position = pos

    def next_token(self):
        """Return next token from source code"""
        self._skip_whitespace_and_comments()

        if self._position >= len(self.source_code):
            return Token("EOF", None)

        char = self.source_code[self._position]

        if char in "()":
            return self._read_paren()

        elif char == "#":
            return self._read_symbol()

        elif char == "\'":
            return self._read_quote()

        elif char.isalpha():
            return self._read_symbol()

        elif char == "\"":
            return self._read_string()

        elif char in ("+", "-", "*", "/") and self.peek().isspace():   # function symbols
            return self._read_symbol()

        elif char == ".":
            peek = self.peek()
            if peek and (peek.isalnum() or peek in "+-*/_!?.#,$%&:<=>@^~"):
                # 若 . 後面是符號的一部分，那它整體應該是 SYMBOL
                return self._read_number_or_symbol()
            else:
                return self._read_dot()

        elif (char.isdigit() or
              (char in "+-" and (self.peek().isdigit() or self.peek() == "."))
        ):
            return self._read_number_or_symbol()

        else:
            return self._read_unknown()

    def _skip_whitespace_and_comments(self):
        """Skips whitespace and comments"""
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

    def _read_string(self):
        """Read string token"""
        start_pos = self._column_number
        self._position += 1  # skip "
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

                if self.position >= len(self.source_code):
                    raise NoClosingQuoteError()

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

        raise NoClosingQuoteError()

    def _read_number_or_symbol(self):
        """Read number token or symbol starting with a number"""
        start_pos = self._column_number
        number_str = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isalnum() or char in "+-*/_!?.#,$%&:<=>@^~":
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

    def _read_symbol(self):
        """Read symbol token (variable names, function names)"""
        start_pos = self._column_number
        symbol = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isalnum() or char in "+-*/_!?.#,":   # TODO: check legal characters
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

    def _read_dot(self):
        """Read DOT (.)"""
        dot_pos = self._column_number
        self._position += 1
        self._column_number += 1

        return Token("DOT", ".", self._line_number, dot_pos, dot_pos)

    def _read_quote(self):
        """Read quote"""
        quote_pos = self._column_number
        self._position += 1
        self._column_number += 1

        return Token("QUOTE", "quote", self._line_number, quote_pos, quote_pos)

    def _read_paren(self):
        """Read parenthesis"""
        char = self.source_code[self._position]
        paren_pos = self._column_number
        self._position += 1
        self._column_number += 1

        if char == "(":
            return Token("LEFT_PAREN", "(", self._line_number, paren_pos, paren_pos)
        else:
            return Token("RIGHT_PAREN", ")", self._line_number, paren_pos, paren_pos)

    def _read_unknown(self):
        start_pos = self._column_number
        unknown_str = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isspace() or char in "()":
                break

            unknown_str += char
            self._position += 1
            self._column_number += 1

        end_pos = self._column_number - 1

        return Token("UNKNOWN", unknown_str, self._line_number, start_pos, end_pos)