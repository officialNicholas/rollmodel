"""v451: the Learn the basics card in fewer words.

- The user: "Learn the basics? A quick training match or jump right in?" The title stays; the line under it is now just "A quick
  training match or jump right in?" (it listed every move before)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "'A quick training match: steer, jump, slingshot, pound and dodge. Or skip it and jump straight in.'", "'A quick training match or jump right in?'")
    return s
