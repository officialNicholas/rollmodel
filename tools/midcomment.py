# find '//' line comments that are followed on the same physical line by more code in the built game (the comment swallows it)
import re, sys
src = open(sys.argv[1]).read(); s = src.index('<script>', src.index('three.r186.min.js')); e = src.index('</script>', s); code = src[s:e]
bad = 0
for n, line in enumerate(code.split('\n')):
    # strip strings/regex crudely, then look for // ... followed by code markers typical of a swallowed statement
    m = re.search(r'(?<![:\'"\\/])//\s*\([^)]*\)\s*(\S.*)$', line)
    if m and re.search(r'[;{}]|\b(const|let|if|return|for|function)\b', m.group(1)):
        bad += 1; print('line', n, '...', line[max(0, m.start() - 60): m.start() + 140])
print('suspects', bad)
