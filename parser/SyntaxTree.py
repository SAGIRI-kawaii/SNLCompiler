from typing import Union

from parser.TreeNode import TreeNode


class SyntaxTree:
    __root: TreeNode

    def __init__(self, root: Union[TreeNode, None]):
        self.__root = root

    @classmethod
    def by_no_data(cls):
        return cls(None)

    def get_root(self) -> TreeNode:
        return self.__root

    def set_root(self, root: TreeNode) -> None:
        self.__root = root

    @staticmethod
    def __is_child_of(node: TreeNode, parent: TreeNode) -> bool:
        if not parent:
            return False
        if parent.get_children():
            for n in parent.get_children():
                if n == node:
                    return True
        return False
