from enum import Enum


class TokenType(Enum):
    EOF = '.'
    ERROR = "error"
    EMPTY = ''

    # 保留字
    PROGRAM = "program"
    PROCEDURE = "procedure"
    TYPE = "type"
    VAR = "var"
    IF = "if"
    THEN = "then"
    ELSE = "else"
    FI = "fi"
    WHILE = "while"
    DO = "do"
    ENDWH = "endwh"
    BEGIN = "begin"
    END = "end"
    READ = "read"
    WRITE = "write"
    ARRAY = "array"
    OF = "of"
    RECORD = "record"
    RETURN = "return"

    # 类型
    INTEGER = "integer"
    CHAR = "char"
    CHARC = "charc"

    ID = "id"
    INTC = "intc"
    CHARACTER = "character"

    # 特殊符号
    ASSIGN = ":="
    EQ = '='
    LT = '<'
    RT = '>'
    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    OVER = '/'
    LPAREN = '('
    RPAREN = ')'
    LMIDPAREN = '['
    RMIDPAREN = ']'
    UNDERRANGE = ".."
    SEMI = ';'
    COMMA = ','
    DOT = '.'


