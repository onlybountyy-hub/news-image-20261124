# THE WORLD TODAY — Tuesday 24 November 2026

[![Rank](https://make.fun/badge/news-image-20261124/onlybountyy-hub/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/onlybountyy-hub/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image, one day: the world news of Tuesday 24 November 2026 as a
newspaper front page. Hero story — Ukraine sank the Russian corvette
*Merkury* off Benghazi, Libya — plus five more stories from the day:
tankers burning in the Strait of Hormuz, Nvidia's 31% surge, a deadly
factory fire in Banten, Indonesia, airstrikes in Gaza, and a 5.6-magnitude
earthquake in Nepal.

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

This writes `entry.png` (1024×1024) into the output directory.

## How it works

Pure Python standard library — no Pillow, no third-party packages, no
network access, no external assets. `main.py` draws the whole poster
(masthead, night-sea hero scene, five pictogram panels, footer) with its
own 5×7 bitmap font and writes the PNG by hand (zlib-compressed scanlines).
Output is fully deterministic: two runs produce byte-identical files.
