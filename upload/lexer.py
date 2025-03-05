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
    def __init__(self, source_code: str):
        """

        :param source_code:
        """
        self.source_code = source_code      # Store 1 line of user input in repl.
        self.position = 0                   # Store current location.

    def reset(self, new_source_code):
        """Reset lexer status, let it tokenize new source code"""
        self.source_code = new_source_code
        self.position = 0

    def next_token(self) -> Token:
        """Return next token from source code"""
        self._skip_whitespace_and_comments()

        if self.position >= len(self.source_code):
            return Token("EOF", None)

        char = self.source_code[self.position]
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
            raise SyntaxError(f"Unknown character: {char}")

    def has_more_token(self):
        """Check if lexer have more token"""
        return self.position < len(self.source_code)

    def _skip_whitespace_and_comments(self):
        """Skips whitespace and comments"""
        while self.position < len(self.source_code):
            char = self.source_code[self.position]

            if char.isspace():  # whitespace
                self.position += 1
            elif char == ";":   # comments
                while self.position < len(self.source_code) and self.source_code[self.position] != "\n":
                    self.position += 1
            else:
                break

    def _peek(self):
        """Peek next character"""
        return self.source_code[self.position + 1] if self.position + 1 < len(self.source_code) else ""

    def _peek_token(self):
        current_position = self.position
        token = self.next_token()
        self.position = current_position
        return token

    def _read_string(self):
        """Read string token"""
        self.position += 1  # skip "
        result = ""

        while self.position < len(self.source_code):
            if self.source_code[self.position] == "\"":
                self.position += 1
                return Token("STRING", result)

            elif self.source_code[self.position] == "\\": # Escape characters
                self.position += 1  # skip backslash

                if self.position >= len(self.source_code):
                    raise SyntaxError("Missing closing \"")

                if self.source_code[self.position] == "n":      # newline
                    result += "\n"

                elif self.source_code[self.position] == "t":    # tab
                    result += "\t"

                elif self.source_code[self.position] == "\"":   # double quote
                    result += "\""

                elif self.source_code[self.position] == "\\":   # backslash
                    result += "\\"

                else:
                    raise SyntaxError(f"Invalid escape character: '\\{self.source_code[self.position]}'")

                self.position += 1

            elif self.source_code[self.position] == "\n":
                raise SyntaxError("Missing closing \"")

            else:
                result += self.source_code[self.position]
                self.position += 1

        raise SyntaxError("Missing closing \"")

    def _read_int_or_float(self):
        """Read number token"""
        start_position = self.position

        self.position += 1

        while self.position < len(self.source_code) and self.source_code[self.position].isdigit():
            self.position += 1

        if self.position < len(self.source_code) and self.source_code[self.position] == ".":
            if self._peek().isdigit():  # is float
                self.position += 1
                while self.position < len(self.source_code) and self.source_code[self.position].isdigit():
                    self.position += 1
                return Token("FLOAT", float(self.source_code[start_position:self.position]))
            else:   # dot pair
                return Token("INT", int(self.source_code[start_position:self.position]))

        return Token("INT", int(self.source_code[start_position:self.position]))

    def _read_symbol(self):
        """Read symbol token (variable names, function names)"""
        start_position = self.position

        while (self.position < len(self.source_code)
               and (self.source_code[self.position].isalnum() or self.source_code[self.position] in "+-*/_!?.")):
            self.position += 1

        symbol = self.source_code[start_position:self.position]

        if symbol == "t":
            return Token("T", "#t")
        elif symbol == "nil":
            return Token("NIL", "nil")

        return Token("SYMBOL", symbol)

    def _read_boolean(self):
        """Read boolean (only handle #t and #f)"""
        if self.source_code[self.position] == "#":  # #t or #f
            self.position += 1

            if self.position >= len(self.source_code):
                raise Exception("Boolean incomplete")

            char = self.source_code[self.position]

            if char == "t": # #t
                self.position += 1
                if (self.position < len(self.source_code)
                        and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_")):
                    raise Exception(f"Illegal boolean: #t{self.source_code[self.position]}")

                return Token("T", "#t")

            elif char == "f":   # #f
                self.position += 1
                if (self.position < len(self.source_code)
                        and (self.source_code[self.position].isalnum() or self.source_code[self.position] == "_")):
                    raise Exception(f"Illegal boolean: #f{self.source_code[self.position]}")

                return Token("NIL", "nil")

            else:
                raise Exception(f"Unknown boolean: #{char}")

        else:
            raise Exception(f"Unknown boolean: {self.source_code[self.position]}")

    def _read_dot(self):
        """Read DOT (.)"""
        self.position += 1

        return Token("DOT", ".")

    def _read_quote(self):
        """Read quote"""
        self.position += 1

        return Token("QUOTE", "quote")

    def _read_paren(self):
        """Read parenthesis"""
        char = self.source_code[self.position]
        self.position += 1

        if char == "(":
            return Token("LEFT_PAREN", "(")
        else:
            return Token("RIGHT_PAREN", ")")
        
        
import sys
        
def main():
    """Lexer REPL & batch input handling"""
    if sys.stdin.isatty():
        print("Welcome to OurScheme Lexer!")
        while True:
            try:
                s_exp = input("> ")
                if s_exp.lower() in ("exit", "quit"):
                    break

                lexer = Lexer(s_exp)

                token = lexer.next_token()
                while token.type != "EOF":
                    print(token)
                    token = lexer.next_token()

            except Exception as e:
                print("Error:", e)

        print("> ")
        print("Thanks for using OurScheme!")
    else:
        source_code = sys.stdin.read().strip()
        lexer = Lexer(source_code)

        while lexer.has_more_token():
            try:
                token = lexer.next_token()
                print(token)
            except Exception as e:
                print("Error:", e)
                break

if __name__ == "__main__":
    main()