from typing import Union
from loguru import logger
from abc import ABC, abstractmethod

from parser.TreeNode import TreeNode
from lexer.Token import Token, TokenType
from parser.ParseResult import ParseResult
from lexer.scanner import Lexer, LexerResult


class SyntexParser(ABC):
    __error_token: Token = Token.by_type(TokenType.ERROR)
    __current_token_index: int = 0
    _token_list: list = []
    _last_read: Token = __error_token
    _errors: list = []

    @abstractmethod
    def parse_token_list(self, token_list: list) -> ParseResult: ...

    def parse(self, fp: list) -> ParseResult:
        self._errors = []
        result = ParseResult()
        laxer = Lexer()
        try:
            laxer_result = laxer.get_result(fp)
            if not laxer_result.get_errors():
                self._token_list = laxer_result.get_token_list()
            else:
                self._errors.append("Laxer Error")
                self._errors += laxer_result.get_errors()
                result.set_errors(self._errors)
                return result
        except Exception as e:
            self._errors.append(str(e))
            result.set_errors(self._errors)
            return result
        return self.parse_token_list(self._token_list)

    def _get_token(self) -> Union[Token, None]:
        token = None
        if self.__current_token_index < len(self._token_list):
            token = self._token_list[self.__current_token_index]
            self.__current_token_index += 1
            logger.info(f"get next token = {token.to_string()}")
            self._last_read = token
        else:
            logger.info("EOF")
        return token

    def _peek_token(self) -> Token:
        token = self.__error_token
        if self.__current_token_index < len(self._token_list):
            token = self._token_list[self.__current_token_index]
        return token

    @staticmethod
    def _node(value: str):
        return TreeNode.by_value(value)

    @staticmethod
    def _node_null():
        return TreeNode.by_value("ɛ")

    @logger.catch
    def _match(self, expected: TokenType) -> TreeNode:
        input = self._get_token()
        node = self._node_null()
        # logger.error(input.to_string())
        if input:
            token_type = input.get_token_type()
            if token_type == expected:
                logger.info(f"match {input.to_string()}")
                if token_type in (TokenType.ID, TokenType.INTC, TokenType.CHARACTER):
                    node = self._node(input.get_value())
                logger.info(f"node.value = {node.get_value()}")
            else:
                # self._errors.append(f"Unexpected token near `{input.get_value()}`. `{expected.value}` expected. at [{input.get_line()}:{input.get_column()}]")
                self._errors.append(f"Unexpected token near `{input.get_value()}`. at [{input.get_line()}]")
                # logger.error(f"Unexpected token near `{input.get_value()}`. `{expected.value}` expected. at [{input.get_line()}:{input.get_column()}]")
                logger.error(f"Unexpected token near `{input.get_value()}`. at [{input.get_line()}]")
        else:
            self._errors.append("Unexpected EOF. No more tokens at input stream.")
            raise ValueError(f"{expected.value} EOF")
        return node

    @logger.catch
    def error(self, *token_types: TokenType):
        logger.error(f"匹配错误{self._peek_token().to_string()}")
        string = ""
        for token in token_types:
            string += f"{token.value}|"
        string += f" expected. at [{self._last_read.get_line()}]"
        # :{self._last_read.get_column()}
        self._errors.append(string)
        raise ValueError("匹配错误")
