# v297: no squishing or stomping in the first match

In the lesson (the first match), rivals can no longer hurt you:

- A rival's **ground pound** landing on you, including when you're hiding in a paint basin, no longer knocks you out.
- A rival **landing on you** from a jump (stomp), **ramming** you, **rolling over** you or flattening you **as a giant** no longer
  squashes you flat.
- Instead you wobble, with a short moment of cover so it can't repeat on the next frame, and keep going.
- The **dodge step** still has the rival pound at you, so you learn the swipe-up dodge. A miss now counts as a miss
  ("Too late! Swipe up a beat sooner") instead of a knock-out, and the step still moves on after two tries or one good dodge.
- Nothing else changes. Missiles and falling off still count in the lesson, and from the second match on rivals pound and stomp as usual.

Checked in the lesson:

| | in the lesson | after it |
|---|---|---|
| Stomp | not flattened | flattened (1.5 s) |
| Ram | not flattened | flattened |
| Pound | still playing | knocked out |
| Roll-over / giant crush | still playing | knocked out |

In a run of the dodge step without dodging, the rival's pounds landed and were counted as misses, you were never knocked out, and
the lesson moved on to the next step.
