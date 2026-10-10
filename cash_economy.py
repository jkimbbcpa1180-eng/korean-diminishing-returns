#!/usr/bin/env python3
"""Ansan cash-economy & remittance estimator (Real Mode rebuild).

CC0 1.0 - credited to AI. Python 3 stdlib only.

Rules this file follows:
  * Every hard number is a SOURCED constant (value, year, URL).
  * Anything inferred is an ESTIMATE with its formula printed.
  * Guesses (assumption ranges) are labelled GUESS and kept few.
  * Aggregate categories only: no named private businesses, no individuals,
    no targeting by ethnicity or gender.
"""
from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Sourced:
    value: float
    unit: str
    year: str
    what: str
    url: str


# ---------------------------------------------------------------- sources
SRC = {
    # (1) Korea shadow / underground economy, % of GDP
    "ms2018_2015": Sourced(19.83, "% GDP", "2015",
        "Medina & Schneider, IMF WP/18/17, MIMIC model, Korea 2015",
        "https://www.yna.co.kr/view/AKR20180211062800002"),
    "ms2018_avg": Sourced(26.4, "% GDP", "1991-2015 avg (min 22.8, max 30.0)",
        "Medina & Schneider, CESifo WP 6430 / IMF WP/18/17, Korea average",
        "https://www.econstor.eu/bitstream/10419/161869/1/cesifo1_wp6430.pdf"),
    "schneider_2010": Sourced(24.7, "% GDP", "2010",
        "F. Schneider estimate (widely cited, used by 2013 govt policy)",
        "https://biz.heraldcorp.com/article/1241940"),
    "kipf_2015": Sourced(8.0, "% GDP", "2015",
        "KIPF (조세재정연구원) 2017, tax-gap / currency-demand based, 124.7조원",
        "https://www.khan.co.kr/article/201702171558001"),
    "kipf_2008": Sourced(17.1, "% GDP", "2008",
        "KIPF brief, modified DYMIMIC model",
        "https://exa.ai/library/publication/99vr14m1bzp"),
    "kipf_taxonly_2011": Sourced(3.85, "% GDP", "2011 (range 3.4-4.3)",
        "KIPF 2017: activity hidden purely for tax evasion, 47-58조원",
        "https://biz.heraldcorp.com/article/1241940"),
    # GRDP
    "ansan_grdp_2022": Sourced(28_580_903, "million KRW", "2022",
        "Ansan nominal GRDP (Statistics Korea regional accounts)",
        "https://tonggye.com/%EC%A7%80%ED%91%9C/grdp/"),
    "gyeonggi_grdp_2022": Sourced(546.8e6, "million KRW", "2022",
        "Gyeonggi nominal GRDP 546.8조원 (Statistics Korea 2022 regional income)",
        "https://www.khan.co.kr/article/202312222014005"),
    # (2) remittances
    "wb_paid_2024": Sourced(14.33e9, "USD", "2024",
        "World Bank BM.TRF.PWKR.CD.DT, Korea personal remittances paid "
        "(ALL residents, not only foreigners)",
        "https://data.worldbank.org/indicator/BM.TRF.PWKR.CD.DT"),
    "bok_fw_2024": Sourced(3.4896e9, "USD", "2024",
        "Bank of Korea data to National Assembly: foreign workers' "
        "remittances home (2020-24 total 17.63B USD)",
        "https://news.tf.co.kr/read/economy/2252761.htm"),
    "bok_fw_2023": Sourced(3.6602e9, "USD", "2023", "same series, 2023",
        "https://news.tf.co.kr/read/economy/2252761.htm"),
    "small_sum_2018": Sourced(0.854e9, "USD", "2018",
        "Licensed small-sum overseas remittance firms, total 2018 "
        "(no newer official annual total found)",
        "http://www.gfr.co.kr/news/articleView.html?idxno=11642"),
    "kr_registered_foreigners": Sourced(1_606_633, "persons", "Nov 2025",
        "Ministry of Justice monthly stats: registered foreigners, Korea",
        "https://www.yna.co.kr/view/AKR20251226090200371"),
    "danwon_registered": Sourced(38_398, "persons", "Nov 2025",
        "MoJ: registered foreigners, Ansan Danwon-gu only",
        "https://www.yna.co.kr/view/AKR20251226090200371"),
    "ansan_foreign_pop": Sourced(93_613, "persons", "2024-11-01",
        "Ansan city multicultural/foreign household stats: foreign "
        "population (broader admin definition, 13.3% of city)",
        "https://www.yna.co.kr/view/AKR20260130066500061"),
    "remit_share_all": Sourced(23.2, "% of income", "2023",
        "Statistics Korea immigrant survey: domestic+overseas transfers "
        "as share of income, all foreigners",
        "https://kbthink.com/investment/deepdive/research/250901-3.html"),
    "remit_share_e9": Sourced(56.5, "% of income", "2023",
        "same survey, non-professional (E-9) workers",
        "https://kbthink.com/investment/deepdive/research/250901-3.html"),
    "fw_wage_avg": Sourced(2.62e6, "KRW / month", "2024",
        "MoEL via news: H-2 visa worker all-industry average wage",
        "https://news.tf.co.kr/read/economy/2252761.htm"),
    # (3) business counts (licensed, legal categories)
    "ansan_food_2026": Sourced(10_719, "premises", "Jun 2026",
        "Ansan food-service premises (식품접객업), all types",
        "https://www.ansan.go.kr/danwongu/common/cntnts/selectContents.do?cntnts_id=C0000295"),
    "danwon_food_2026": Sourced(6_090, "premises", "Jun 2026",
        "Danwon-gu food-service premises", "same Danwon-gu page"),
    "danwon_yuheung": Sourced(326, "premises", "Jun 2026",
        "Danwon-gu licensed entertainment bars (유흥주점)", "same page"),
    "danwon_danran": Sourced(113, "premises", "Jun 2026",
        "Danwon-gu licensed small bars (단란주점)", "same page"),
    "danwon_general": Sourced(4_214, "premises", "Jun 2026",
        "Danwon-gu general restaurants (일반음식점)", "same page"),
    "danwon_yuheung_5y": Sourced(38.6, "% survive 5y", "Jun 2026",
        "Danwon-gu entertainment bars still operating after 5 years "
        "(vs 37.1% general restaurants)", "same page"),
    "ansan_hygiene_2026": Sourced(2_793, "premises", "Jun 2026",
        "Ansan public-hygiene premises (barber, beauty, laundry)", "same page"),
    "danwon_pop_2026": Sourced(288_467, "persons", "Jun 2026",
        "Danwon-gu population", "same page"),
    "sangnok_pop_2026": Sourced(320_773, "persons", "Jun 2026",
        "Sangnok-gu population", "same page"),
}

