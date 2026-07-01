from pygrep.tokens import Token
from src.pygrep.lexer import BasicGrammarLexer, ExtendedGrammarLexer


def basic_lexer(pattern: str) -> list[Token]:
    return BasicGrammarLexer(pattern).scan()


def extended_lexer(pattern: str) -> list[Token]:
    return ExtendedGrammarLexer(pattern).scan()


class TestBasicLexer:
    def test_basic_lexer_no_pattern(self) -> None:
        assert basic_lexer("") == [Token.eof(0)]

    def test_basic_lexer_literal_characters(self) -> None:
        assert basic_lexer("abc") == [
            Token.character("a", 0),
            Token.character("b", 1),
            Token.character("c", 2),
            Token.eof(3),
        ]
        assert basic_lexer("123") == [
            Token.character("1", 0),
            Token.character("2", 1),
            Token.character("3", 2),
            Token.eof(3),
        ]

    # In BRE, unescaped + ? | ( ) { } are plain literals.
    def test_basic_lexer_unescaped_metacharacters_are_literals(self) -> None:
        assert basic_lexer("+") == [Token.character("+", 0), Token.eof(1)]
        assert basic_lexer("?") == [Token.character("?", 0), Token.eof(1)]
        assert basic_lexer("|") == [Token.character("|", 0), Token.eof(1)]
        assert basic_lexer("(") == [Token.character("(", 0), Token.eof(1)]
        assert basic_lexer(")") == [Token.character(")", 0), Token.eof(1)]
        assert basic_lexer("{") == [Token.character("{", 0), Token.eof(1)]
        assert basic_lexer("}") == [Token.character("}", 0), Token.eof(1)]

    def test_basic_lexer_digit_character_class(self) -> None:
        assert basic_lexer(r"\d") == [Token.digit_class(0), Token.eof(2)]
        assert basic_lexer(r"\d\d\d") == [
            Token.digit_class(0),
            Token.digit_class(2),
            Token.digit_class(4),
            Token.eof(6),
        ]

    def test_basic_lexer_word_character_class(self) -> None:
        assert basic_lexer(r"\w") == [Token.word_class(0), Token.eof(2)]
        assert basic_lexer(r"\w\w\w") == [
            Token.word_class(0),
            Token.word_class(2),
            Token.word_class(4),
            Token.eof(6),
        ]

    def test_basic_lexer_positive_character_group(self) -> None:
        assert basic_lexer("[abc]") == [
            Token.left_bracket(0),
            Token.character("a", 1),
            Token.character("b", 2),
            Token.character("c", 3),
            Token.right_bracket(4),
            Token.eof(5),
        ]
        assert basic_lexer("[123]") == [
            Token.left_bracket(0),
            Token.character("1", 1),
            Token.character("2", 2),
            Token.character("3", 3),
            Token.right_bracket(4),
            Token.eof(5),
        ]

    def test_basic_lexer_negative_character_group(self) -> None:
        assert basic_lexer("[^abc]") == [
            Token.left_bracket(0),
            Token.caret(1),
            Token.character("a", 2),
            Token.character("b", 3),
            Token.character("c", 4),
            Token.right_bracket(5),
            Token.eof(6),
        ]

    def test_basic_lexer_combining_character_class(self) -> None:
        assert basic_lexer(r"\d apple") == [
            Token.digit_class(0),
            Token.character(" ", 2),
            Token.character("a", 3),
            Token.character("p", 4),
            Token.character("p", 5),
            Token.character("l", 6),
            Token.character("e", 7),
            Token.eof(8),
        ]
        assert basic_lexer(r"\d\d\d apples") == [
            Token.digit_class(0),
            Token.digit_class(2),
            Token.digit_class(4),
            Token.character(" ", 6),
            Token.character("a", 7),
            Token.character("p", 8),
            Token.character("p", 9),
            Token.character("l", 10),
            Token.character("e", 11),
            Token.character("s", 12),
            Token.eof(13),
        ]
        assert basic_lexer(r"\d \w\w\ws") == [
            Token.digit_class(0),
            Token.character(" ", 2),
            Token.word_class(3),
            Token.word_class(5),
            Token.word_class(7),
            Token.character("s", 9),
            Token.eof(10),
        ]

    def test_basic_lexer_start_string_anchor(self) -> None:
        assert basic_lexer("^log") == [
            Token.caret(0),
            Token.character("l", 1),
            Token.character("o", 2),
            Token.character("g", 3),
            Token.eof(4),
        ]
        assert basic_lexer(r"^\d\d\d") == [
            Token.caret(0),
            Token.digit_class(1),
            Token.digit_class(3),
            Token.digit_class(5),
            Token.eof(7),
        ]

    def test_basic_lexer_end_string_anchor(self) -> None:
        assert basic_lexer("dog$") == [
            Token.character("d", 0),
            Token.character("o", 1),
            Token.character("g", 2),
            Token.dollar(3),
            Token.eof(4),
        ]
        assert basic_lexer(r"\d\d\d$") == [
            Token.digit_class(0),
            Token.digit_class(2),
            Token.digit_class(4),
            Token.dollar(6),
            Token.eof(7),
        ]
        assert basic_lexer(r"\w\w\w$") == [
            Token.word_class(0),
            Token.word_class(2),
            Token.word_class(4),
            Token.dollar(6),
            Token.eof(7),
        ]

    # BRE: \+ is the one-or-more quantifier; bare + is a literal.
    def test_basic_lexer_one_or_more(self) -> None:
        assert basic_lexer(r"a\+") == [
            Token.character("a", 0),
            Token.plus(r"\+", 1),
            Token.eof(3),
        ]
        assert basic_lexer(r"ca\+ts") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.plus(r"\+", 2),
            Token.character("t", 4),
            Token.character("s", 5),
            Token.eof(6),
        ]
        assert basic_lexer(r"\d\+") == [
            Token.digit_class(0),
            Token.plus(r"\+", 2),
            Token.eof(4),
        ]

    # BRE: \? is the zero-or-one quantifier; bare ? is a literal.
    def test_basic_lexer_zero_or_one(self) -> None:
        assert basic_lexer(r"dogs\?") == [
            Token.character("d", 0),
            Token.character("o", 1),
            Token.character("g", 2),
            Token.character("s", 3),
            Token.question(r"\?", 4),
            Token.eof(6),
        ]
        assert basic_lexer(r"colou\?r") == [
            Token.character("c", 0),
            Token.character("o", 1),
            Token.character("l", 2),
            Token.character("o", 3),
            Token.character("u", 4),
            Token.question(r"\?", 5),
            Token.character("r", 7),
            Token.eof(8),
        ]
        assert basic_lexer(r"\d\?") == [
            Token.digit_class(0),
            Token.question(r"\?", 2),
            Token.eof(4),
        ]

    # BRE: * is the zero-or-more quantifier without escaping (same as ERE).
    def test_basic_lexer_zero_or_more(self) -> None:
        assert basic_lexer("ca*t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.asterisk(2),
            Token.character("t", 3),
            Token.eof(4),
        ]
        assert basic_lexer(r"k\d*t") == [
            Token.character("k", 0),
            Token.digit_class(1),
            Token.asterisk(3),
            Token.character("t", 4),
            Token.eof(5),
        ]
        assert basic_lexer("k[abc]*t") == [
            Token.character("k", 0),
            Token.left_bracket(1),
            Token.character("a", 2),
            Token.character("b", 3),
            Token.character("c", 4),
            Token.right_bracket(5),
            Token.asterisk(6),
            Token.character("t", 7),
            Token.eof(8),
        ]

    # BRE: \{n\} is exactly-n; bare { } are literals.
    def test_basic_lexer_exactly_n_times(self) -> None:
        assert basic_lexer(r"ca\{3\}t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.left_brace(r"\{", 2),
            Token.character("3", 4),
            Token.right_brace(r"\}", 5),
            Token.character("t", 7),
            Token.eof(8),
        ]
        assert basic_lexer(r"d\d\{2\}g") == [
            Token.character("d", 0),
            Token.digit_class(1),
            Token.left_brace(r"\{", 3),
            Token.character("2", 5),
            Token.right_brace(r"\}", 6),
            Token.character("g", 8),
            Token.eof(9),
        ]
        assert basic_lexer(r"c[xyz]\{4\}w") == [
            Token.character("c", 0),
            Token.left_bracket(1),
            Token.character("x", 2),
            Token.character("y", 3),
            Token.character("z", 4),
            Token.right_bracket(5),
            Token.left_brace(r"\{", 6),
            Token.character("4", 8),
            Token.right_brace(r"\}", 9),
            Token.character("w", 11),
            Token.eof(12),
        ]

    def test_basic_lexer_at_least_n_times(self) -> None:
        assert basic_lexer(r"ca\{2,\}t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.left_brace(r"\{", 2),
            Token.character("2", 4),
            Token.comma(5),
            Token.right_brace(r"\}", 6),
            Token.character("t", 8),
            Token.eof(9),
        ]
        assert basic_lexer(r"x\d\{3,\}y") == [
            Token.character("x", 0),
            Token.digit_class(1),
            Token.left_brace(r"\{", 3),
            Token.character("3", 5),
            Token.comma(6),
            Token.right_brace(r"\}", 7),
            Token.character("y", 9),
            Token.eof(10),
        ]
        assert basic_lexer(r"b[aeiou]\{2,\}r") == [
            Token.character("b", 0),
            Token.left_bracket(1),
            Token.character("a", 2),
            Token.character("e", 3),
            Token.character("i", 4),
            Token.character("o", 5),
            Token.character("u", 6),
            Token.right_bracket(7),
            Token.left_brace(r"\{", 8),
            Token.character("2", 10),
            Token.comma(11),
            Token.right_brace(r"\}", 12),
            Token.character("r", 14),
            Token.eof(15),
        ]

    def test_basic_lexer_between_n_and_m_times(self) -> None:
        assert basic_lexer(r"ca\{2,4\}t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.left_brace(r"\{", 2),
            Token.character("2", 4),
            Token.comma(5),
            Token.character("4", 6),
            Token.right_brace(r"\}", 7),
            Token.character("t", 9),
            Token.eof(10),
        ]
        assert basic_lexer(r"n\d\{1,3\}m") == [
            Token.character("n", 0),
            Token.digit_class(1),
            Token.left_brace(r"\{", 3),
            Token.character("1", 5),
            Token.comma(6),
            Token.character("3", 7),
            Token.right_brace(r"\}", 8),
            Token.character("m", 10),
            Token.eof(11),
        ]
        assert basic_lexer(r"p[xyz]\{2,3\}q") == [
            Token.character("p", 0),
            Token.left_bracket(1),
            Token.character("x", 2),
            Token.character("y", 3),
            Token.character("z", 4),
            Token.right_bracket(5),
            Token.left_brace(r"\{", 6),
            Token.character("2", 8),
            Token.comma(9),
            Token.character("3", 10),
            Token.right_brace(r"\}", 11),
            Token.character("q", 13),
            Token.eof(14),
        ]

    # . and * are metacharacters in BRE without escaping (same as ERE).
    def test_basic_lexer_wildcard(self) -> None:
        assert basic_lexer("d.g") == [
            Token.character("d", 0),
            Token.dot(1),
            Token.character("g", 2),
            Token.eof(3),
        ]
        assert basic_lexer("...") == [
            Token.dot(0),
            Token.dot(1),
            Token.dot(2),
            Token.eof(3),
        ]
        assert basic_lexer(r".\d.") == [
            Token.dot(0),
            Token.digit_class(1),
            Token.dot(3),
            Token.eof(4),
        ]

    # BRE: \( \) are group delimiters; \| is alternation.
    def test_basic_lexer_alteration(self) -> None:
        assert basic_lexer(r"\(cat\|dog\)") == [
            Token.left_parenthesis(r"\(", 0),
            Token.character("c", 2),
            Token.character("a", 3),
            Token.character("t", 4),
            Token.pipe(r"\|", 5),
            Token.character("d", 7),
            Token.character("o", 8),
            Token.character("g", 9),
            Token.right_parenthesis(r"\)", 10),
            Token.eof(12),
        ]
        assert basic_lexer(r"I like \(cats\|dogs\)") == [
            Token.character("I", 0),
            Token.character(" ", 1),
            Token.character("l", 2),
            Token.character("i", 3),
            Token.character("k", 4),
            Token.character("e", 5),
            Token.character(" ", 6),
            Token.left_parenthesis(r"\(", 7),
            Token.character("c", 9),
            Token.character("a", 10),
            Token.character("t", 11),
            Token.character("s", 12),
            Token.pipe(r"\|", 13),
            Token.character("d", 15),
            Token.character("o", 16),
            Token.character("g", 17),
            Token.character("s", 18),
            Token.right_parenthesis(r"\)", 19),
            Token.eof(21),
        ]
        assert basic_lexer(r"\(red\|green\|blue\)") == [
            Token.left_parenthesis(r"\(", 0),
            Token.character("r", 2),
            Token.character("e", 3),
            Token.character("d", 4),
            Token.pipe(r"\|", 5),
            Token.character("g", 7),
            Token.character("r", 8),
            Token.character("e", 9),
            Token.character("e", 10),
            Token.character("n", 11),
            Token.pipe(r"\|", 12),
            Token.character("b", 14),
            Token.character("l", 15),
            Token.character("u", 16),
            Token.character("e", 17),
            Token.right_parenthesis(r"\)", 18),
            Token.eof(20),
        ]

    # BRE supports backreferences via \( \) groups.
    def test_basic_lexer_single_backreference(self) -> None:
        assert basic_lexer(r"\(cat\) and \1") == [
            Token.left_parenthesis(r"\(", 0),
            Token.character("c", 2),
            Token.character("a", 3),
            Token.character("t", 4),
            Token.right_parenthesis(r"\)", 5),
            Token.character(" ", 7),
            Token.character("a", 8),
            Token.character("n", 9),
            Token.character("d", 10),
            Token.character(" ", 11),
            Token.back_reference(r"\1", 1, 12),
            Token.eof(14),
        ]
        assert basic_lexer(r"\(\w\+\) and \1") == [
            Token.left_parenthesis(r"\(", 0),
            Token.word_class(2),
            Token.plus(r"\+", 4),
            Token.right_parenthesis(r"\)", 6),
            Token.character(" ", 8),
            Token.character("a", 9),
            Token.character("n", 10),
            Token.character("d", 11),
            Token.character(" ", 12),
            Token.back_reference(r"\1", 1, 13),
            Token.eof(15),
        ]
        assert basic_lexer(r"\(\d\+\)-\1") == [
            Token.left_parenthesis(r"\(", 0),
            Token.digit_class(2),
            Token.plus(r"\+", 4),
            Token.right_parenthesis(r"\)", 6),
            Token.dash(8),
            Token.back_reference(r"\1", 1, 9),
            Token.eof(11),
        ]

    def test_basic_lexer_multiple_backreferences(self) -> None:
        assert basic_lexer(r"\(\d\+\) \(\w\+\) and \1 \2") == [
            Token.left_parenthesis(r"\(", 0),
            Token.digit_class(2),
            Token.plus(r"\+", 4),
            Token.right_parenthesis(r"\)", 6),
            Token.character(" ", 8),
            Token.left_parenthesis(r"\(", 9),
            Token.word_class(11),
            Token.plus(r"\+", 13),
            Token.right_parenthesis(r"\)", 15),
            Token.character(" ", 17),
            Token.character("a", 18),
            Token.character("n", 19),
            Token.character("d", 20),
            Token.character(" ", 21),
            Token.back_reference(r"\1", 1, 22),
            Token.character(" ", 24),
            Token.back_reference(r"\2", 2, 25),
            Token.eof(27),
        ]
        assert basic_lexer(r"\(cat\) and \(dog\) are \2 and \1") == [
            Token.left_parenthesis(r"\(", 0),
            Token.character("c", 2),
            Token.character("a", 3),
            Token.character("t", 4),
            Token.right_parenthesis(r"\)", 5),
            Token.character(" ", 7),
            Token.character("a", 8),
            Token.character("n", 9),
            Token.character("d", 10),
            Token.character(" ", 11),
            Token.left_parenthesis(r"\(", 12),
            Token.character("d", 14),
            Token.character("o", 15),
            Token.character("g", 16),
            Token.right_parenthesis(r"\)", 17),
            Token.character(" ", 19),
            Token.character("a", 20),
            Token.character("r", 21),
            Token.character("e", 22),
            Token.character(" ", 23),
            Token.back_reference(r"\2", 2, 24),
            Token.character(" ", 26),
            Token.character("a", 27),
            Token.character("n", 28),
            Token.character("d", 29),
            Token.character(" ", 30),
            Token.back_reference(r"\1", 1, 31),
            Token.eof(33),
        ]
        assert basic_lexer(r"\(\w\+\)-\(\w\+\)-\1-\2") == [
            Token.left_parenthesis(r"\(", 0),
            Token.word_class(2),
            Token.plus(r"\+", 4),
            Token.right_parenthesis(r"\)", 6),
            Token.dash(8),
            Token.left_parenthesis(r"\(", 9),
            Token.word_class(11),
            Token.plus(r"\+", 13),
            Token.right_parenthesis(r"\)", 15),
            Token.dash(17),
            Token.back_reference(r"\1", 1, 18),
            Token.dash(20),
            Token.back_reference(r"\2", 2, 21),
            Token.eof(23),
        ]

    def test_basic_lexer_nested_backreferences(self) -> None:
        assert basic_lexer(r"\('\(cat\) and \2'\) is the same as \1") == [
            Token.left_parenthesis(r"\(", 0),
            Token.character("'", 2),
            Token.left_parenthesis(r"\(", 3),
            Token.character("c", 5),
            Token.character("a", 6),
            Token.character("t", 7),
            Token.right_parenthesis(r"\)", 8),
            Token.character(" ", 10),
            Token.character("a", 11),
            Token.character("n", 12),
            Token.character("d", 13),
            Token.character(" ", 14),
            Token.back_reference(r"\2", 2, 15),
            Token.character("'", 17),
            Token.right_parenthesis(r"\)", 18),
            Token.character(" ", 20),
            Token.character("i", 21),
            Token.character("s", 22),
            Token.character(" ", 23),
            Token.character("t", 24),
            Token.character("h", 25),
            Token.character("e", 26),
            Token.character(" ", 27),
            Token.character("s", 28),
            Token.character("a", 29),
            Token.character("m", 30),
            Token.character("e", 31),
            Token.character(" ", 32),
            Token.character("a", 33),
            Token.character("s", 34),
            Token.character(" ", 35),
            Token.back_reference(r"\1", 1, 36),
            Token.eof(38),
        ]
        assert basic_lexer(r"\(\(dog\)-\2\)") == [
            Token.left_parenthesis(r"\(", 0),
            Token.left_parenthesis(r"\(", 2),
            Token.character("d", 4),
            Token.character("o", 5),
            Token.character("g", 6),
            Token.right_parenthesis(r"\)", 7),
            Token.dash(9),
            Token.back_reference(r"\2", 2, 10),
            Token.right_parenthesis(r"\)", 12),
            Token.eof(14),
        ]
        assert basic_lexer(r"\(\(\w\+\) \2\) and \1") == [
            Token.left_parenthesis(r"\(", 0),
            Token.left_parenthesis(r"\(", 2),
            Token.word_class(4),
            Token.plus(r"\+", 6),
            Token.right_parenthesis(r"\)", 8),
            Token.character(" ", 10),
            Token.back_reference(r"\2", 2, 11),
            Token.right_parenthesis(r"\)", 13),
            Token.character(" ", 15),
            Token.character("a", 16),
            Token.character("n", 17),
            Token.character("d", 18),
            Token.character(" ", 19),
            Token.back_reference(r"\1", 1, 20),
            Token.eof(22),
        ]


class TestExtendedLexer:
    def test_lexer_no_pattern(self) -> None:
        assert extended_lexer("") == [Token.eof(0)]

    def test_lexer_literal_characters(self) -> None:
        assert extended_lexer("abc") == [
            Token.character("a", 0),
            Token.character("b", 1),
            Token.character("c", 2),
            Token.eof(3),
        ]
        assert extended_lexer("123") == [
            Token.character("1", 0),
            Token.character("2", 1),
            Token.character("3", 2),
            Token.eof(3),
        ]

    def test_lexer_digit_character_class(self) -> None:
        assert extended_lexer(r"\d") == [Token.digit_class(0), Token.eof(2)]
        assert extended_lexer(r"\d\d\d") == [
            Token.digit_class(0),
            Token.digit_class(2),
            Token.digit_class(4),
            Token.eof(6),
        ]

    def test_lexer_word_character_class(self) -> None:
        assert extended_lexer(r"\w") == [Token.word_class(0), Token.eof(2)]
        assert extended_lexer(r"\w\w\w") == [
            Token.word_class(0),
            Token.word_class(2),
            Token.word_class(4),
            Token.eof(6),
        ]

    def test_lexer_positive_character_group(self) -> None:
        assert extended_lexer("[abc]") == [
            Token.left_bracket(0),
            Token.character("a", 1),
            Token.character("b", 2),
            Token.character("c", 3),
            Token.right_bracket(4),
            Token.eof(5),
        ]
        assert extended_lexer("[123]") == [
            Token.left_bracket(0),
            Token.character("1", 1),
            Token.character("2", 2),
            Token.character("3", 3),
            Token.right_bracket(4),
            Token.eof(5),
        ]

    def test_lexer_negative_character_group(self) -> None:
        assert extended_lexer("[^abc]") == [
            Token.left_bracket(0),
            Token.caret(1),
            Token.character("a", 2),
            Token.character("b", 3),
            Token.character("c", 4),
            Token.right_bracket(5),
            Token.eof(6),
        ]

    def test_lexer_combining_character_class(self) -> None:
        assert extended_lexer(r"\d apple") == [
            Token.digit_class(0),
            Token.character(" ", 2),
            Token.character("a", 3),
            Token.character("p", 4),
            Token.character("p", 5),
            Token.character("l", 6),
            Token.character("e", 7),
            Token.eof(8),
        ]
        assert extended_lexer(r"\d\d\d apples") == [
            Token.digit_class(0),
            Token.digit_class(2),
            Token.digit_class(4),
            Token.character(" ", 6),
            Token.character("a", 7),
            Token.character("p", 8),
            Token.character("p", 9),
            Token.character("l", 10),
            Token.character("e", 11),
            Token.character("s", 12),
            Token.eof(13),
        ]
        assert extended_lexer(r"\d \w\w\ws") == [
            Token.digit_class(0),
            Token.character(" ", 2),
            Token.word_class(3),
            Token.word_class(5),
            Token.word_class(7),
            Token.character("s", 9),
            Token.eof(10),
        ]

    def test_lexer_start_string_anchor(self) -> None:
        assert extended_lexer("^log") == [
            Token.caret(0),
            Token.character("l", 1),
            Token.character("o", 2),
            Token.character("g", 3),
            Token.eof(4),
        ]
        assert extended_lexer(r"^\d\d\d") == [
            Token.caret(0),
            Token.digit_class(1),
            Token.digit_class(3),
            Token.digit_class(5),
            Token.eof(7),
        ]

    def test_lexer_end_string_anchor(self) -> None:
        assert extended_lexer("dog$") == [
            Token.character("d", 0),
            Token.character("o", 1),
            Token.character("g", 2),
            Token.dollar(3),
            Token.eof(4),
        ]
        assert extended_lexer(r"\d\d\d$") == [
            Token.digit_class(0),
            Token.digit_class(2),
            Token.digit_class(4),
            Token.dollar(6),
            Token.eof(7),
        ]
        assert extended_lexer(r"\w\w\w$") == [
            Token.word_class(0),
            Token.word_class(2),
            Token.word_class(4),
            Token.dollar(6),
            Token.eof(7),
        ]

    def test_lexer_one_or_more(self) -> None:
        assert extended_lexer("a+") == [
            Token.character("a", 0),
            Token.plus("+", 1),
            Token.eof(2),
        ]
        assert extended_lexer("ca+ts") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.plus("+", 2),
            Token.character("t", 3),
            Token.character("s", 4),
            Token.eof(5),
        ]
        assert extended_lexer(r"\d+") == [
            Token.digit_class(0),
            Token.plus("+", 2),
            Token.eof(3),
        ]

    def test_lexer_zero_or_one(self) -> None:
        assert extended_lexer("dogs?") == [
            Token.character("d", 0),
            Token.character("o", 1),
            Token.character("g", 2),
            Token.character("s", 3),
            Token.question("?", 4),
            Token.eof(5),
        ]
        assert extended_lexer("colou?r") == [
            Token.character("c", 0),
            Token.character("o", 1),
            Token.character("l", 2),
            Token.character("o", 3),
            Token.character("u", 4),
            Token.question("?", 5),
            Token.character("r", 6),
            Token.eof(7),
        ]
        assert extended_lexer(r"\d?") == [
            Token.digit_class(0),
            Token.question("?", 2),
            Token.eof(3),
        ]

    def test_lexer_zero_or_more(self) -> None:
        assert extended_lexer("ca*t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.asterisk(2),
            Token.character("t", 3),
            Token.eof(4),
        ]
        assert extended_lexer(r"k\d*t") == [
            Token.character("k", 0),
            Token.digit_class(1),
            Token.asterisk(3),
            Token.character("t", 4),
            Token.eof(5),
        ]
        assert extended_lexer("k[abc]*t") == [
            Token.character("k", 0),
            Token.left_bracket(1),
            Token.character("a", 2),
            Token.character("b", 3),
            Token.character("c", 4),
            Token.right_bracket(5),
            Token.asterisk(6),
            Token.character("t", 7),
            Token.eof(8),
        ]

    def test_lexer_exactly_n_times(self) -> None:
        assert extended_lexer(r"ca{3}t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.left_brace("{", 2),
            Token.character("3", 3),
            Token.right_brace("}", 4),
            Token.character("t", 5),
            Token.eof(6),
        ]
        assert extended_lexer(r"d\d{2}g") == [
            Token.character("d", 0),
            Token.digit_class(1),
            Token.left_brace("{", 3),
            Token.character("2", 4),
            Token.right_brace("}", 5),
            Token.character("g", 6),
            Token.eof(7),
        ]
        assert extended_lexer(r"c[xyz]{4}w") == [
            Token.character("c", 0),
            Token.left_bracket(1),
            Token.character("x", 2),
            Token.character("y", 3),
            Token.character("z", 4),
            Token.right_bracket(5),
            Token.left_brace("{", 6),
            Token.character("4", 7),
            Token.right_brace("}", 8),
            Token.character("w", 9),
            Token.eof(10),
        ]

    def test_lexer_at_least_n_times(self) -> None:
        assert extended_lexer(r"ca{2,}t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.left_brace("{", 2),
            Token.character("2", 3),
            Token.comma(4),
            Token.right_brace("}", 5),
            Token.character("t", 6),
            Token.eof(7),
        ]
        assert extended_lexer(r"x\d{3,}y") == [
            Token.character("x", 0),
            Token.digit_class(1),
            Token.left_brace("{", 3),
            Token.character("3", 4),
            Token.comma(5),
            Token.right_brace("}", 6),
            Token.character("y", 7),
            Token.eof(8),
        ]
        assert extended_lexer(r"b[aeiou]{2,}r") == [
            Token.character("b", 0),
            Token.left_bracket(1),
            Token.character("a", 2),
            Token.character("e", 3),
            Token.character("i", 4),
            Token.character("o", 5),
            Token.character("u", 6),
            Token.right_bracket(7),
            Token.left_brace("{", 8),
            Token.character("2", 9),
            Token.comma(10),
            Token.right_brace("}", 11),
            Token.character("r", 12),
            Token.eof(13),
        ]

    def test_lexer_between_n_and_m_times(self) -> None:
        assert extended_lexer(r"ca{2,4}t") == [
            Token.character("c", 0),
            Token.character("a", 1),
            Token.left_brace("{", 2),
            Token.character("2", 3),
            Token.comma(4),
            Token.character("4", 5),
            Token.right_brace("}", 6),
            Token.character("t", 7),
            Token.eof(8),
        ]
        assert extended_lexer(r"n\d{1,3}m") == [
            Token.character("n", 0),
            Token.digit_class(1),
            Token.left_brace("{", 3),
            Token.character("1", 4),
            Token.comma(5),
            Token.character("3", 6),
            Token.right_brace("}", 7),
            Token.character("m", 8),
            Token.eof(9),
        ]
        assert extended_lexer(r"p[xyz]{2,3}q") == [
            Token.character("p", 0),
            Token.left_bracket(1),
            Token.character("x", 2),
            Token.character("y", 3),
            Token.character("z", 4),
            Token.right_bracket(5),
            Token.left_brace("{", 6),
            Token.character("2", 7),
            Token.comma(8),
            Token.character("3", 9),
            Token.right_brace("}", 10),
            Token.character("q", 11),
            Token.eof(12),
        ]

    def test_lexer_wildcard(self) -> None:
        assert extended_lexer("d.g") == [
            Token.character("d", 0),
            Token.dot(1),
            Token.character("g", 2),
            Token.eof(3),
        ]
        assert extended_lexer("...") == [
            Token.dot(0),
            Token.dot(1),
            Token.dot(2),
            Token.eof(3),
        ]
        assert extended_lexer(r".\d.") == [
            Token.dot(0),
            Token.digit_class(1),
            Token.dot(3),
            Token.eof(4),
        ]

    def test_lexer_alteration(self) -> None:
        assert extended_lexer("(cat|dog)") == [
            Token.left_parenthesis("(", 0),
            Token.character("c", 1),
            Token.character("a", 2),
            Token.character("t", 3),
            Token.pipe("|", 4),
            Token.character("d", 5),
            Token.character("o", 6),
            Token.character("g", 7),
            Token.right_parenthesis(")", 8),
            Token.eof(9),
        ]
        assert extended_lexer("I like (cats|dogs)") == [
            Token.character("I", 0),
            Token.character(" ", 1),
            Token.character("l", 2),
            Token.character("i", 3),
            Token.character("k", 4),
            Token.character("e", 5),
            Token.character(" ", 6),
            Token.left_parenthesis("(", 7),
            Token.character("c", 8),
            Token.character("a", 9),
            Token.character("t", 10),
            Token.character("s", 11),
            Token.pipe("|", 12),
            Token.character("d", 13),
            Token.character("o", 14),
            Token.character("g", 15),
            Token.character("s", 16),
            Token.right_parenthesis(")", 17),
            Token.eof(18),
        ]
        assert extended_lexer("(red|green|blue)") == [
            Token.left_parenthesis("(", 0),
            Token.character("r", 1),
            Token.character("e", 2),
            Token.character("d", 3),
            Token.pipe("|", 4),
            Token.character("g", 5),
            Token.character("r", 6),
            Token.character("e", 7),
            Token.character("e", 8),
            Token.character("n", 9),
            Token.pipe("|", 10),
            Token.character("b", 11),
            Token.character("l", 12),
            Token.character("u", 13),
            Token.character("e", 14),
            Token.right_parenthesis(")", 15),
            Token.eof(16),
        ]

    def test_lexer_single_backreference(self) -> None:
        assert extended_lexer(r"(cat) and \1") == [
            Token.left_parenthesis("(", 0),
            Token.character("c", 1),
            Token.character("a", 2),
            Token.character("t", 3),
            Token.right_parenthesis(")", 4),
            Token.character(" ", 5),
            Token.character("a", 6),
            Token.character("n", 7),
            Token.character("d", 8),
            Token.character(" ", 9),
            Token.back_reference(r"\1", 1, 10),
            Token.eof(12),
        ]
        assert extended_lexer(r"(\w+) and \1") == [
            Token.left_parenthesis("(", 0),
            Token.word_class(1),
            Token.plus("+", 3),
            Token.right_parenthesis(")", 4),
            Token.character(" ", 5),
            Token.character("a", 6),
            Token.character("n", 7),
            Token.character("d", 8),
            Token.character(" ", 9),
            Token.back_reference(r"\1", 1, 10),
            Token.eof(12),
        ]
        assert extended_lexer(r"(\d+)-\1") == [
            Token.left_parenthesis("(", 0),
            Token.digit_class(1),
            Token.plus("+", 3),
            Token.right_parenthesis(")", 4),
            Token.dash(5),
            Token.back_reference(r"\1", 1, 6),
            Token.eof(8),
        ]

    def test_lexer_multiple_backreferences(self) -> None:
        assert extended_lexer(r"(\d+) (\w+) and \1 \2") == [
            Token.left_parenthesis("(", 0),
            Token.digit_class(1),
            Token.plus("+", 3),
            Token.right_parenthesis(")", 4),
            Token.character(" ", 5),
            Token.left_parenthesis("(", 6),
            Token.word_class(7),
            Token.plus("+", 9),
            Token.right_parenthesis(")", 10),
            Token.character(" ", 11),
            Token.character("a", 12),
            Token.character("n", 13),
            Token.character("d", 14),
            Token.character(" ", 15),
            Token.back_reference(r"\1", 1, 16),
            Token.character(" ", 18),
            Token.back_reference(r"\2", 2, 19),
            Token.eof(21),
        ]
        assert extended_lexer(r"(cat) and (dog) are \2 and \1") == [
            Token.left_parenthesis("(", 0),
            Token.character("c", 1),
            Token.character("a", 2),
            Token.character("t", 3),
            Token.right_parenthesis(")", 4),
            Token.character(" ", 5),
            Token.character("a", 6),
            Token.character("n", 7),
            Token.character("d", 8),
            Token.character(" ", 9),
            Token.left_parenthesis("(", 10),
            Token.character("d", 11),
            Token.character("o", 12),
            Token.character("g", 13),
            Token.right_parenthesis(")", 14),
            Token.character(" ", 15),
            Token.character("a", 16),
            Token.character("r", 17),
            Token.character("e", 18),
            Token.character(" ", 19),
            Token.back_reference(r"\2", 2, 20),
            Token.character(" ", 22),
            Token.character("a", 23),
            Token.character("n", 24),
            Token.character("d", 25),
            Token.character(" ", 26),
            Token.back_reference(r"\1", 1, 27),
            Token.eof(29),
        ]
        assert extended_lexer(r"(\w+)-(\w+)-\1-\2") == [
            Token.left_parenthesis("(", 0),
            Token.word_class(1),
            Token.plus("+", 3),
            Token.right_parenthesis(")", 4),
            Token.dash(5),
            Token.left_parenthesis("(", 6),
            Token.word_class(7),
            Token.plus("+", 9),
            Token.right_parenthesis(")", 10),
            Token.dash(11),
            Token.back_reference(r"\1", 1, 12),
            Token.dash(14),
            Token.back_reference(r"\2", 2, 15),
            Token.eof(17),
        ]

    def test_lexer_nested_backreferences(self) -> None:
        assert extended_lexer(r"('(cat) and \2') is the same as \1") == [
            Token.left_parenthesis("(", 0),
            Token.character("'", 1),
            Token.left_parenthesis("(", 2),
            Token.character("c", 3),
            Token.character("a", 4),
            Token.character("t", 5),
            Token.right_parenthesis(")", 6),
            Token.character(" ", 7),
            Token.character("a", 8),
            Token.character("n", 9),
            Token.character("d", 10),
            Token.character(" ", 11),
            Token.back_reference(r"\2", 2, 12),
            Token.character("'", 14),
            Token.right_parenthesis(")", 15),
            Token.character(" ", 16),
            Token.character("i", 17),
            Token.character("s", 18),
            Token.character(" ", 19),
            Token.character("t", 20),
            Token.character("h", 21),
            Token.character("e", 22),
            Token.character(" ", 23),
            Token.character("s", 24),
            Token.character("a", 25),
            Token.character("m", 26),
            Token.character("e", 27),
            Token.character(" ", 28),
            Token.character("a", 29),
            Token.character("s", 30),
            Token.character(" ", 31),
            Token.back_reference(r"\1", 1, 32),
            Token.eof(34),
        ]
        assert extended_lexer(r"((dog)-\2)") == [
            Token.left_parenthesis("(", 0),
            Token.left_parenthesis("(", 1),
            Token.character("d", 2),
            Token.character("o", 3),
            Token.character("g", 4),
            Token.right_parenthesis(")", 5),
            Token.dash(6),
            Token.back_reference(r"\2", 2, 7),
            Token.right_parenthesis(")", 9),
            Token.eof(10),
        ]
        assert extended_lexer(r"((\w+) \2) and \1") == [
            Token.left_parenthesis("(", 0),
            Token.left_parenthesis("(", 1),
            Token.word_class(2),
            Token.plus("+", 4),
            Token.right_parenthesis(")", 5),
            Token.character(" ", 6),
            Token.back_reference(r"\2", 2, 7),
            Token.right_parenthesis(")", 9),
            Token.character(" ", 10),
            Token.character("a", 11),
            Token.character("n", 12),
            Token.character("d", 13),
            Token.character(" ", 14),
            Token.back_reference(r"\1", 1, 15),
            Token.eof(17),
        ]
