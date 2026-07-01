from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    EOF = "eof"
    CHARACTER = "character"
    # Character classes
    DIGIT_CLASS = "digit class"
    WORD_CLASS = "word class"
    # Anchors
    CARET = "caret"
    DOLLAR = "dollar"
    # Quantifiers
    PLUS = "plus"
    QUESTION = "question"
    ASTERISK = "asterisk"
    LEFT_BRACE = "left brace"
    RIGHT_BRACE = "right brace"
    COMMA = "comma"
    # Ranges
    LEFT_BRACKET = "left bracket"
    RIGHT_BRACKET = "right bracket"
    DASH = "dash"
    DOT = "dot"
    PIPE = "pipe"
    # Groupings
    LEFT_PARENTHESIS = "left parenthesis"
    RIGHT_PARENTHESIS = "right parenthesis"
    BACK_REFERENCE = "back reference"


type TokenValue = str | int | None


@dataclass(frozen=True)
class Token:
    token_type: TokenType
    lexeme: str
    literal: TokenValue
    position: int

    @classmethod
    def eof(cls, position: int) -> "Token":
        return cls(TokenType.EOF, "", None, position)

    @classmethod
    def character(cls, character: str, position: int) -> "Token":
        return cls(TokenType.CHARACTER, character, character, position)

    @classmethod
    def digit_class(cls, position: int) -> "Token":
        return cls(TokenType.DIGIT_CLASS, r"\d", None, position)

    @classmethod
    def word_class(cls, position: int) -> "Token":
        return cls(TokenType.WORD_CLASS, r"\w", None, position)

    @classmethod
    def caret(cls, position: int) -> "Token":
        return cls(TokenType.CARET, "^", None, position)

    @classmethod
    def dollar(cls, position: int) -> "Token":
        return cls(TokenType.DOLLAR, "$", None, position)

    @classmethod
    def plus(cls, lexeme: str, position) -> "Token":
        return cls(TokenType.PLUS, lexeme, None, position)

    @classmethod
    def question(cls, lexeme: str, position) -> "Token":
        return cls(TokenType.QUESTION, lexeme, None, position)

    @classmethod
    def asterisk(cls, position: int) -> "Token":
        return cls(TokenType.ASTERISK, "*", None, position)

    @classmethod
    def left_brace(cls, lexeme: str, position: int) -> "Token":
        return cls(TokenType.LEFT_BRACE, lexeme, None, position)

    @classmethod
    def right_brace(cls, lexeme: str, position: int) -> "Token":
        return cls(TokenType.RIGHT_BRACE, lexeme, None, position)

    @classmethod
    def comma(cls, position: int) -> "Token":
        return cls(TokenType.COMMA, ",", None, position)

    @classmethod
    def dot(cls, position: int) -> "Token":
        return cls(TokenType.DOT, ".", None, position)

    @classmethod
    def dash(cls, position: int) -> "Token":
        return cls(TokenType.DASH, "-", None, position)

    @classmethod
    def left_bracket(cls, position: int) -> "Token":
        return cls(TokenType.LEFT_BRACKET, "[", None, position)

    @classmethod
    def right_bracket(cls, position: int) -> "Token":
        return cls(TokenType.RIGHT_BRACKET, "]", None, position)

    @classmethod
    def pipe(cls, lexeme: str, position: int) -> "Token":
        return cls(TokenType.PIPE, lexeme, None, position)

    @classmethod
    def left_parenthesis(cls, lexeme: str, position: int) -> "Token":
        return cls(TokenType.LEFT_PARENTHESIS, lexeme, None, position)

    @classmethod
    def right_parenthesis(cls, lexeme: str, position: int) -> "Token":
        return cls(TokenType.RIGHT_PARENTHESIS, lexeme, None, position)

    @classmethod
    def back_reference(cls, lexeme: str, literal: int, position: int) -> "Token":
        return cls(TokenType.BACK_REFERENCE, lexeme, literal, position)
