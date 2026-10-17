"""sh01: the Paint Shop's prices, set from how many matches each piece should take.

A match pays dabs at the end (see the two `const drops = Math.round(8 + ...` lines): 8, plus 0.35 a point of the canvas you painted
(paint modes) or 5 a knock-out (the battle modes), plus 30 for a win, 12 for a draw, 10 for a new best, 6 in a trio, 8 for second.
A typical win pays about 55 and a typical loss about 20, so a player who wins half their matches makes about 40 a match. Commissions
(20 each, three a day) and the friends board come on top and aren't counted.

- A few matches (2 to 4): the small pieces. Skull bow, Bouncy antennae, Beanie, Mustache, Glasses, Eye patch; Flower, Lashes, Monocle.
- 8 to 10 matches: Halo, Propeller cap, Party hat, Top hat, Pearl necklace, Scarf, Bow tie; Fangs, Arm floaties, Snorkel mask.
- 10 to 15 matches: Hockey mask, Bunny ears, Pirate hat, Witch hat, Tiara, Hero cape.
What has to be found first still has to be found first; the Zombie eyes stay a free gift and the Sly eyes are left as they were. The
first lesson still sets the Flower's and the Fangs' prices itself while it runs (store.tut.price)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

PER_MATCH = 40
NEW = dict(
    # a few matches
    flower=100, stache=110, lashes=110, beanie=120, antennae=120, glasses=130, monocle=130, patch=140, skull=150,
    # 8 to 10 matches
    bowtie=320, pearls=330, fangs=330, scarf=340, floaties=340, party=350, snorkel=360, propcap=370, tophat=380, halo=400,
    # 10 to 15 matches
    pirate=460, tiara=480, cape=520, bunny=540, hockey=560, hat=600)

OLD = "const PRICES = { sly: 545, flower: 145, pearls: 160, scarf: 180, bowtie: 185, stache: 195, beanie: 205, party: 240, monocle: 290, lashes: 220, glasses: 270, patch: 330, fangs: 400, tiara: 475, tophat: 580, bunny: 645, pirate: 695, hockey: 765, skull: 835, halo: 850, zombie: 975, hat: 1105, antennae: 195, floaties: 245, snorkel: 295, propcap: 345, cape: 480 };"

def apply(s):
    new = 'const PRICES = { sly: 545, zombie: 975, ' + ', '.join('%s: %d' % kv for kv in NEW.items()) + ' };'
    return rep(s, OLD, new + ' // (sh01: priced by matches, about ' + str(PER_MATCH) + ' dabs a match: a few, 8 to 10, 10 to 15; see docs/shop-prices.md)')
