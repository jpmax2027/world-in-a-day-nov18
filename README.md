# world-in-a-day-nov18

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/jpmax2027/world-in-a-day-nov18/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/jpmax2027/world-in-a-day-nov18/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A newspaper front page that sums up one day of world news — Wednesday 18 November 2026 — in a single 1024×1024 image: U.S. jets striking an Iranian missile site on Qeshm Island and Iran firing back at Kuwait and Bahrain as the lead, Xi and Putin meeting in Shenzhen ahead of a first-ever three-way summit with Trump, Ukraine hitting the Kerch Bridge for a second day, Mary Peltola flipping Alaska's Senate seat, the U.S. losing its measles-elimination status, Voyager 1 reaching one light-day from Earth, and a ticker of the day's smaller stories.

The image is drawn entirely from code by `main.py`, a dependency-free Python program with its own tiny rasterizer, an embedded bitmap font, and a built-in PNG encoder — no image assets, no network, and every run produces byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `entry.png` (1024×1024, about 26 KiB) to the directory named by the `MAKEFUN_OUTPUT_DIR` environment variable, or to `/output` when that is not set.

---

<sub>Entered on [make.fun](https://make.fun/?ref=zbqpv30a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
