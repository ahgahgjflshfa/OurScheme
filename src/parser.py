from .lexer import *
from .ast_nodes import *

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    @property
    def current(self) -> Token:
        return self.current_token

    def parse(self) -> ASTNode:
        """Entry point of parser"""
        return self._parse_s_exp()  # repl

    def _consume_token(self) -> Token:
        token = self.current_token
        self.current_token = self.lexer.next_token()
        return token

    def _parse_s_exp(self) -> ASTNode:
        """Parse a single S-expression"""
        token = self._consume_token()

        if token.type in ("SYMBOL", "INT", "FLOAT", "STRING", "NIL", "T"):
            return self._parse_atom(token)

        elif token.type == "QUOTE":
            return self._parse_quote()

        elif token.type == "LEFT_PAREN":
            return self._parse_list()

        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def _parse_list(self) -> ASTNode:
        elements = []

        while self.current.type not in ("RIGHT_PAREN", "EOF"):
            if self.current.type == "DOT":
                self._consume_token()  # skip `.`

                if not elements:
                    raise SyntaxError("Dotted pair must have left value.")

                right = self._parse_s_exp()

                if self._consume_token().type != "RIGHT_PAREN":
                    raise SyntaxError("Dotted pair must end with right parenthesis.")

                return ConsNode(elements[0], right) if len(elements) == 1 else ConsNode(ListNode(elements), right)

            elements.append(self._parse_s_exp())

        if self.current.type == "EOF":
            raise SyntaxError("Unexpected EOF while parsing list.")

        self._consume_token()  # consume right parenthesis
        return ListNode(elements)

    def _parse_quote(self) -> ASTNode:
        if self.current.type == "EOF":
            raise SyntaxError("Unexpected EOF after quote.")

        return QuoteNode(self._parse_s_exp())  # Consume and parse quoted expression

    def _parse_atom(self, token: Token) -> ASTNode:
        """Parse atom and preserve type information"""
        if token.type in ("INT", "FLOAT", "SYMBOL", "STRING"):
            return AtomNode(token.type, token.value)

        elif token.type == "T":  # #t
            return AtomNode("BOOLEAN", True)

        elif token.type == "NIL":  # #f
            return AtomNode("BOOLEAN", False)

        raise SyntaxError(f"Unexpected atom type: {token.type}")