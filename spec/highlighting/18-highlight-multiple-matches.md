# Highlight multiple matches

## Instructions

### Your Task

In this stage, you'll add support for highlighting multiple matches.

### Highlighting Multiple Matches

Grep highlights all matching text it finds in a line.

For example:

```bash
$ echo -n "dogs and cats are pets" | grep --color=always -E '(dogs|cats)'
dogs and cats are pets
```

Here, both `dogs` and `cats` are in bold red formatting.

For each match found in an input:

1. Insert the opening ANSI sequence `\033[01;31m` before the match
2. Insert the closing ANSI sequence `\033[m` after the match
3. Continue searching for the next match from where the previous match ended

### Tests

The tester will execute your program like this:

```bash
$ echo -n "jekyll and hyde" | ./your_program.sh --color=always -E '(jekyll|hyde)'
jekyll and hyde

$ echo -n "2025" | ./your_program.sh --color=always -E '\d'
2025
```

If the input does not match the pattern, your program must:

- Exit with the code `1`.
- Exit with no printed output.

If the input text matches the pattern, your program must:

- Exit with the code `0`.
- Print the input text to the standard output.
- Highlight all the matched texts in the input with bold red formatting.

### Notes

- You only need to handle the case of a single line. We'll get to highlighting matches in multiple lines in the later
  stages.
- The order of the SGR codes doesn't matter: `\033[31;01m` and `\033[01;31m` both produce the same bold red effect.