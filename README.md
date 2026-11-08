# Day 13 of 100 · Diwali website tour

Screen-recorded walkthrough of the "Forever With You – New Year 2027" surprise website
(https://newyear-2027-hackncode.sites.tab.bot/) for the @hack.n.code 100 Days Daily Reel Challenge.

- `record_tour.py` - Playwright script. Opens the site in a 390x694 mobile viewport, taps every
  button (opening, name, countdown, fireworks, couple scene, love letter, promise, gift, finale)
  and captures frames at 30 fps using Chrome virtual time, so the real animations play at real speed.
  Usage: `python3 record_tour.py <out_dir> <url> 2.7692 694`
- `diya_heart.html` - bonus: 44 diyas lighting one by one into a heart, pure SVG + SMIL (one small loop places them).

Frames are then stitched with ffmpeg and overlaid with the hook, DAY 13/100 badge and CTA.

Happy Diwali 🪔