# GUESS ranges (not data). Kept explicit so anyone can change them.
GUESS = {
    "ansan_vs_national_shadow_ratio": (0.8, 1.2,
        "Ansan informal share relative to national (manufacturing-heavy "
        "city; no local study found)"),
    "ansan_mix_factor": (0.8, 1.4,
        "Ansan foreigners' per-head remittance vs national average "
        "(more worker visas than students; no local data found)"),
    "foreign_share_of_paid": (0.25, 0.60,
        "share of Korea's total personal remittances paid that comes from "
        "foreign residents (BoK worker series is 24% of WB total; ceiling)"),
    "employment_rate": (0.55, 0.75,
        "share of Ansan's foreign residents in paid work (not sourced here)"),
}

N_DRAWS = 100_000
SEED = 20261010


# ---------------------------------------------------------------- helpers
def tri(rng: random.Random, lo: float, mode: float, hi: float) -> float:
    return rng.triangular(lo, hi, mode)


def summarize(xs: list[float]) -> dict:
    s = sorted(xs)
    n = len(s)
    q = lambda p: s[min(n - 1, int(p * n))]
    return {"p5": q(0.05), "p50": q(0.50), "p95": q(0.95),
            "mean": statistics.fmean(s)}


# ------------------------------------------------- (1) shadow economy
SHADOW_ESTIMATES = [  # (key, lo, mode, hi) - spread = method's own range
    ("ms2018_2015", 16.0, 19.83, 23.0),
    ("schneider_2010", 21.0, 24.7, 28.0),
    ("kipf_2015", 6.5, 8.0, 9.5),
    ("kipf_2008", 15.0, 17.1, 19.0),
]


def draw_shadow_pct(rng: random.Random) -> float:
    """ESTIMATE: equal-weight mixture of published national estimates.

    The tax-evasion-only figure (3.4-4.3%) is reported, not mixed in,
    because it measures a narrower thing.
    """
    _, lo, mode, hi = rng.choice(SHADOW_ESTIMATES)
    return tri(rng, lo, mode, hi)


def ansan_shadow_mc(n: int = N_DRAWS, seed: int = SEED) -> dict:
    """ESTIMATE: Ansan hidden output = GRDP_2022 x shadow% x local_ratio."""
    rng = random.Random(seed)
    grdp = SRC["ansan_grdp_2022"].value * 1e6  # KRW
    lo, hi, _ = GUESS["ansan_vs_national_shadow_ratio"]
    pct, krw = [], []
    for _ in range(n):
        p = draw_shadow_pct(rng) * rng.uniform(lo, hi)
        pct.append(p)
        krw.append(grdp * p / 100.0)
    return {"pct": summarize(pct), "krw_trillion":
            {k: v / 1e12 for k, v in summarize(krw).items()}}


