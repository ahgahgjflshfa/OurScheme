from src.ast_nodes import *


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
