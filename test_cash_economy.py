"""Tests for cash_economy.py (CC0, AI). Run: python3 -m unittest"""
import unittest
import cash_economy as ce


class T(unittest.TestCase):
    def test_every_source_has_url_and_year(self):
        for k, s in ce.SRC.items():
            self.assertTrue(s.year, k)
            self.assertTrue(s.url.startswith("http") or s.url.startswith("same"), k)

    def test_shadow_mc_bounds(self):
        r = ce.ansan_shadow_mc(20_000)
        self.assertGreater(r["pct"]["p5"], 6.5 * 0.8 - 1e-9)
        self.assertLess(r["pct"]["p95"], 28.0 * 1.2 + 1e-9)
        # 28.58 trillion KRW x <=33.6% caps hidden output under ~9.6
        self.assertLess(r["krw_trillion"]["p95"], 28.58 * 0.336 + 0.01)

    def test_remit_share_bounds(self):
        r = ce.ansan_remit_mc(20_000)
        lo = 38_398 / 1_606_633 * 100
        hi = 93_613 / 1_606_633 * 100
        self.assertGreaterEqual(r["ansan_share_pct"]["p5"], lo - 1e-9)
        self.assertLessEqual(r["ansan_share_pct"]["p95"], hi + 1e-9)

    def test_remit_routes_same_order_of_magnitude(self):
        r = ce.ansan_remit_mc(20_000)
        meds = [r[k]["p50"] for k in ("A_bok_usd_m", "B_wb_usd_m", "C_survey_usd_m")]
        self.assertLess(max(meds) / min(meds), 10)

    def test_deterministic(self):
        self.assertEqual(ce.ansan_remit_mc(5_000), ce.ansan_remit_mc(5_000))

    def test_business_ratio(self):
        b = ce.business_ratios()
        self.assertAlmostEqual(b["danwon_bar_share_pct"], 439 / 6090 * 100)

    def test_no_named_businesses_or_targeting(self):
        txt = ce.report(2_000).lower()
        for bad in ("benz", "blue bird", "plus barber", "daylong", "wang-cha",
                    "seohyeon", "hostess", "masseuse", "women"):
            self.assertNotIn(bad, txt)

    def test_unsupported_claims_flagged(self):
        verdicts = [v for _, v, _ in ce.CLAIMS]
        self.assertEqual(sum(v.startswith("UNSUPPORTED") for v in verdicts), 2)


if __name__ == "__main__":
    unittest.main()
