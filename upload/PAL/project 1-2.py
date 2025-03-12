class NoClosingQuoteError(Exception):
    def __init__(self, msg_):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class NotFinishError(Exception):
    """讓parser等待多行輸入"""
    def __init__(self, msg_="S expression not complete"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class EmptyInputError(Exception):
    """遇到註解或是整行空白用的"""
    def __init__(self, msg_):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class UnexpectedTokenError(Exception):
    def __init__(self, msg_):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


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

    @property
    def line_count(self):
        return self._line_count

    @property
    def position(self):
        return self._position

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
            return self._read_symbol()

        elif char == "\'":
            return self._read_quote()

        elif char.isalpha():
            return self._read_symbol()

        elif char == "\"":
            return self._read_string()

        elif char in ("+", "-", "*", "/") and self.peek().isspace():   # function symbols
            return self._read_symbol()

        elif char.isdigit() or (char in "+-" and self.peek().isdigit()):   # +100 -5 etc.
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
        token = self.next_token()
        self._position = current_position
        return token

    def _read_string(self):
        """Read string token"""
        self._position += 1  # skip "
        result = ""

        while self._position < len(self.source_code):
            if self.source_code[self._position] == "\"":
                self._position += 1
                return Token("STRING", result)

            else:
                result += self.source_code[self._position]
                self._position += 1

        raise NoClosingQuoteError(f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self._line_count} Column {self._position + 1}")

    def _read_int_or_float(self):
        """Read number token"""
        start_position = self._position
        is_symbol = False

        self._position += 1

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isdigit():
                self._position += 1

            elif char.isalpha():
                is_symbol = True
                self._position += 1

            elif char == ".":
                if is_symbol:
                    self._position += 1

                else:
                    self._position += 1
                    while self._position < len(self.source_code) and self.source_code[self._position].isdigit():
                        self._position += 1

                    return Token("FLOAT", float(self.source_code[start_position:self._position]))

            else:
                break

        if is_symbol:
            return Token("SYMBOL", self.source_code[start_position:self._position])

        else:
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
        elif symbol == "#t":
            return Token("T", "#t")
        elif symbol == "#f":
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
        while self._position < len(self.source_code) and not self.source_code[self._position].isspace():
            self._position += 1

        return Token("UNKNOWN", self.source_code[start:self._position])


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


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    @property
    def current(self) -> Token:
        return self.current_token

    def parse(self) -> list:
        """Entry point of parser"""
        elements = []

        while self.current.type != "EOF":
            elements.append(self._parse_s_exp())  # repl

        return elements

    def _consume_token(self) -> Token:
        token = self.current_token
        self.current_token = self.lexer.next_token()
        return token

    def _parse_s_exp(self) -> ASTNode:
        """Parse a single S-expression"""
        token = self._consume_token()

        if token.type in ("SYMBOL", "INT", "FLOAT", "STRING", "NIL", "T", "UNKNOWN"):
            return self._parse_atom(token)

        elif token.type == "QUOTE":
            return self._parse_quote()

        elif token.type == "LEFT_PAREN":
            return self._parse_list()

        elif token.type == "EOF":
            raise EmptyInputError(f"EOF encountered")

        # else:
        #     raise SyntaxError(f"Unexpected token: {token}")

    def _parse_list(self) -> ASTNode:
        """Parse an S-Expression list"""
        self._consume_token()  # consume `LEFT_PAREN`
        elements = []

        line = len(self.lexer.source_code.split("\n"))
        pos = len(self.lexer.source_code.split("\n")[-1])

        while self.current.type not in ("RIGHT_PAREN", "EOF"):
            if self.current.type == "DOT":
                self._consume_token()  # skip `.`

                if self.current.type == "RIGHT_PAREN":  # `.` 不能沒有右值
                    raise UnexpectedTokenError(
                        f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>)<<"
                    )

                elif self.current.type == "EOF":
                    raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

                right = self._parse_s_exp()

                if self._consume_token().type != "RIGHT_PAREN":
                    raise NotFinishError("Unexpected EOF while parsing list.")

                return ConsNode(elements[0], right) if len(elements) == 1 else ConsNode(ListNode(elements), right)

            elements.append(self._parse_s_exp())

        if self.current.type == "EOF":
            raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

        self._consume_token()  # consume right parenthesis

        if not elements:
            return AtomNode("NIL", "nil")  # `()` 應該回傳 `nil`

        return ListNode(elements)

    def _parse_quote(self) -> ASTNode:
        if self.current.type == "EOF":
            raise SyntaxError("Unexpected EOF after quote.")

        return QuoteNode(self._parse_s_exp())  # Consume and parse quoted expression

    def _parse_atom(self, token: Token) -> ASTNode:
        """Parse atom and preserve type information"""
        if token.type in ("INT", "FLOAT", "SYMBOL", "STRING", "UNKNOWN"):
            return AtomNode(token.type, token.value)

        elif token.type == "T":  # #t
            return AtomNode("BOOLEAN", True)

        elif token.type == "NIL":  # #f
            return AtomNode("BOOLEAN", False)

        raise SyntaxError(f"Unexpected atom type: {token.type}")


def repl():
    lexer = Lexer()
    print("Welcome to OurScheme!")

    partial_input = ""  # 存儲多行輸入
    while True:
        try:
            new_input = input()  # 讀取新的一行
            if new_input.lower() == "(exit)":
                break

            partial_input += new_input + "\n"  # 儲存多行輸入
            lexer.reset(partial_input.rstrip())
            parser = Parser(lexer)

            try:
                results = parser.parse()
                for result in results:
                    if isinstance(result, AtomNode) and result.type == "STRING":
                        print(f'\n> "{result.value}"')
                    elif isinstance(result, ListNode) and not result.elements:
                        print("\n> nil")
                    elif isinstance(result, AtomNode) and result.type == "FLOAT":
                        print(f"\n> {result.value:.3f}")
                    else:
                        print(f"\n> {result}")

                    partial_input = ""  # 解析成功後清空輸入
                    lexer.reset_line_count()

            except NotFinishError as e:
                if "Unexpected EOF" in str(e):
                    continue  # 繼續等待輸入（多行解析）

                # e.g. no closing quote ...
                print(f"\n> {e}")
                partial_input = ""  # 出錯後清空輸入

            except UnexpectedTokenError as e:
                # e.g. no closing quote ...
                print(f"\n> {e}")
                partial_input = ""

            except EmptyInputError as e:
                partial_input = ""

        except NoClosingQuoteError as e:
            print(f"\n> {e}")

    print("Thanks for using OurScheme!")

if __name__ == "__main__":
    n = input()
    repl()
    quit(0)