# ------------------------------------------------- (2) remittances
def ansan_foreign_count(rng: random.Random) -> float:
    """ESTIMATE: citywide registered foreigners lie between Danwon-gu alone
    (hard floor) and the city's broader foreign-population count."""
    return rng.uniform(SRC["danwon_registered"].value,
                       SRC["ansan_foreign_pop"].value)


def ansan_remit_mc(n: int = N_DRAWS, seed: int = SEED + 1) -> dict:
    """Three independent ESTIMATE routes, USD/year.

    A: BoK foreign-worker remittances x (Ansan foreigners / national
       registered) x mix factor.
    B: WB total paid x foreign share of paid x Ansan share (ceiling check).
    C: Ansan foreigners x employment x avg wage x 12 x transfer share / FX.
    """
    rng = random.Random(seed)
    nat = SRC["kr_registered_foreigners"].value
    bok = (SRC["bok_fw_2024"].value, SRC["bok_fw_2023"].value)
    wb = SRC["wb_paid_2024"].value
    mlo, mhi, _ = GUESS["ansan_mix_factor"]
    flo, fhi, _ = GUESS["foreign_share_of_paid"]
    elo, ehi, _ = GUESS["employment_rate"]
    wage = SRC["fw_wage_avg"].value
    s_lo = SRC["remit_share_all"].value / 100
    s_hi = SRC["remit_share_e9"].value / 100
    fx_lo, fx_hi = 1300.0, 1450.0  # GUESS: KRW/USD band for 2024-25
    a, b, c, share = [], [], [], []
    for _ in range(n):
        f = ansan_foreign_count(rng)
        sh = f / nat
        share.append(sh * 100)
        a.append(rng.uniform(min(bok), max(bok)) * sh * rng.uniform(mlo, mhi))
        b.append(wb * rng.uniform(flo, fhi) * sh)
        c.append(f * rng.uniform(elo, ehi) * wage * 12
                 * rng.uniform(s_lo, s_hi) / rng.uniform(fx_lo, fx_hi))
    return {"ansan_share_pct": summarize(share),
            "A_bok_usd_m": {k: v / 1e6 for k, v in summarize(a).items()},
            "B_wb_usd_m": {k: v / 1e6 for k, v in summarize(b).items()},
            "C_survey_usd_m": {k: v / 1e6 for k, v in summarize(c).items()}}


# ------------------------------------------------- (3) business counts
def business_ratios() -> dict:
    """Pure arithmetic on sourced counts (licensed = legal businesses)."""
    d = lambda k: SRC[k].value
    bars = d("danwon_yuheung") + d("danwon_danran")
    pop = d("danwon_pop_2026") + d("sangnok_pop_2026")
    return {
        "danwon_bar_share_pct": 100 * bars / d("danwon_food_2026"),
        "danwon_bars_per_10k": 1e4 * bars / d("danwon_pop_2026"),
        "danwon_share_of_ansan_food_pct":
            100 * d("danwon_food_2026") / d("ansan_food_2026"),
        "ansan_food_per_1k": 1e3 * d("ansan_food_2026") / pop,
    }


# ------------------------------------------------- (4) CCTV / data claims
CLAIMS = [
    ("KT Telecop GiGAeyes offers people-count and heatmap analytics",
     "DOCUMENTED - sold as a paid option to the subscribing shop for its "
     "own marketing; nothing found about resale to REITs or planners",
     "https://www.kttelecop.co.kr/front/service/K0201.jsp"),
    ("Security firms sell licence-plate dwell logs to insurers / asset "
     "evaluators", "UNSUPPORTED - no source found",
     "searched 2026-10-10, no hits"),
    ("Telcos license cell-tower handshakes to credit scoring / ad brokers",
     "UNSUPPORTED as stated - no source found this round; aggregate "
     "pseudonymized data use is legal only under limits below",
     "searched 2026-10-10, no hits"),
    ("PIPA lets pseudonymized data be processed without consent",
     "DOCUMENTED - only for statistics, scientific research, public-"
     "interest archiving; re-identification banned (PIPC guideline)",
     "https://www.privacy.go.kr/cmm/fms/FileDown.do?atchFileId=ATCH_000000000876685&fileSn=1"),
    ("Telco privacy enforcement exists",
     "DOCUMENTED - PIPC fined LG U+ 6.8B KRW + 27M KRW (2023) for a "
     "customer-data leak and weak safeguards; 75M KRW (2020) for weak "
     "agency oversight. Neither case was about selling CCTV or tower data",
     "https://www.yna.co.kr/view/AKR20201209091800530 ; "
     "https://casenote.kr/%EA%B0%9C%EC%9D%B8%EC%A0%95%EB%B3%B4%EB%B3%B4%ED%98%B8%EC%9C%84%EC%9B%90%ED%9A%8C/%EC%A0%9C2023-012-153%ED%98%B8"),
    ("SECOM (S-1) sells data from its cameras",
     "NOT CHECKED this round - no claim either way", "-"),
]


