from typing import Protocol

from pygrep.tokens import Token, TokenType, TokenValue


class Lexer(Protocol):
    def scan(self) -> list[Token]: ...


class BasicGrammarLexer(Lexer):
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.start = 0
        self.current = 0
        self.tokens: list[Token] = []

    def scan(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token.eof(self.current))
        return self.tokens

    def scan_token(self) -> None:
        character = self.advance()
        match character:
            case "^":
                self.add_token(TokenType.CARET)
            case "$":
                self.add_token(TokenType.DOLLAR)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.DASH)
            case "*":
                self.add_token(TokenType.ASTERISK)
            case ",":
                self.add_token(TokenType.COMMA)
            case "[":
                self.add_token(TokenType.LEFT_BRACKET)
            case "]":
                self.add_token(TokenType.RIGHT_BRACKET)
            case "\\":
                self.scan_escaped()
            case _:
                self.add_token(TokenType.CHARACTER, character)

    def scan_escaped(self) -> None:
        character = self.advance()
        match character:
            case "?":
                self.add_token(TokenType.QUESTION)
            case "+":
                self.add_token(TokenType.PLUS)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case "|":
                self.add_token(TokenType.PIPE)
            case "(":
                self.add_token(TokenType.LEFT_PARENTHESIS)
            case ")":
                self.add_token(TokenType.RIGHT_PARENTHESIS)
            case "d":
                self.add_token(TokenType.DIGIT_CLASS)
            case "w":
                self.add_token(TokenType.WORD_CLASS)
            case _ if is_digit(character):
                num = character
                while is_digit(self.peek()):
                    num += self.advance()
                self.add_token(TokenType.BACK_REFERENCE, int(num))
            case _:
                # TODO: Something better here, maybe an error callback
                raise Exception

    def is_at_end(self) -> bool:
        return self.current >= len(self.pattern)

    def peek(self) -> str:
        if self.is_at_end():
            return ""
        return self.pattern[self.current]

    def add_token(self, token_type: TokenType, literal: TokenValue = None) -> None:
        lexeme = self.pattern[self.start : self.current]
        self.tokens.append(Token(token_type, lexeme, literal, self.start))

    def advance(self) -> str:
        character = self.pattern[self.current]
        self.current += 1
        return character


class ExtendedGrammarLexer(Lexer):
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.start = 0
        self.current = 0
        self.tokens: list[Token] = []

    def scan(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token.eof(self.current))
        return self.tokens

    def scan_token(self) -> None:
        character = self.advance()
        match character:
            case "^":
                self.add_token(TokenType.CARET)
            case "$":
                self.add_token(TokenType.DOLLAR)
            case ".":
                self.add_token(TokenType.DOT)
            case "|":
                self.add_token(TokenType.PIPE)
            case ",":
                self.add_token(TokenType.COMMA)
            case "-":
                self.add_token(TokenType.DASH)
            case "+":
                self.add_token(TokenType.PLUS)
            case "*":
                self.add_token(TokenType.ASTERISK)
            case "?":
                self.add_token(TokenType.QUESTION)
            case "(":
                self.add_token(TokenType.LEFT_PARENTHESIS)
            case ")":
                self.add_token(TokenType.RIGHT_PARENTHESIS)
            case "[":
                self.add_token(TokenType.LEFT_BRACKET)
            case "]":
                self.add_token(TokenType.RIGHT_BRACKET)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "}":
                self.add_token(TokenType.RIGHT_BRACE)
            case "\\":
                self.scan_escaped()
            case _:
                self.add_token(TokenType.CHARACTER, character)

    def scan_escaped(self) -> None:
        character = self.advance()
        match character:
            case "w":
                self.add_token(TokenType.WORD_CLASS)
            case "d":
                self.add_token(TokenType.DIGIT_CLASS)
            case _ if is_digit(character):
                num = character
                while is_digit(self.peek()):
                    num += self.advance()
                self.add_token(TokenType.BACK_REFERENCE, int(num))
            case _:
                # TODO: Something better here, maybe an error callback
                raise Exception

    def is_at_end(self) -> bool:
        return self.current >= len(self.pattern)

    def add_token(self, token_type: TokenType, literal: TokenValue = None) -> None:
        lexeme = self.pattern[self.start : self.current]
        self.tokens.append(Token(token_type, lexeme, literal, self.start))

    def peek(self) -> str:
        if self.current >= len(self.pattern):
            return ""
        return self.pattern[self.current]

    def advance(self) -> str:
        character = self.pattern[self.current]
        self.current += 1
        return character


def is_digit(character: str) -> bool:
    return "0" <= character <= "9"
