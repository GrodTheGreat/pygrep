import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: pygrep [OPTION]... PATTERNS [FILE]...")
        print("Try 'pygrep --help' for more information.")
        sys.exit(1)
    sys.exit(1)


if __name__ == "__main__":
    main()
