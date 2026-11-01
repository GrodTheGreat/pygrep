import sys

from pygrep.environment import Environment
from pygrep.grep import Grep


def main():
    env = Environment(
        sys.argv[1:], sys.stdin, sys.stdout, sys.stderr, sys.stdout.isatty()
    )
    sys.exit(Grep(env).run())


if __name__ == "__main__":
    main()