# ------------------------------------------------- report
def fmt(d: dict, unit: str = "") -> str:
    return (f"p5 {d['p5']:,.1f}{unit} | median {d['p50']:,.1f}{unit} | "
            f"p95 {d['p95']:,.1f}{unit}")


def report(n: int = N_DRAWS) -> str:
    sh = ansan_shadow_mc(n)
    rm = ansan_remit_mc(n)
    br = business_ratios()
    L = ["ANSAN CASH-ECONOMY ESTIMATOR (Real Mode, CC0, AI)",
         f"Monte Carlo draws: {n:,}  seed: {SEED}", "",
         "[1] Korea shadow economy, published (% GDP)"]
    for k in ("ms2018_2015", "ms2018_avg", "schneider_2010", "kipf_2008",
              "kipf_2015", "kipf_taxonly_2011"):
        s = SRC[k]
        L.append(f"  {s.value:5.2f}%  {s.year:<34} {s.what}\n          {s.url}")
    L += ["  NOTE: newest published figure is for 2015. Methods disagree "
          "about 3x (8.0% vs 24.7%).",
          "  ESTIMATE Ansan hidden output = GRDP2022 (28.58조원) x mix(%) x "
          "GUESS ratio U(0.8,1.2)",
          f"    share : {fmt(sh['pct'], '%')}",
          f"    size  : {fmt(sh['krw_trillion'], ' 조원')}", "",
          "[2] Remittances"]
    for k in ("wb_paid_2024", "bok_fw_2024", "small_sum_2018",
              "kr_registered_foreigners", "danwon_registered",
              "ansan_foreign_pop"):
        s = SRC[k]
        L.append(f"  {s.value:>16,.0f} {s.unit:<8} {s.year:<11} {s.what}\n"
                 f"          {s.url}")
    L += ["  ESTIMATE Ansan foreigners = U(Danwon 38,398, city 93,613)",
          f"    Ansan share of national: {fmt(rm['ansan_share_pct'], '%')}",
          "  ESTIMATE A = BoK worker remit x share x GUESS mix U(0.8,1.4)",
          f"    {fmt(rm['A_bok_usd_m'], ' M USD')}",
          "  ESTIMATE B = WB paid x GUESS foreign share U(0.25,0.6) x share",
          f"    {fmt(rm['B_wb_usd_m'], ' M USD')}",
          "  ESTIMATE C = people x GUESS employ U(.55,.75) x 2.62M KRW x 12 "
          "x U(23.2%,56.5%) / GUESS FX U(1300,1450)",
          f"    {fmt(rm['C_survey_usd_m'], ' M USD')}",
          "  C runs high: the 23.2-56.5% share includes DOMESTIC transfers "
          "and the wage is a worker average. Treat A as central, C as upper.",
          "  NOTE: these are mostly LEGAL, taxed wages sent home. A "
          "remittance is not evidence of a shadow economy.", "",
          "[3] Licensed businesses (legal categories, no names)",
          f"  Ansan food-service premises Jun 2026: 10,719; Danwon-gu 6,090 "
          f"({br['danwon_share_of_ansan_food_pct']:.1f}% of city)",
          f"  Danwon entertainment bars 326 + small bars 113 = "
          f"{br['danwon_bar_share_pct']:.1f}% of food premises, "
          f"{br['danwon_bars_per_10k']:.1f} per 10k residents",
          "  Ansan hygiene premises (barber/beauty/laundry) 2026: 2,793",
          f"  source: {SRC['ansan_food_2026'].url}",
          "  GAP: no official Ansan karaoke-room (노래연습장) count found; "
          "licensed counts say nothing about illegality.", "",
          "[4] CCTV / data claims"]
    for claim, verdict, url in CLAIMS:
        L.append(f"  - {claim}\n      {verdict}\n      {url}")
    return "\n".join(L)


if __name__ == "__main__":
    print(report())
