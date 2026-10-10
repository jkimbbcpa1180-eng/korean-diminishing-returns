# Ansan cash-economy estimator (Real Mode rebuild)

CC0 1.0, credited to AI. Python 3 stdlib only.

This replaces a pasted "field investigation report" that named five real
Ansan businesses as fronts based on how they looked, used a hand-typed
30/25/40/5 money split, and claimed without sources that security and
telecom firms sell plate logs and tower data. This version uses public
data only. Every number carries a source and year. Inferred values are
marked ESTIMATE, with their formula. Assumptions are marked GUESS. No
business, person, ethnicity or gender is singled out.

## Run
    python3 cash_economy.py          # report, 100,000 Monte Carlo draws
    python3 -m unittest -q           # 8 tests

## What it estimates
1. Korea's shadow economy as a share of GDP. The published range is
   8.0% (KIPF, 2015) to 24.7% (Schneider, 2010). The model mixes those
   estimates and scales them to Ansan's 2022 GRDP (28.58조원).
2. Ansan's outbound remittances, by three routes: Bank of Korea
   foreign-worker data, the World Bank figure for remittances paid, and
   survey income shares.
3. Licensed business counts (legal categories only) from Ansan city
   pages.
4. The CCTV and data claims, each marked DOCUMENTED, UNSUPPORTED or NOT
   CHECKED.

## Data gaps (stated, not filled)
- No published Korea shadow-economy estimate newer than 2015 was found.
- No Ansan-specific informal-economy study was found, so the local
  ratio is a GUESS.
- A citywide Ansan *registered* foreigner count could not be fetched,
  because the city's xlsx was unreachable from this box. The model uses
  a range: Danwon-gu's MoJ count (38,398) as the floor and the city's
  broader foreign-population figure (93,613) as the ceiling.
- The newest official total for licensed small-sum remittance firms is
  from 2018 ($854M).
- No official Ansan count of karaoke rooms (노래연습장) was found.
  Bar counts cover Danwon-gu only.
- No national VAT-gap figure was found.
- SECOM and telecom data-sale practices were not checked in depth.

## Read this before quoting numbers
- A remittance is mostly legal, taxed wages sent home. It is not
  evidence of a shadow economy.
- A licensed bar count says nothing about illegality.
- Shadow-economy models disagree by about 3x. The median is less
  meaningful than the range.
