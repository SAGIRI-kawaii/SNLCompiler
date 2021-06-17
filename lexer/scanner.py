from enum import Enum
from typing import Union
from loguru import logger
from prettytable import PrettyTable

from lexer.utils import *
from lexer.Token import *


class State(Enum):
    Normal = "normal"
    InId = "in_id"
    InNum = "in_num"
    InComment = "in_comment"
    InChar = "in_char"
    Error = "error"
    InAssign = "in_assign"
    InRange = "in_range",
    InDot = "in_dot"


class LexerResult:
    token_list: list = []
    errors: list = []

    def get_errors(self) -> list:
        return self.errors

    def set_errors(self, errors: list) -> None:
        self.errors = errors

    def get_token_list(self) -> list:
        return self.token_list

    def set_token_list(self, token_list: list) -> None:
        self.token_list = token_list


class Lexer:
    get_me_first: str = None
    line: int = 1
    column: int = 0
    errors: list = []
    fp: list = []
    fp_index: int = -1

    @staticmethod
    def is_blank(char: str) -> bool:
        return char in ('', ' ', '\r', '\n')

    def get_char(self) -> Union[None, str]:
        if self.get_me_first and not self.is_blank(self.get_me_first):
            ch = self.get_me_first
            self.get_me_first = ''
        else:
            if self.fp_index < len(self.fp) - 1:
                self.fp_index += 1
                ch = self.fp[self.fp_index]
            else:
                ch = None
        if ch == '\n':
            self.column = 0
            self.line += 1
        elif ch is not None:
            self.column += 1
        if ch == '\r':
            self.column -= 1
        return ch

    def get_result(self, fp: list) -> LexerResult:
        token_list: list = []
        errors: list = []
        result: LexerResult = LexerResult()
        if not fp:
            errors.append("Input must not be not null.")
            result.set_errors(errors)
            result.set_token_list(token_list)
            return result
        else:
            self.fp = fp
            token = self.get_token()
            while token:
                token_list.append(token)
                token = self.get_token()
            result.set_token_list(token_list)
            result.set_errors(self.errors)
            for error in errors:
                logger.warning(error)
            return result

    def get_token(self) -> Union[None, Token]:
        state = State.Normal
        # logger.info("get_token()")
        string = ""
        char = self.get_char()
        while char:
            string += char
            if state == State.Normal:
                # logger.info("state: Normal")
                if isalpha(char):
                    state = State.InId
                elif isdigit(char):
                    state = State.InNum
                elif char in (' ', '\t', '\n', '\r'):
                    string = string[:-1]
                    state = State.Normal
                elif char == '+':
                    token = Token.by_data(self.line, self.column, TokenType.PLUS, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '-':
                    token = Token.by_data(self.line, self.column, TokenType.MINUS, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '*':
                    token = Token.by_data(self.line, self.column, TokenType.TIMES, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '/':
                    token = Token.by_data(self.line, self.column, TokenType.OVER, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '(':
                    token = Token.by_data(self.line, self.column, TokenType.LPAREN, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == ')':
                    token = Token.by_data(self.line, self.column, TokenType.RPAREN, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '[':
                    token = Token.by_data(self.line, self.column, TokenType.LMIDPAREN, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == ']':
                    token = Token.by_data(self.line, self.column, TokenType.RMIDPAREN, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == ';':
                    token = Token.by_data(self.line, self.column, TokenType.SEMI, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == ',':
                    token = Token.by_data(self.line, self.column, TokenType.COMMA, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '=':
                    token = Token.by_data(self.line, self.column, TokenType.EQ, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '<':
                    token = Token.by_data(self.line, self.column, TokenType.LT, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '>':
                    token = Token.by_data(self.line, self.column, TokenType.RT, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == ':':
                    state = State.InAssign
                elif char == '{':
                    string = string[:-1]
                    state = State.InComment
                elif char == '.':
                    state = State.InDot
                elif char == '\'':
                    string = string[:-1]
                    state = State.InChar
                else:
                    logger.error(f"Unexpected char: {char}")
                    state = State.Error
            elif state == State.InId:
                # logger.info("state: InId")
                if isalnum(char):
                    state = State.InId
                else:
                    # logger.info(f"当前字符已经不属于标识符组成了:{char}")
                    self.unget_char(char)
                    token = Token.by_data(self.line, self.column, TokenType.ID, string[:-1])
                    token.check_key_words()
                    logger.success(f"get token:{token.to_string()}")
                    return token
            elif state == State.InNum:
                # logger.info("state: InNum")
                if not isdigit(char):
                    self.unget_char(char)
                    token = Token.by_data(self.line, self.column, TokenType.INTC, string[:-1])
                    logger.success(f"get token:{token.to_string()}")
                    return token
            elif state == State.InAssign:
                # logger.info("state: InAssign")
                if char == '=':
                    token = Token.by_data(self.line, self.column, TokenType.ASSIGN, string)
                    logger.success(f"get token:{token.to_string()}")
                    return token
                else:
                    state = State.Error
            elif state == State.InComment:
                # logger.info("state: InComment")
                string = string[:-1]
                while char != '' and char != '}':
                    char = self.get_char()
                state = State.Normal
                if char != '}':
                    logger.error("Expected comment terminator '{' not found")
                    state = State.Error
            elif state == State.InDot:
                # logger.info("state: InDot")
                if isalpha(char):
                    self.unget_char(char)
                    token = Token.by_data(self.line, self.column, TokenType.DOT, string[:-1])
                    logger.success(f"get token:{token.to_string()}")
                    return token
                elif char == '.':
                    state = State.InRange
                    char = self.get_char()
                    continue
                while self.is_blank(char):
                    char = self.get_char()
                if not char:
                    token = Token.by_data(self.line, self.column, TokenType.EOF, '.')
                    logger.success(f"get token:{token.to_string()}")
                    return token
                logger.error("Wrong dot(.)")
                self.unget_char(char)
                state = State.Error
            elif state == State.InRange:
                # logger.info("state: InRange")
                if isdigit(char):
                    self.unget_char(char)
                    token = Token.by_data(self.line, self.column, TokenType.UNDERRANGE, string[:-1])
                    logger.success(f"get token:{token.to_string()}")
                    return token
                state = State.Error
            elif state == State.InChar:
                # logger.info("state: InChar")
                if isalnum(char):
                    char = self.get_char()
                    if char == '\'':
                        token = Token.by_data(self.line, self.column, TokenType.CHARACTER, string[:-1])
                        logger.success(f"get token:{token.to_string()}")
                        return token
                state = State.Error
            elif state == State.Error:
                logger.warning(f"[Error] Unrecognized token. near {self.line}:{self.column}")
                self.errors.append(f"[Error] Unrecognized token. near {self.line}:{self.column}")
                token = Token.by_no_data()
                return token
            else:
                state = state.Error
            char = self.get_char()
        if state == State.InDot:
            token = Token.by_data(self.line, self.column, TokenType.EOF, '.')
            logger.success(f"get token:{token.to_string()}")
            return token
        elif state != State.Normal:
            self.errors.append(f"错误在 {self.line}:{self.column}")
        return None

    def unget_char(self, char: str):
        self.get_me_first = char
        if self.column != 0:
            self.column -= 1


def main():
    with open("demo2.txt", "r", encoding="utf-8") as r:
        fp = list(r.read())
    # print(''.join(fp))
    lexer = Lexer()
    # try:
    result = lexer.get_result(fp)
    if not result.get_errors():
        token_list = result.get_token_list()
        if token_list:
            table = PrettyTable(field_names=["行", "列", "语义信息", "词法信息"])
            for token in token_list:
                table.add_row([token.line, token.column, token.value, token.token_type.value])
            print(table)
    else:
        print("分析错误\n")
        for error in result.get_errors():
            print(error)
    # except Exception as e:
    #     print(e)
