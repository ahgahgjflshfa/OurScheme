from mpmath import convert
from sqlalchemy.sql.base import elements


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

    @property
    def position(self):
        return self._position

    def reset(self, new_source_code):
        """Reset lexer status, let it tokenize new source code"""
        self.source_code = new_source_code # + "\n"
        self._position = 0

    def next_token(self):
        """Return next token from source code"""
        self._skip_whitespace_and_comments()

        if self._position >= len(self.source_code):
            return Token("EOF", None)

        char = self.source_code[self._position]
        if char in "()":
            return self._read_paren()

        elif char == ".":
            if self.peek().isdigit():
                return self._read_int_or_float()
            else:
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
        line = len(self.source_code.split("\n"))
        pos = len(self.source_code.split("\n")[-1])

        while self._position < len(self.source_code):
            if self.source_code[self._position] == "\"":
                self._position += 1
                return Token("STRING", result)

            else:
                result += self.source_code[self._position]
                self._position += 1

        raise NoClosingQuoteError(f"ERROR (no closing quote) : END-OF-LINE encountered at Line {line} Column {pos+1}")

    def _read_int_or_float(self):
        """Read number token or symbol starting with a number"""
        start_position = self._position
        has_dot = False  # 是否有小數點
        is_symbol = False  # 是否應該被解析為符號

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isdigit():  # **如果是數字，繼續讀取**
                self._position += 1

            elif char in ("+", "-"):  # **允許開頭有 `+` 或 `-`**
                if self._position != start_position:  # `+` 或 `-` 只能出現在開頭
                    is_symbol = True
                self._position += 1

            elif char == ".":
                if has_dot:  # **如果已經有 `.`，則不允許第二個 `.`
                    is_symbol = True
                has_dot = True
                self._position += 1

                # **如果 `.` 是輸入的最後一個字符 (e.g., `3.`)，則應該視為 `FLOAT`**
                if self._position >= len(self.source_code) or not self.source_code[self._position].isdigit():
                    break  # **允許 `3.` 解析為 `FLOAT(3.0)`**

            elif char.isalpha():  # **數字後面如果有字母，則應該是 `SYMBOL`**
                is_symbol = True
                self._position += 1

            else:
                break  # **遇到非數字、字母、符號，停止解析**

        number_str = self.source_code[start_position:self._position]

        if is_symbol:
            return Token("SYMBOL", number_str)  # **如果包含字母或 `.` 解析錯誤，則為 Symbol**
        elif has_dot:
            return Token("FLOAT", float(number_str))  # **解析為 Float**
        else:
            return Token("INT", int(number_str))  # **解析為 Int**

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
        self._current_token = self.lexer.next_token()
        self._processed_length = 0      # 記錄當前 Token 之前的輸入長度
        self._prev_s_exp_end_pos = 0    # 紀錄上一個 S-Expression 結束的位置

        if self._current_token.type == "EOF":   # supposedly only empty line or a line starting with comment will encounter
            raise EmptyInputError(f"EOF encountered")

    @property
    def current(self):
        return self._current_token

    def parse(self):
        """Entry point of parser"""
        self._prev_s_exp_end_pos = self._processed_length  # 更新上一個 S-Expression 的結束位置
        return self._parse_s_exp()

    def _consume_token(self) -> Token:
        token = self._current_token
        self._processed_length = self.lexer.position    # 記錄 current token **之前** 的輸入長度
        self._current_token = self.lexer.next_token()
        return token

    def _get_error_position(self):
        """計算錯誤 Token 的 Line 和 Column"""
        line_number = 1

        column_number = self._processed_length - self._prev_s_exp_end_pos

        return line_number, column_number

    def _parse_s_exp(self) -> ASTNode | None:
        """Parse a single S-expression"""
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
            line, pos = self._get_error_position()

            raise UnexpectedTokenError(f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>.<<")

        elif token.type == "RIGHT_PAREN":
            line, pos = self._get_error_position()

            raise UnexpectedTokenError(f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>)<<")

    def _parse_list(self) -> ASTNode:
        """Parse an S-Expression list"""
        elements = []

        while self._current_token.type not in ("RIGHT_PAREN", "EOF"):
            if self._current_token.type == "DOT":   # if dot encounter, should be a cons node
                if not elements:
                    line = len(self.lexer.source_code.split("\n"))
                    pos = self.lexer.source_code.split("\n")[-1].index(".")

                    raise UnexpectedTokenError(
                        f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos+1} is >>.<<"
                    )

                self._consume_token()  # skip `.`

                if self._current_token.type == "RIGHT_PAREN":  # `.` 不能沒有右值
                    line = len(self.lexer.source_code.split("\n"))
                    pos = self.lexer.source_code.split("\n")[-1].index(")")

                    raise UnexpectedTokenError(
                        f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos+1} is >>)<<"
                    )

                elif self._current_token.type == "EOF":
                    # Note: because the expression is not finish, input length shouldn't be reset yet
                    raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

                cdr = self._parse_s_exp()

                if self._consume_token().type != "RIGHT_PAREN":
                    line, pos = self._get_error_position()

                    raise UnexpectedTokenError(f"ERROR (unexpected token) : ')' expected when token at Line {line} Column {pos} is >>.<<")

                if len(elements) == 1:
                    return ConsNode(elements[0], cdr)

                if any(isinstance(e, ListNode) for e in elements):
                    return ConsNode(ListNode(elements), cdr)

                return self._convert_to_cons(elements, cdr)

            elements.append(self._parse_s_exp())

        if self._current_token.type == "EOF":
            raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

        self._consume_token()  # consume right parenthesis

        return ListNode(elements)

    def _convert_to_cons(self, elements, cdr):
        result = cdr
        for elem in elements[::-1]:
            result = ConsNode(elem, result)

        return result

    def _parse_quote(self) -> ASTNode:
        if self._current_token.type == "EOF":
            raise SyntaxError("Unexpected EOF after quote.")

        return QuoteNode(self._parse_s_exp())  # Consume and parse quoted expression

    def _parse_atom(self, token: Token) -> ASTNode:
        """Parse atom and preserve type information"""
        if token.type in ("INT", "FLOAT", "SYMBOL", "STRING", "UNKNOWN"):
            return AtomNode(token.type, token.value)

        elif token.type == "T":  # #t
            return AtomNode("BOOLEAN", "#t")

        elif token.type == "NIL":  # #f
            return AtomNode("BOOLEAN", "nil")

        raise SyntaxError(f"Unexpected atom type: {token.type}")


