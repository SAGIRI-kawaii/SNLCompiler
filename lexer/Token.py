from typing import Optional

from lexer.TokenType import TokenType


class Token:
    line: int = 0
    column: int = 0
    token_type: TokenType
    value: str = None

    def __init__(self, line: int, column: int, token_type: TokenType, value: str):
        self.line = line
        self.column = column
        self.token_type = token_type
        self.value = value

    @classmethod
    def by_no_data(cls):
        return cls(0, 0, TokenType.EMPTY, "")

    @classmethod
    def by_value(cls, value):
        return cls(0, 0, TokenType.EMPTY, value)

    @classmethod
    def by_type(cls, token_type: TokenType):
        return cls(0, 0, token_type, token_type.value)

    @classmethod
    def by_data(cls, line: int, column: int, token_type: TokenType, value: str):
        return cls(line, column, token_type, value)

    def check_key_words(self):
        if self.token_type == TokenType.ID:
            if self.value == TokenType.PROGRAM.value:
                self.token_type = TokenType.PROGRAM
            elif self.value == TokenType.PROCEDURE.value:
                self.token_type = TokenType.PROCEDURE
            elif self.value == TokenType.TYPE.value:
                self.token_type = TokenType.TYPE
            elif self.value == TokenType.VAR.value:
                self.token_type = TokenType.VAR
            elif self.value == TokenType.IF.value:
                self.token_type = TokenType.IF
            elif self.value == TokenType.THEN.value:
                self.token_type = TokenType.THEN
            elif self.value == TokenType.ELSE.value:
                self.token_type = TokenType.ELSE
            elif self.value == TokenType.FI.value:
                self.token_type = TokenType.FI
            elif self.value == TokenType.WHILE.value:
                self.token_type = TokenType.WHILE
            elif self.value == TokenType.DO.value:
                self.token_type = TokenType.DO
            elif self.value == TokenType.ENDWH.value:
                self.token_type = TokenType.ENDWH
            elif self.value == TokenType.BEGIN.value:
                self.token_type = TokenType.BEGIN
            elif self.value == TokenType.END.value:
                self.token_type = TokenType.END
            elif self.value == TokenType.READ.value:
                self.token_type = TokenType.READ
            elif self.value == TokenType.WRITE.value:
                self.token_type = TokenType.WRITE
            elif self.value == TokenType.ARRAY.value:
                self.token_type = TokenType.ARRAY
            elif self.value == TokenType.OF.value:
                self.token_type = TokenType.OF
            elif self.value == TokenType.RECORD.value:
                self.token_type = TokenType.RECORD
            elif self.value == TokenType.RETURN.value:
                self.token_type = TokenType.RETURN
            elif self.value == TokenType.CHAR.value:
                self.token_type = TokenType.CHAR
            elif self.value == TokenType.INTEGER.value:
                self.token_type = TokenType.INTEGER
            elif self.value == TokenType.CHARC.value:
                self.token_type = TokenType.CHARC

    def to_string(self):
        return f"{self.value}|{self.token_type}|{self.line}:{self.column}"

    def get_line(self) -> int:
        return self.line

    def get_column(self) -> int:
        return self.column

    def get_token_type(self) -> TokenType:
        return self.token_type

    def get_value(self) -> str:
        return self.value
