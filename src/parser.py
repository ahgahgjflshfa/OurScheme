from .lexer import *
from .ast_nodes import *

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def parse(self) -> ASTNode:
        """Entry point of parser"""
        return self._parse_s_exp()  # repl

    def _consume_token(self) -> Token:
        token = self.current_token
        self.current_token = self.lexer.next_token()
        return token

    def _current_token(self) -> Token:
        return self.current_token

    def _parse_s_exp(self) -> ASTNode:
        """HI"""
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

        while self._current_token().type not in ("RIGHT_PAREN", "EOF"):
            if self._current_token().type == "DOT":
                self._consume_token()   # skip `.`

                if not elements:
                    raise SyntaxError("Dotted pair must have left value.")

                right = self._parse_s_exp()

                if self._consume_token().type != "RIGHT_PAREN":
                    raise SyntaxError("Dotted pair must ends in right parenthesis.")

                return ConsNode(ListNode(elements), right)

            elements.append(self._parse_s_exp())

        if self._current_token().type == "EOF":
            raise SyntaxError("Unexpected EOF while parsing list.")

        self._consume_token()   # consume right parenthesis
        return ListNode(elements)

    def _parse_quote(self) -> ASTNode:
        if self._current_token().type == "EOF":
            raise SyntaxError("Unexpected EOF after quote.")

        return QuoteNode(self._parse_s_exp())

    def _parse_atom(self, token: Token) -> ASTNode:
        """Parse atom"""
        return AtomNode(token.value)