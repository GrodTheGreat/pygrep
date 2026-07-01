from pygrep.tokens import Token, TokenType


def test_eof_token() -> None:
    assert Token.eof(0) == Token(
        token_type=TokenType.EOF,
        lexeme="",
        literal=None,
        position=0,
    )


def test_character_token() -> None:
    assert Token.character("a", 0) == Token(
        token_type=TokenType.CHARACTER,
        lexeme="a",
        literal="a",
        position=0,
    )


def test_digit_class_token() -> None:
    assert Token.digit_class(0) == Token(
        token_type=TokenType.DIGIT_CLASS,
        lexeme=r"\d",
        literal=None,
        position=0,
    )


def test_word_class_token() -> None:
    assert Token.word_class(0) == Token(
        token_type=TokenType.WORD_CLASS,
        lexeme=r"\w",
        literal=None,
        position=0,
    )


def test_caret_token() -> None:
    assert Token.caret(0) == Token(
        token_type=TokenType.CARET,
        lexeme="^",
        literal=None,
        position=0,
    )


def test_dollar_token() -> None:
    assert Token.dollar(0) == Token(
        token_type=TokenType.DOLLAR,
        lexeme="$",
        literal=None,
        position=0,
    )


def test_plus_token() -> None:
    assert Token.plus(r"\+", 0) == Token(TokenType.PLUS, r"\+", None, 0)
    assert Token.plus("+", 0) == Token(TokenType.PLUS, "+", None, 0)


def test_question_token() -> None:
    assert Token.question(r"\?", 0) == Token(TokenType.QUESTION, r"\?", None, 0)
    assert Token.question("?", 0) == Token(TokenType.QUESTION, "?", None, 0)


def test_asterisk_token() -> None:
    assert Token.asterisk(0) == Token(
        token_type=TokenType.ASTERISK,
        lexeme="*",
        literal=None,
        position=0,
    )


def test_left_brace() -> None:
    assert Token.left_brace(r"\[", 0) == Token(
        token_type=TokenType.LEFT_BRACE,
        lexeme=r"\[",
        literal=None,
        position=0,
    )
    assert Token.left_brace("[", 0) == Token(
        token_type=TokenType.LEFT_BRACE,
        lexeme="[",
        literal=None,
        position=0,
    )


def test_right_brace() -> None:
    assert Token.right_brace(r"\]", 0) == Token(
        token_type=TokenType.RIGHT_BRACE,
        lexeme=r"\]",
        literal=None,
        position=0,
    )
    assert Token.right_brace("]", 0) == Token(
        token_type=TokenType.RIGHT_BRACE,
        lexeme="]",
        literal=None,
        position=0,
    )


def test_comma_token() -> None:
    assert Token.comma(0) == Token(
        token_type=TokenType.COMMA,
        lexeme=",",
        literal=None,
        position=0,
    )


def test_left_bracket_token() -> None:
    assert Token.left_bracket(0) == Token(
        token_type=TokenType.LEFT_BRACKET,
        lexeme="[",
        literal=None,
        position=0,
    )


def test_right_bracket_token() -> None:
    assert Token.right_bracket(0) == Token(
        token_type=TokenType.RIGHT_BRACKET,
        lexeme="]",
        literal=None,
        position=0,
    )


def test_dash_token() -> None:
    assert Token.dash(0) == Token(
        token_type=TokenType.DASH,
        lexeme="-",
        literal=None,
        position=0,
    )


def test_dot_token() -> None:
    assert Token.dot(0) == Token(
        token_type=TokenType.DOT,
        lexeme=".",
        literal=None,
        position=0,
    )


def test_pipe_token() -> None:
    assert Token.pipe(r"\|", 0) == Token(
        TokenType.PIPE,
        lexeme=r"\|",
        literal=None,
        position=0,
    )
    assert Token.pipe("|", 0) == Token(
        TokenType.PIPE,
        lexeme="|",
        literal=None,
        position=0,
    )


def test_left_parenthesis_token() -> None:
    assert Token.left_parenthesis(r"\(", 0) == Token(
        TokenType.LEFT_PARENTHESIS,
        lexeme=r"\(",
        literal=None,
        position=0,
    )
    assert Token.left_parenthesis("(", 0) == Token(
        TokenType.LEFT_PARENTHESIS,
        lexeme="(",
        literal=None,
        position=0,
    )


def test_right_parenthesis_token() -> None:
    assert Token.right_parenthesis(r"\)", 0) == Token(
        TokenType.RIGHT_PARENTHESIS,
        lexeme=r"\)",
        literal=None,
        position=0,
    )
    assert Token.right_parenthesis(")", 0) == Token(
        TokenType.RIGHT_PARENTHESIS,
        lexeme=")",
        literal=None,
        position=0,
    )


def test_back_reference_token() -> None:
    assert Token.back_reference("\1", 1, 0) == Token(
        token_type=TokenType.BACK_REFERENCE,
        lexeme="\1",
        literal=1,
        position=0,
    )
