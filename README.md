# Bring the humans 03 — make.fun TikTok ad

A 20-second vertical video ad for [make.fun](https://make.fun), made for the
["Bring the humans 03"](https://make.fun/bounty/bring-the-humans-03) bounty
($500, top 20 paid by TikTok views).

## The ad

Spoken in Bahasa Indonesia, for an Indonesian audience. Four beats, one idea
each:

1. **Hook** — "AI lu nganggur?" (Is your AI idle?) over the make.fun ghost
   at a laptop, brand badge on screen from the first frame.
2. **What it is** — AI agents compete building software on make.fun, and the
   prizes are real money.
3. **The money** — $500 split across 20 winners; free to enter, your agent
   does the work.
4. **Call to action** — enter your AI agent in a bounty on make.fun, then the
   referral end card with code `j62x7qjj`.

The ad was built with ffmpeg from make.fun's own press pack: the brand badge,
the ghost illustrations, the lockup, and the official 9:16 referral card.
No stock footage, no generated video — just the press assets, brand colours,
and big readable text.

## What's in this repo

- `main.ts` — the entry program. It validates `VIDEO.json` and copies it
  into the output folder. Run it with `node main.ts` (Node 22).
- `VIDEO.json` — the full TikTok address of the posted ad.

## The video

The ad lives on TikTok at the address in `VIDEO.json`, posted publicly from
[@tauruuussssssssss](https://www.tiktok.com/@tauruuussssssssss).
