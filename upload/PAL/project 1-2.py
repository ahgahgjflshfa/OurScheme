class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

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
        self._line_count = 0    # Store current line count

    def reset(self, new_source_code):
        """Reset lexer status, let it tokenize new source code"""
        self.source_code = new_source_code # + "\n"
        self._position = 0
        self._line_count += 1

    def reset_line_count(self):
        """Reset line counter"""
        self._line_count = 0

    def next_token(self):
        """Return next token from source code"""
        self._skip_whitespace_and_comments()

        if self._position >= len(self.source_code):
            return Token("EOF", None)

        char = self.source_code[self._position]
        if char in "()":
            return self._read_paren()

        elif char == ".":
            return self._read_dot()

        elif char == "#":
            return self._read_boolean()

        elif char == "\'":
            return self._read_quote()

        elif char.isalpha():
            return self._read_symbol()

        elif char == "\"":
            return self._read_string()

        elif char in ("+", "-", "*", "/") and self._peek().isspace():   # function symbols
            return self._read_symbol()

        elif char.isdigit() or (char in "+-" and self._peek().isdigit()):   # +100 -5 etc.
            return self._read_int_or_float()

        else:
            return self._read_unknown()

    def has_more_token(self):
        """Check if lexer have more token"""
        return self._position < len(self.source_code)

    def _skip_whitespace_and_comments(self):
        """Skips whitespace and comments"""
        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isspace():  # whitespace
                self._position += 1

            elif char == ";":   # comments
                while self._position < len(self.source_code) and self.source_code[self._position] != "\n":
                    self._position += 1

            else:
                break

    def peek(self):
        """Peek next character"""
        return self.source_code[self._position + 1] if self._position + 1 < len(self.source_code) else ""

    def peek_token(self):
        current_position = self._position
        # current_line_count = self._line_count

        token = self.next_token()

        self._position = current_position
        # self._line_count = current_line_count

        return token

    def _read_string(self):
        """Read string token"""
        self._position += 1  # skip "
        result = ""

        while self._position < len(self.source_code):
            if self.source_code[self._position] == "\"":
                self._position += 1
                return Token("STRING", result)

            # TODO: don't know if this part is needed
            # elif self.source_code[self._position] == "\n":
            #     self._line_count += 1
            #     raise SyntaxError(
            #         f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self._line_count} Column {self._position + 1}"
            #     )

            else:
                result += self.source_code[self._position]
                self._position += 1

        raise SyntaxError(f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self._line_count} Column {self._position + 1}")

    def _read_int_or_float(self):
        """Read number token"""
        start_position = self._position

        # if self.source_code[start_position] in "+-" and not self._peek().isdigit():
        #     raise SyntaxError(f"不合法的符號: {self.source_code[start_position]}")

        self._position += 1

        while self._position < len(self.source_code) and self.source_code[self._position].isdigit():
            self._position += 1

        if self._position < len(self.source_code) and self.source_code[self._position] == ".":
            # if self._peek().isdigit():  # is float
            #     self._position += 1
            #     while self._position < len(self.source_code) and self.source_code[self._position].isdigit():
            #         self._position += 1
            #     return Token("FLOAT", float(self.source_code[start_position:self._position]))
            # else:   # dot pair
            #     return Token("INT", int(self.source_code[start_position:self._position]))

            self._position += 1
            while self._position < len(self.source_code) and self.source_code[self._position].isdigit():
                self._position += 1
            return Token("FLOAT", float(self.source_code[start_position:self._position]))

        return Token("INT", int(self.source_code[start_position:self._position]))

    def _read_symbol(self):
        """Read symbol token (variable names, function names)"""
        start_position = self._position

        while (self._position < len(self.source_code)
               and (self.source_code[self._position].isalnum() or self.source_code[self._position] in "+-*/_!?.#")):
            self._position += 1

        symbol = self.source_code[start_position:self._position]

        if symbol == "t":
            return Token("T", "#t")
        elif symbol == "nil":
            return Token("NIL", "nil")

        return Token("SYMBOL", symbol)

    def _read_boolean(self):
        """Read boolean (only handle #t and #f)"""
        if self.source_code[self._position] == "#":  # #t or #f
            self._position += 1

            if self._position >= len(self.source_code):
                raise Exception("布林值 #t 或 #f 不完整")

            char = self.source_code[self._position]

            if char == "t": # #t
                self._position += 1
                if (self._position < len(self.source_code)
                        and (self.source_code[self._position].isalnum() or self.source_code[self._position] == "_")):
                    raise Exception(f"不合法的布林值: #t{self.source_code[self._position]}")

                return Token("T", "#t")

            elif char == "f":   # #f
                self._position += 1
                if (self._position < len(self.source_code)
                        and (self.source_code[self._position].isalnum() or self.source_code[self._position] == "_")):
                    raise Exception(f"Illegal boolean: #f{self.source_code[self._position]}")

                return Token("NIL", "nil")

            else:
                raise Exception(f"Unknown boolean: #{char}")

        else:
            raise Exception(f"Unknown boolean: {self.source_code[self._position]}")

    def _read_dot(self):
        """Read DOT (.)"""
        self._position += 1

        return Token("DOT", ".")

    def _read_quote(self):
        """Read quote"""
        self._position += 1

        return Token("QUOTE", "quote")

    def _read_paren(self):
        """Read parenthesis"""
        char = self.source_code[self._position]
        self._position += 1

        if char == "(":
            return Token("LEFT_PAREN", "(")
        else:
            return Token("RIGHT_PAREN", ")")

    def _read_unknown(self):
        start = self._position
        while not self.source_code[self._position].isspace():
            self._position += 1

        return Token("UNKNOWN", self.source_code[start:self._position])


def repl():
    lexer = Lexer()

    print("Welcome to OurScheme!")

    while True:
        try:
            s_exp = input()
            if s_exp.lower() == "(exit)":
                break

            #
            if "\\N" in s_exp:
                s_exp = (s_exp
                                    .replace("\\n", "\n")
                                    .replace("\\t", "\t")
                                    .replace("\\\"", "\""))  # 只轉換 `\"`

            else:
                s_exp = bytes(s_exp, "utf-8").decode("unicode_escape")

            lexer.reset(s_exp)
            token = lexer.next_token()
            while token.type != "EOF":
                lexer.reset_line_count()

                if token.type == "STRING":
                    print(f"\n> \"{token.value}\"")

                elif token.type == "LEFT_PAREN":
                    if lexer.peek_token().type == "RIGHT_PAREN":
                        _ = lexer.next_token()

                    print("\n> nil")

                elif token.type == "FLOAT":
                    print(f"\n> {token.value:.3f}")

                else:
                    print(f"\n> {token.value}")
                token = lexer.next_token()

        except Exception as e:
            print(f"\n> {e}")
            lexer.reset_line_count()


    print("Thanks for using OurScheme!")

if __name__ == "__main__":
    n = input()
    repl()
    quit(0)