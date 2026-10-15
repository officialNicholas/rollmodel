"""v289: Ol' Bloop's first line in the lobby is shorter: "Hey, rookie! Ready to roll? Your first match is a little training session."
(no more "Tap Play and show me what you've got!"). He still points at Play."""
import re

def apply(s):
    pat = re.compile(r"(tutShow\('Hey, rookie! Ready to roll\? Your first match is a little training session\.) Tap Play and show me what you[^']{1,8}ve got!'")
    assert len(pat.findall(s)) == 1, len(pat.findall(s))
    return pat.sub(lambda m: m.group(1) + "'", s)
