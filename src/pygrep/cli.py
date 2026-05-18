import argparse

parser = argparse.ArgumentParser(
    prog="grep",
    usage="grep [OPTION]... PATTERNS [FILE]...\n"
    "grep [OPTION]... -e PATTERNS ... [FILE]...\n"
    "grep [OPTION]... -f PATTERN_FILE ... [FILE]...",
    description="grep searches for patterns in each FILE.  In the synopsis's first form, which is used if no -e or -f options are present, the first operand PATTERNS is one or more patterns separated by newline characters, and grep prints each line that matches a pattern. Typically PATTERNS should be quoted when grep is used in a shell command.\n\nA FILE of “-” stands for standard input.  If no FILE is given,recursive searches examine the working directory, and nonrecursive searches read standard input.",
)
parser.add_argument(
    "-E",
    "--extended-regexp",
    help="Interpret PATTERNS as extended regular expressions",
)
args = parser.parse_args()
