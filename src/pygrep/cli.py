import argparse

# TODO: These probably need refinement...
parser = argparse.ArgumentParser(
    prog="pygrep - print lines that match patterns",
    usage="grep [OPTION]... PATTERNS [FILE]...\n"
    "grep [OPTION]... -e PATTERNS ... [FILE]...\n"
    "grep [OPTION]... -f PATTERN_FILE ... [FILE]...",
    description="pygrep searches for patterns in each FILE. In the synopsis's first form, which is used if no -e or -f options are present, the first operand PATTERNS is one or more patterns separated by newline characters, and grep prints each line that matches a pattern. Typically PATTERNS should be quoted when grep is used in a shell command. A FILE of “-” stands for standard input.  If no FILE is given, recursive searches examine the working directory, and non-recursive searches read standard input.",
)
parser.add_argument(
    "-G",
    "--basic-regexp",
    action="store_true",
    help="PATTERNS are basic regular expressions",
    # description="Interpret PATTERNS as basic regular expressions. This is the default.",
)
parser.add_argument(
    "-E",
    "--extended-regexp",
    action="store_true",
    help="PATTERNS are extended regular expressions",
    # description="Interpret PATTERNS as extended regular expressions.",
)
parser.add_argument(
    "-o",
    "--only-matching",
    action="store_true",
    help="show only nonempty parts of lines that match",
    # description="Print only the matched (non-empty) parts of a matching line, with each such part on a separate output line.",
)
parser.add_argument(
    "--color",
    "--colour",
    choices=["never", "always", "auto"],
    help="use markers to highlight the matching strings; WHEN is 'always', 'never', or 'auto'",
    # description="Surround the matched (non-empty) strings, matching lines, context lines, file names, line numbers, byte offsets, and separators (for fields and groups of context lines) with escape sequences to display them in color on the terminal. The colors are defined by the environment variable GREP_COLORS.  WHEN is never, always, or auto.",
)
parser.add_argument(
    "-r",
    "--recursive",
    action="store_true",
    help="like --directories=recurse",
    # description="Read all files under each directory, recursively, following symbolic links only if they are on the command line.  Note that if no file operand is given, grep searches the working directory.  This is equivalent to the -d recurse option.",
)
parser.add_argument("patterns")
parser.add_argument("files", nargs="*", metavar="file")
args = parser.parse_args()
