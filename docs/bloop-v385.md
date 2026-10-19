# v385: Ol' Bloop's new look, in three moods

The user's new Ol' Bloop art replaces the old picture everywhere he turns up: the corner of the screen in a match, the lesson's plates,
and over the lesson's cards. Backgrounds were cut away with Ludo.ai and each set in the game's 640x596 coach frame
(`tools/v385_bloop_art.py`): `game/art/coach.webp` (normal), `coach_serious.webp`, `coach_laugh.webp`.

| Mood | Picture | When |
| --- | --- | --- |
| Normal | talking, finger up | how to do a thing ("Tap Strokes to open it", "Slingshotting is the fastest way around") |
| Serious | arms crossed | warnings ("Out of paint!", "The sun's coming out!", "Rivals pound too", "Don't forget to slingshot", "Now win it!") |
| Laughing | eyes shut, hands out | wins and gifts ("Learned!", "It's ready!", "You found a flower", "You earned dabs", "Hey, rookie!", "Looking good!", "Safe in a tub!") and the news cards (new modes, commissions, more to learn) |

His line picks the mood (`coachMoodOf` in `tools/v385_bloop.py`). All three are loaded and given his soft shadow when the game starts,
so changing mood never shows an empty frame.
