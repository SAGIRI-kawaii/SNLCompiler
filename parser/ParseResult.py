from parser.SyntaxTree import SyntaxTree


class ParseResult:
    __tree: SyntaxTree
    __errors: list

    def is_success(self) -> bool:
        return self.__errors is None or len(self.__errors) == 0

    def get_tree(self) -> SyntaxTree:
        return self.__tree

    def set_tree(self, tree: SyntaxTree) -> None:
        self.__tree = tree

    def get_errors(self) -> list:
        return self.__errors

    def set_errors(self, errors: list) -> None:
        self.__errors = errors