def pretty_print(node, indent=0):
    """格式化 Pretty Print 輸出 Scheme AST，確保排版嚴格符合要求"""
    indent_str = "  " * indent  # 當前縮排
    next_indent_str = "  " * (indent + 1)  # 下一層縮排

    if isinstance(node, AtomNode):
        """處理基本類型 (數字、布林值、符號、字串)"""
        if node.type == "STRING":
            return f'"{node.value}"'
        elif node.type == "FLOAT":
            return f"{node.value:.3f}"
        else:
            return f"{node.value}"

    elif isinstance(node, ListNode):
        """處理 ListNode，確保 `(` 與第一個元素同一行，並且控制 `(` 之間的空格數量"""
        if not node.elements:
            return "nil"

        result = f"( "  # `(` 與 list 中的第一個元素應該有一格空格的距離

        result += f"{pretty_print(node.elements[0], indent + 1)}"

        # 處理剩下的元素，每個元素(不管是 atom、list、cons 還是 quote)，都是每一個元素自己一行
        for element in node.elements[1:]:
            # 剩餘每個元素都是固定的 indent ，所以需要用到 next_indent_str 來縮排
            result += f"\n{next_indent_str}{pretty_print(element, indent + 1)}"

        result += f"\n{indent_str})"
        return result

    elif isinstance(node, ConsNode):
        elements = []
        current = node

        while isinstance(current, ConsNode):
            elements.append(current.car)
            current = current.cdr

        # 如果 `cdr` 最終是 `nil`，則轉換成 ListNode 格式
        if isinstance(current, AtomNode) and current.value == "nil":
            return pretty_print(ListNode(elements), indent)

        # 否則，按照 `ConsNode` 標準格式輸出
        result = f"{indent_str}( {pretty_print(node.car, indent + 1)}"

        # `.` 必須獨立一行
        result += f"\n{next_indent_str}."

        # `cdr` 部分處理
        result += f"\n{next_indent_str}{pretty_print(node.cdr, indent + 1)}"
        result += f"\n)"
        return result


    elif isinstance(node, QuoteNode):
        """處理 `quote` 內部的 ListNode，確保 `(` 與 `quote` 的 `q` 對齊"""
        result = f"{indent_str}( quote"

        result += f"\n{next_indent_str}{pretty_print(node.value, indent + 1)}"

        result += f"\n{indent_str})"
        return result

    return f"{indent_str}UNKNOWN_NODE"


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
            lexer.reset(partial_input.rstrip("\n"))
            parser = Parser(lexer)

            try:
                while parser.current.type != "EOF":
                    result = parser.parse()

                    # 檢查 `(exit)` 是否是獨立的 S-Expression
                    if isinstance(result, ListNode) and len(result.elements) == 1:
                        if isinstance(result.elements[0], AtomNode) and result.elements[0].value == "exit":
                            print("\n> \nThanks for using OurScheme!")
                            return

                    print("\n> " + pretty_print(result).lstrip("\n"))

                partial_input = ""  # 解析成功後清空輸入

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

        except EmptyInputError:
            continue

        except NoClosingQuoteError as e:
            print(f"\n> {e}")
            partial_input = ""

        except EOFError:
            print("\n> ERROR (no more input) : END-OF-FILE encountered")
            break

    print("Thanks for using OurScheme!")

if __name__ == "__main__":
    n = input()
    repl()
    quit(0)
