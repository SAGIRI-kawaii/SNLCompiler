from typing import Union


class TreeNode:
    __children: Union[None, list]
    __value: str
    __width: int

    def __init__(self, children: Union[None, list], value: str):
        self.__children = children
        self.set_value(value)

    @classmethod
    def by_value(cls, value: str):
        return cls(None, value)

    def has_child(self) -> bool:
        for node in self.__children:
            if node and not node:
                return True
        return False

    def get_children(self) -> Union[None, list]:
        return self.__children

    def set_children(self, *nodes) -> None:
        self.__children = list(nodes)

    def get_value(self) -> str:
        return self.__value

    def set_value(self, value: str) -> None:
        self.__value = value
        self.__width = len(value)

    def get_width(self) -> int:
        return self.__width

    def to_string(self) -> str:
        return f"[TreeNode value={self.__value}]"
